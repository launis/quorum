import asyncio
import logging
import uuid
from collections.abc import Awaitable, Callable

from tenacity import retry, stop_after_attempt, wait_exponential

from backend_v2.exceptions import AppException
from backend_v2.llm.caching_service import LLMCachingService
from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.blackboard import (
    DraftAtomList,
    DraftExtractedAtom,
    LLMDraftAtomList,
)
from backend_v2.models.dtos.dag_models import ExtractedAtom, GlobalOntologyMap
from backend_v2.models.prompt import CompiledPrompt
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.prompts.atom_extraction import (
    PHASE_0_SYSTEM_PROMPT,
    PHASE_1_SYSTEM_PROMPT,
)
from backend_v2.settings import get_settings
from backend_v2.utils.alias_engine import AliasEngine

logger = logging.getLogger(__name__)


class TwoPassAtomizer:
    """Orchestrates the Phase 0 Map-Reduce and Phase 1 Local Chunk Extraction."""

    def __init__(self, executor: LLMTaskExecutor) -> None:
        """Initialize the TwoPassAtomizer.

        Args:
            executor: Centralized LLM task orchestrator for executing prompts.
        """
        self.executor = executor

    def _calculate_packets(self, hydrated_text: str, packet_size: int = 50) -> list[tuple[str, str, list[str]]]:
        """Deterministically calculate logical chunk boundaries."""
        block_keys = []
        for line in hydrated_text.split("\n\n"):
            if line.startswith("[") and "] " in line:
                block_keys.append(line[1 : line.find("]")])

        packets: list[tuple[str, str, list[str]]] = []
        if not block_keys:
            packets.append(("[NO_BLOCK]", "[NO_BLOCK]", []))
        else:
            for i in range(0, len(block_keys), packet_size):
                packet_keys = block_keys[i : i + packet_size]
                packets.append((packet_keys[0], packet_keys[-1], packet_keys))
        return packets

    async def execute_phase_0(
        self,
        client: LLMClient,
        hydrated_text: str,
        progress_callback: Callable[[int, int], Awaitable[None]] | None = None,
        semaphore: asyncio.Semaphore | None = None,
    ) -> GlobalOntologyMap:
        """Extracts and merges GlobalOntologyMap from all chunks.

        Args:
            client: The LLM client to use.
            hydrated_text: Globally hydrated text with block IDs.

        Returns:
            A merged GlobalOntologyMap containing entities and macro-rules.
        """
        all_entities = {}
        all_rules = set()

        packets = self._calculate_packets(hydrated_text)

        compiled_prompt = CompiledPrompt(
            static_messages=[
                {"role": "system", "content": PHASE_0_SYSTEM_PROMPT},
                {"role": "user", "content": f"<source_data>\n{hydrated_text}\n</source_data>"},
            ],
            dynamic_messages=[],
        )

        await LLMCachingService.pre_cache_document(
            provider_name=client.provider_name, compiled_prompt=compiled_prompt, model_name=client.model_name
        )

        try:
            sem = semaphore or asyncio.Semaphore(get_settings().max_concurrent_llm_steps)
            async with asyncio.TaskGroup() as tg:
                tasks = []
                completed = 0

                async def track_task(start_b: str, end_b: str) -> GlobalOntologyMap:
                    nonlocal completed
                    res = await self._extract_ontology_from_chunk(client, compiled_prompt, start_b, end_b, sem)
                    completed += 1
                    if progress_callback:
                        await progress_callback(completed, len(packets))
                    return res

                for start_b, end_b, _ in packets:
                    tasks.append(tg.create_task(track_task(start_b, end_b)))

            for task in tasks:
                result = task.result()
                for entity in result.entities:
                    all_entities[entity.name] = entity
                for rule in result.macro_rules:
                    all_rules.add(rule)

        finally:
            await LLMCachingService.teardown_workflow_caches(client.provider_name, "tda_phase_0")

        return GlobalOntologyMap(entities=list(all_entities.values()), macro_rules=list(all_rules))

    async def _extract_ontology_from_chunk(
        self, client: LLMClient, compiled_prompt: CompiledPrompt, start_b: str, end_b: str, sem: asyncio.Semaphore
    ) -> GlobalOntologyMap:
        async with sem:
            dynamic_instruction = (
                f"<execution_parameters>\nExtract atoms ONLY from [{start_b}] to [{end_b}].\n</execution_parameters>"
            )
            chunk_prompt = CompiledPrompt(
                static_messages=compiled_prompt.static_messages,
                dynamic_messages=[{"role": "user", "content": dynamic_instruction}],
            )
            result, _ = await self.executor.execute_structured_task(
                client=client,
                messages=chunk_prompt,
                response_model=GlobalOntologyMap,
            )
            return result

    async def execute_phase_1(
        self,
        client: LLMClient,
        hydrated_text: str,
        ontology: GlobalOntologyMap,
        progress_callback: Callable[[int, int], Awaitable[None]] | None = None,
        semaphore: asyncio.Semaphore | None = None,
    ) -> list[ExtractedAtom]:
        """Extracts atomic claims from chunks utilizing the global ontology.

        Args:
            client: The LLM client.
            hydrated_text: Globally hydrated text with block IDs.
            ontology: The ontology map generated in Phase 0.

        Returns:
            A list of ExtractedAtom objects with fully hydrated Opaque Stripe IDs.
        """
        ontology_json = ontology.model_dump_json()
        system_prompt = PHASE_1_SYSTEM_PROMPT.replace("{ontology_map_json}", ontology_json)

        packets = self._calculate_packets(hydrated_text)

        compiled_prompt = CompiledPrompt(
            static_messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"<source_data>\n{hydrated_text}\n</source_data>"},
            ],
            dynamic_messages=[],
        )

        await LLMCachingService.pre_cache_document(
            provider_name=client.provider_name, compiled_prompt=compiled_prompt, model_name=client.model_name
        )

        all_atoms = []
        try:
            sem = semaphore or asyncio.Semaphore(get_settings().max_concurrent_llm_steps)
            async with asyncio.TaskGroup() as tg:
                tasks = []
                completed = 0

                async def track_task(start_b: str, end_b: str, packet_keys: list[str], idx: int) -> list[ExtractedAtom]:
                    nonlocal completed
                    res = await self._extract_atoms_from_chunk(
                        client, compiled_prompt, start_b, end_b, packet_keys, idx, hydrated_text, sem
                    )
                    completed += 1
                    if progress_callback:
                        await progress_callback(completed, len(packets))
                    return res

                for idx, (start_b, end_b, packet_keys) in enumerate(packets):
                    tasks.append(tg.create_task(track_task(start_b, end_b, packet_keys, idx)))

            for task in tasks:
                all_atoms.extend(task.result())

        finally:
            await LLMCachingService.teardown_workflow_caches(client.provider_name, "tda_phase_1")

        return all_atoms

    async def _extract_atoms_from_chunk(
        self,
        client: LLMClient,
        compiled_prompt: CompiledPrompt,
        start_b: str,
        end_b: str,
        packet_keys: list[str],
        chunk_index: int,
        hydrated_text: str,
        sem: asyncio.Semaphore,
    ) -> list[ExtractedAtom]:
        async with sem:
            dynamic_instruction = (
                f"<execution_parameters>\nExtract atoms ONLY from [{start_b}] to [{end_b}].\n</execution_parameters>"
            )
            chunk_prompt = CompiledPrompt(
                static_messages=compiled_prompt.static_messages,
                dynamic_messages=[{"role": "user", "content": dynamic_instruction}],
            )

            draft_result, _ = await self.executor.execute_structured_task(
                client=client,
                messages=chunk_prompt,
                response_model=LLMDraftAtomList,
            )

            local_alias_map = {}
            for line in hydrated_text.split("\n\n"):
                if line.startswith("[") and "] " in line:
                    b_id = line[1 : line.find("]")]
                    text = line[line.find("]") + 2 :]
                    local_alias_map[b_id] = text
            alias_engine = AliasEngine(alias_map=local_alias_map)

            final_atoms = []
            for draft in draft_result.atoms:
                tda_id = f"tda_{uuid.uuid4().hex[:8]}"
                exact_quote = None

                if not draft.is_logical_deduction and draft.source_block_id:
                    clean_id = draft.source_block_id.replace("[", "").replace("]", "").strip()
                    if clean_id not in packet_keys:
                        raise ValueError(
                            f"Block ID {clean_id} is outside the assigned packet [{start_b}] to [{end_b}]!"
                        )

                    try:
                        resolved = alias_engine.resolve_alias(clean_id)
                        if resolved != clean_id:
                            exact_quote = resolved
                    except AppException as exc:
                        logger.warning(
                            "AliasEngine hallucination detected for %s: %s",
                            tda_id,
                            exc.message,
                        )

                    if not exact_quote:
                        logger.warning(
                            "Anchor Hydration failed for %s. LLM hallucinated block ID: %s",
                            tda_id,
                            draft.source_block_id,
                        )

                final_atoms.append(
                    ExtractedAtom(
                        reasoning=draft.reasoning,
                        resolved_claim=draft.resolved_claim,
                        source_quote=exact_quote,
                        tda_id=tda_id,
                        source_id=f"chunk_{chunk_index}",
                        source_sequence_index=chunk_index,
                    )
                )
            return final_atoms

    async def execute_phase_1_drafts(
        self,
        client: LLMClient,
        hydrated_text: str,
        ontology: GlobalOntologyMap,
        progress_callback: Callable[[int, int], Awaitable[None]] | None = None,
        semaphore: asyncio.Semaphore | None = None,
    ) -> DraftAtomList:
        """Extracts atomic claims from chunks returning raw drafts and handling DLQ routing.

        Args:
            client: The LLM client.
            hydrated_text: Globally hydrated text with block IDs.
            ontology: The ontology map generated in Phase 0.

        Returns:
            A DraftAtomList containing DraftExtractedAtom instances and potential dlq_status.
        """
        ontology_json = ontology.model_dump_json()
        system_prompt = PHASE_1_SYSTEM_PROMPT.replace("{ontology_map_json}", ontology_json)

        packets = self._calculate_packets(hydrated_text)

        compiled_prompt = CompiledPrompt(
            static_messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"<source_data>\n{hydrated_text}\n</source_data>"},
            ],
            dynamic_messages=[],
        )

        await LLMCachingService.pre_cache_document(
            provider_name=client.provider_name, compiled_prompt=compiled_prompt, model_name=client.model_name
        )

        all_atoms = []
        has_dlq = False
        try:
            sem = semaphore or asyncio.Semaphore(get_settings().max_concurrent_llm_steps)
            async with asyncio.TaskGroup() as tg:
                tasks = []
                completed = 0

                async def track_task(start_b: str, end_b: str, packet_keys: list[str], idx: int) -> DraftAtomList:
                    nonlocal completed
                    res = await self._extract_drafts_from_chunk(
                        client, compiled_prompt, start_b, end_b, packet_keys, idx, hydrated_text, sem
                    )
                    completed += 1
                    if progress_callback:
                        await progress_callback(completed, len(packets))
                    return res

                for idx, (start_b, end_b, packet_keys) in enumerate(packets):
                    tasks.append(tg.create_task(track_task(start_b, end_b, packet_keys, idx)))

            for task in tasks:
                result = task.result()
                if result.dlq_status:
                    has_dlq = True
                    logger.warning("dlq_chunk_detected", extra={"dlq_status": result.dlq_status})
                all_atoms.extend(result.atoms)

        finally:
            await LLMCachingService.teardown_workflow_caches(client.provider_name, "tda_phase_1_drafts")

        return DraftAtomList(atoms=all_atoms, dlq_status="FAILED/DLQ" if has_dlq else None)

    @retry(
        stop=stop_after_attempt(get_settings().llm_max_retries),
        wait=wait_exponential(
            multiplier=get_settings().llm_retry_multiplier,
            min=get_settings().llm_retry_min_seconds,
            max=get_settings().llm_retry_max_seconds,
        ),
    )
    async def _extract_drafts_from_chunk_with_retry(
        self,
        client: LLMClient,
        compiled_prompt: CompiledPrompt,
        start_b: str,
        end_b: str,
        packet_keys: list[str],
        chunk_index: int,
        hydrated_text: str,
        sem: asyncio.Semaphore,
    ) -> DraftAtomList:
        async with sem:
            dynamic_instruction = (
                f"<execution_parameters>\nExtract atoms ONLY from [{start_b}] to [{end_b}].\n</execution_parameters>"
            )
            chunk_prompt = CompiledPrompt(
                static_messages=compiled_prompt.static_messages,
                dynamic_messages=[{"role": "user", "content": dynamic_instruction}],
            )

            draft_result, _ = await self.executor.execute_structured_task(
                client=client,
                messages=chunk_prompt,
                response_model=LLMDraftAtomList,
            )

            local_alias_map = {}
            for line in hydrated_text.split("\n\n"):
                if line.startswith("[") and "] " in line:
                    b_id = line[1 : line.find("]")]
                    text = line[line.find("]") + 2 :]
                    local_alias_map[b_id] = text
            alias_engine = AliasEngine(alias_map=local_alias_map)

            final_drafts = []
            for draft in draft_result.atoms:
                if draft.is_logical_deduction:
                    final_drafts.append(
                        DraftExtractedAtom(
                            reasoning=draft.reasoning,
                            resolved_claim=draft.resolved_claim,
                            is_logical_deduction=True,
                            source_quote=None,
                            draft_id=draft.draft_id,
                            source_sequence_index=chunk_index,
                        )
                    )
                    continue

                if not draft.source_block_id:
                    logger.warning("corrupted_atom_dropped", extra={"reason": "missing_block_id_on_non_deduction"})
                    continue

                clean_id = draft.source_block_id.replace("[", "").replace("]", "").strip()
                if clean_id not in packet_keys:
                    raise ValueError(f"Block ID {clean_id} is outside the assigned packet [{start_b}] to [{end_b}]!")

                exact_quote = None
                try:
                    resolved = alias_engine.resolve_alias(clean_id)
                    if resolved != clean_id:
                        exact_quote = resolved
                except AppException as exc:
                    logger.warning(
                        "AliasEngine hallucination detected for %s: %s",
                        clean_id,
                        exc.message,
                    )

                if not exact_quote:
                    logger.warning("corrupted_atom_dropped", extra={"reason": "hallucinated_block_id_not_found"})
                    continue

                final_drafts.append(
                    DraftExtractedAtom(
                        reasoning=draft.reasoning,
                        resolved_claim=draft.resolved_claim,
                        is_logical_deduction=False,
                        source_quote=exact_quote,
                        draft_id=draft.draft_id,
                        source_sequence_index=chunk_index,
                    )
                )

            return DraftAtomList(atoms=final_drafts)

    async def _extract_drafts_from_chunk(
        self,
        client: LLMClient,
        compiled_prompt: CompiledPrompt,
        start_b: str,
        end_b: str,
        packet_keys: list[str],
        chunk_index: int,
        hydrated_text: str,
        sem: asyncio.Semaphore,
    ) -> DraftAtomList:
        try:
            return await self._extract_drafts_from_chunk_with_retry(
                client, compiled_prompt, start_b, end_b, packet_keys, chunk_index, hydrated_text, sem
            )
        except Exception as e:
            logger.error(f"DLQ Worker Failed: {e}", exc_info=True)
            return DraftAtomList(atoms=[], dlq_status="FAILED/DLQ")

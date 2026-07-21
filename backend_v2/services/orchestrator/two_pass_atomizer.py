import asyncio
import logging
import uuid
from collections.abc import Awaitable, Callable

from tenacity import retry, stop_after_attempt, wait_exponential

from backend_v2.exceptions import AppException
from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.blackboard import (
    DraftAtomList,
    DraftExtractedAtom,
    LLMDraftAtomList,
)
from backend_v2.models.dtos.dag_models import ExtractedAtom, GlobalOntologyMap
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.prompts.atom_extraction import (
    PHASE_0_SYSTEM_PROMPT,
    PHASE_1_SYSTEM_PROMPT,
)
from backend_v2.settings import get_settings
from backend_v2.utils.alias_engine import AliasEngine

logger = logging.getLogger(__name__)


# @deprecated — Import from backend_v2.models.domain.blackboard instead.


class TwoPassAtomizer:
    """Orchestrates the Phase 0 Map-Reduce and Phase 1 Local Chunk Extraction."""

    def __init__(self, executor: LLMTaskExecutor) -> None:
        """Initialize the TwoPassAtomizer.

        Args:
            executor: Centralized LLM task orchestrator for executing prompts.
        """
        self.executor = executor

    async def execute_phase_0(
        self,
        client: LLMClient,
        chunks: list[str],
        progress_callback: Callable[[int, int], Awaitable[None]] | None = None,
    ) -> GlobalOntologyMap:
        """Extracts and merges GlobalOntologyMap from all chunks.

        Args:
            client: The LLM client to use.
            chunks: A list of text chunks representing the document.

        Returns:
            A merged GlobalOntologyMap containing entities and macro-rules.
        """
        all_entities = {}
        all_rules = set()
        sem = asyncio.Semaphore(get_settings().max_concurrent_llm_steps)

        async with asyncio.TaskGroup() as tg:
            tasks = []
            completed = 0

            async def track_task(chunk: str) -> GlobalOntologyMap:
                nonlocal completed
                res = await self._extract_ontology_from_chunk(client, chunk, sem)
                completed += 1
                if progress_callback:
                    await progress_callback(completed, len(chunks))
                return res

            for chunk in chunks:
                tasks.append(tg.create_task(track_task(chunk)))

        for task in tasks:
            result = task.result()
            for entity in result.entities:
                all_entities[entity.name] = entity
            for rule in result.macro_rules:
                all_rules.add(rule)

        return GlobalOntologyMap(entities=list(all_entities.values()), macro_rules=list(all_rules))

    async def _extract_ontology_from_chunk(
        self, client: LLMClient, chunk: str, sem: asyncio.Semaphore
    ) -> GlobalOntologyMap:
        async with sem:
            messages = [
                {"role": "system", "content": PHASE_0_SYSTEM_PROMPT},
                {"role": "user", "content": f"<source_data>\n{chunk}\n</source_data>"},
            ]
            result, _ = await self.executor.execute_structured_task(
                client=client,
                messages=messages,
                response_model=GlobalOntologyMap,
            )
            return result

    async def execute_phase_1(
        self,
        client: LLMClient,
        chunks: list[str],
        ontology: GlobalOntologyMap,
        progress_callback: Callable[[int, int], Awaitable[None]] | None = None,
    ) -> list[ExtractedAtom]:
        """Extracts atomic claims from chunks utilizing the global ontology.

        Args:
            client: The LLM client.
            chunks: Document chunks.
            ontology: The ontology map generated in Phase 0.

        Returns:
            A list of ExtractedAtom objects with fully hydrated Opaque Stripe IDs.
        """
        ontology_json = ontology.model_dump_json()
        sem = asyncio.Semaphore(get_settings().max_concurrent_llm_steps)

        all_atoms = []
        async with asyncio.TaskGroup() as tg:
            tasks = []
            completed = 0

            async def track_task(chunk: str, idx: int) -> list[ExtractedAtom]:
                nonlocal completed
                res = await self._extract_atoms_from_chunk(client, chunk, idx, ontology_json, sem)
                completed += 1
                if progress_callback:
                    await progress_callback(completed, len(chunks))
                return res

            for idx, chunk in enumerate(chunks):
                tasks.append(tg.create_task(track_task(chunk, idx)))

        for task in tasks:
            all_atoms.extend(task.result())

        return all_atoms

    async def _extract_atoms_from_chunk(
        self, client: LLMClient, chunk: str, chunk_index: int, ontology_json: str, sem: asyncio.Semaphore
    ) -> list[ExtractedAtom]:
        async with sem:
            # 1. Anchor Hydration: Break chunk into numbered blocks using AliasEngine
            paragraphs = [p.strip() for p in chunk.split("\n\n") if p.strip()]
            alias_engine = AliasEngine()
            numbered_lines = []
            for p in paragraphs:
                block_id = alias_engine.register(p, prefix="B")
                numbered_lines.append(f"[{block_id}] {p}")

            numbered_chunk = "\n\n".join(numbered_lines)

            system_prompt = PHASE_1_SYSTEM_PROMPT.replace("{ontology_map_json}", ontology_json)
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"<source_data>\n{numbered_chunk}\n</source_data>"},
            ]

            draft_result, _ = await self.executor.execute_structured_task(
                client=client,
                messages=messages,
                response_model=LLMDraftAtomList,
            )

            final_atoms = []
            for draft in draft_result.atoms:
                # Generate a compliant Opaque Stripe ID for the extracted atom.
                # AliasEngine integration in 2.2 will refine this mapping.
                tda_id = f"tda_{uuid.uuid4().hex[:8]}"

                # 2. Anchor Hydration: Map block ID back to exact quote
                exact_quote = None
                if not draft.is_logical_deduction and draft.source_block_id:
                    clean_id = draft.source_block_id.replace("[", "").replace("]", "").strip()
                    try:
                        resolved = alias_engine.resolve_alias(clean_id)
                        if resolved != clean_id:
                            exact_quote = resolved
                    except AppException as exc:
                        # Raised if alias hallucinated with known prefix
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
                        source_sequence_index=0,
                    )
                )
            return final_atoms

    async def execute_phase_1_drafts(
        self,
        client: LLMClient,
        chunks: list[str],
        ontology: GlobalOntologyMap,
        progress_callback: Callable[[int, int], Awaitable[None]] | None = None,
    ) -> DraftAtomList:
        """Extracts atomic claims from chunks returning raw drafts and handling DLQ routing.

        Args:
            client: The LLM client.
            chunks: Document chunks.
            ontology: The ontology map generated in Phase 0.

        Returns:
            A DraftAtomList containing DraftExtractedAtom instances and potential dlq_status.
        """
        ontology_json = ontology.model_dump_json()
        sem = asyncio.Semaphore(get_settings().max_concurrent_llm_steps)

        all_atoms = []
        has_dlq = False
        async with asyncio.TaskGroup() as tg:
            tasks = []
            completed = 0

            async def track_task(chunk: str, idx: int) -> DraftAtomList:
                nonlocal completed
                res = await self._extract_drafts_from_chunk(client, chunk, idx, ontology_json, sem)
                completed += 1
                if progress_callback:
                    await progress_callback(completed, len(chunks))
                return res

            for idx, chunk in enumerate(chunks):
                tasks.append(tg.create_task(track_task(chunk, idx)))

        for task in tasks:
            result = task.result()
            if result.dlq_status:
                has_dlq = True
                logger.warning("dlq_chunk_detected", extra={"dlq_status": result.dlq_status})
            all_atoms.extend(result.atoms)

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
        self, client: LLMClient, chunk: str, chunk_index: int, ontology_json: str, sem: asyncio.Semaphore
    ) -> DraftAtomList:
        async with sem:
            # 1. Anchor Hydration: Break chunk into numbered blocks using AliasEngine
            paragraphs = [p.strip() for p in chunk.split("\n\n") if p.strip()]
            alias_engine = AliasEngine()
            numbered_lines = []
            for p in paragraphs:
                block_id = alias_engine.register(p, prefix="B")
                numbered_lines.append(f"[{block_id}] {p}")

            numbered_chunk = "\n\n".join(numbered_lines)

            system_prompt = PHASE_1_SYSTEM_PROMPT.replace("{ontology_map_json}", ontology_json)
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"<source_data>\n{numbered_chunk}\n</source_data>"},
            ]

            draft_result, _ = await self.executor.execute_structured_task(
                client=client,
                messages=messages,
                response_model=LLMDraftAtomList,
            )

            final_drafts = []
            for draft in draft_result.atoms:
                if draft.is_logical_deduction:
                    # Force null hypothesis for logical deductions
                    final_drafts.append(
                        DraftExtractedAtom(
                            reasoning=draft.reasoning,
                            resolved_claim=draft.resolved_claim,
                            is_logical_deduction=True,
                            source_quote=None,
                            draft_id=draft.draft_id,
                            source_sequence_index=0,
                        )
                    )
                    continue

                if not draft.source_block_id:
                    # Should have a block ID if not a logical deduction
                    logger.warning("corrupted_atom_dropped", extra={"reason": "missing_block_id_on_non_deduction"})
                    continue

                clean_id = draft.source_block_id.replace("[", "").replace("]", "").strip()
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
                        source_sequence_index=0,
                    )
                )

            return DraftAtomList(atoms=final_drafts)

    async def _extract_drafts_from_chunk(
        self, client: LLMClient, chunk: str, chunk_index: int, ontology_json: str, sem: asyncio.Semaphore
    ) -> DraftAtomList:
        try:
            return await self._extract_drafts_from_chunk_with_retry(client, chunk, chunk_index, ontology_json, sem)
        except Exception as e:
            logger.error(f"DLQ Worker Failed: {e}", exc_info=True)
            return DraftAtomList(atoms=[], dlq_status="FAILED/DLQ")

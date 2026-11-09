"""Two-pass atomization service for extracting global ontologies and fine-grained claims."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable

from pydantic import ValidationError
from tenacity import RetryError, retry, stop_after_attempt, wait_exponential

from backend_v2.core.template_processor import TemplateProcessor
from backend_v2.exceptions import AppException
from backend_v2.llm.caching_service import LLMCachingService
from backend_v2.llm.client import LLMClient
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.domain.blackboard import (
    DraftAtomList,
    DraftExtractedAtom,
    LLMDraftAtomList,
)
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.dag_models import ChunkPacketDTO, ExtractedAtom, GlobalOntologyMap, OntologyEntity
from backend_v2.models.enums import EntityPrefix
from backend_v2.models.llm import LLMMessageDTO
from backend_v2.models.prompt import CompiledPrompt
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.prompts.atom_extraction import (
    PHASE_0_SYSTEM_PROMPT,
    build_phase_1_system_prompt,
)
from backend_v2.settings import get_settings

__all__ = ["TwoPassAtomizer"]

logger = logging.getLogger(__name__)


class TwoPassAtomizer:
    """Orchestrates the Phase 0 Map-Reduce and Phase 1 Local Chunk Extraction."""

    def __init__(self, executor: LLMTaskExecutor) -> None:
        """Initialize the TwoPassAtomizer.

        Args:
            executor: Centralized LLM task orchestrator for executing prompts.
        """
        self.executor = executor

    def _calculate_packets(self, hydrated_text: str, packet_size: int | None = None) -> list[ChunkPacketDTO]:
        """Deterministically calculate logical chunk boundaries.

        Args:
            hydrated_text: Full document string containing block markers.
            packet_size: Number of blocks per packet chunk. When unspecified or None,
                resolves dynamically via get_settings().two_pass_atomizer_packet_size.

        Returns:
            List of ChunkPacketDTO instances containing start_block, end_block, and packet_keys.
        """
        effective_packet_size = packet_size if packet_size is not None else get_settings().two_pass_atomizer_packet_size
        block_keys: list[str] = []
        for line in hydrated_text.split("\n\n"):
            if line.startswith("[") and "] " in line:
                b_key = line[1 : line.find("]")]
                if b_key.startswith("B") and b_key[1:].isdigit():
                    block_keys.append(b_key)

        packets: list[ChunkPacketDTO] = []
        if not block_keys:
            return []
        for i in range(0, len(block_keys), effective_packet_size):
            packet_keys = block_keys[i : i + effective_packet_size]
            if not packet_keys:
                continue
            packets.append(
                ChunkPacketDTO(
                    start_block=packet_keys[0],
                    end_block=packet_keys[-1],
                    packet_keys=packet_keys,
                )
            )
        return packets

    @staticmethod
    def _build_chunk_prompt(
        compiled_prompt: CompiledPrompt,
        start_b: str,
        end_b: str,
    ) -> CompiledPrompt:
        """Build chunk-scoped CompiledPrompt with dynamic block boundary instructions.

        Args:
            compiled_prompt: Base compiled prompt containing static system and source messages.
            start_b: Starting block identifier for the chunk.
            end_b: Ending block identifier for the chunk.

        Returns:
            CompiledPrompt scoped to the target block range.
        """
        dynamic_instruction = TemplateProcessor.render_prompt(
            t"<execution_parameters>\nExtract atoms ONLY from [{start_b:raw}] to [{end_b:raw}].\n</execution_parameters>"
        )
        return CompiledPrompt(
            static_messages=compiled_prompt.static_messages,
            dynamic_messages=[LLMMessageDTO(role="user", content=dynamic_instruction)],
        )

    @staticmethod
    def _parse_local_alias_map(hydrated_text: str) -> dict[str, str]:
        """Parse block markers from hydrated text into a block ID to content map.

        Args:
            hydrated_text: Complete hydrated document string containing block markers.

        Returns:
            Dictionary mapping canonical block IDs to their extracted text content.
        """
        local_alias_map: dict[str, str] = {}
        for line in hydrated_text.split("\n\n"):
            if line.startswith("[") and "] " in line:
                b_id = line[1 : line.find("]")]
                if b_id.startswith("B") and b_id[1:].isdigit():
                    local_alias_map[b_id] = line[line.find("]") + 2 :]
        return local_alias_map

    @staticmethod
    def _resolve_bounded_quote(
        raw_block_id: str | None,
        packet_keys: list[str],
        local_alias_map: dict[str, str],
        start_b: str,
        end_b: str,
    ) -> tuple[str, ...] | None:
        """Resolve and bound a citation quote from the local alias map.

        Args:
            raw_block_id: Block identifier reported by the LLM draft atom.
            packet_keys: Allowed block identifiers for the current chunk packet.
            local_alias_map: Block identifier to text mapping for the document.
            start_b: Starting block ID for the chunk packet.
            end_b: Ending block ID for the chunk packet.

        Returns:
            Single-element tuple with bounded quote text, or None if invalid or missing.
        """
        if not raw_block_id:
            logger.warning("corrupted_atom_dropped", extra={"reason": "missing_block_id_on_non_deduction"})
            return None

        clean_id = raw_block_id.replace("[", "").replace("]", "").strip()
        if clean_id not in packet_keys:
            logger.warning(
                "corrupted_atom_dropped",
                extra={
                    "reason": "block_id_outside_packet_boundary",
                    "block_id": clean_id,
                    "packet": f"{start_b}-{end_b}",
                },
            )
            return None

        if clean_id not in local_alias_map:
            logger.warning(
                "corrupted_atom_dropped",
                extra={"reason": "hallucinated_block_id_not_found", "block_id": clean_id},
            )
            return None

        exact_quote = local_alias_map[clean_id]
        max_span_chars = get_settings().max_citation_span_chars
        if max_span_chars > 0 and len(exact_quote) > max_span_chars:
            logger.debug(
                "Bounding anchor quote exceeding %d chars Gate 2 ceiling: block_id=%s, len=%d",
                max_span_chars,
                clean_id,
                len(exact_quote),
            )
            exact_quote = exact_quote[:max_span_chars]

        if not exact_quote:
            return None
        return (exact_quote,)

    async def execute_phase_0(
        self,
        client: LLMClient,
        hydrated_text: str,
        progress_callback: Callable[[int, int], Awaitable[None]] | None = None,
    ) -> tuple[GlobalOntologyMap, TokenUsage]:
        """Extracts and merges GlobalOntologyMap from all chunks.

        Args:
            client: The LLM client to use.
            hydrated_text: Globally hydrated text with block IDs.
            progress_callback: Optional async callback reporting progress (completed, total).

        Returns:
            A tuple of merged GlobalOntologyMap and aggregated TokenUsage.
        """
        all_entities: dict[str, OntologyEntity] = {}
        all_rules: set[str] = set()
        total_usage = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)

        packets = self._calculate_packets(hydrated_text)
        if not packets:
            return GlobalOntologyMap(entities=[], macro_rules=[]), total_usage

        compiled_prompt = CompiledPrompt(
            static_messages=[
                LLMMessageDTO(role="system", content=PHASE_0_SYSTEM_PROMPT),
                LLMMessageDTO(
                    role="user",
                    content=TemplateProcessor.render_prompt(t"<source_data>\n{hydrated_text}\n</source_data>"),
                ),
            ],
            dynamic_messages=[],
        )

        await LLMCachingService.pre_cache_document(
            provider_name=client.provider_name,
            compiled_prompt=compiled_prompt,
            model_name=client.model_name,
            config=client.config,
            resolved_credential=client.resolved_credential,
        )

        try:
            async with asyncio.TaskGroup() as tg:
                tasks: list[asyncio.Task[tuple[GlobalOntologyMap, TokenUsage]]] = []
                completed = 0

                async def track_task(start_b: str, end_b: str) -> tuple[GlobalOntologyMap, TokenUsage]:
                    nonlocal completed
                    res = await self._extract_ontology_from_chunk(client, compiled_prompt, start_b, end_b)
                    completed += 1
                    if progress_callback:
                        await progress_callback(completed, len(packets))
                    return res

                for packet in packets:
                    tasks.append(tg.create_task(track_task(packet.start_block, packet.end_block)))

            for task in tasks:
                result, chunk_usage = task.result()
                total_usage = total_usage + chunk_usage
                for entity in result.entities:
                    all_entities[entity.name] = entity
                for rule in result.macro_rules:
                    all_rules.add(rule)

        finally:
            await LLMCachingService.teardown_workflow_caches(client.provider_name, "tda_phase_0")

        return GlobalOntologyMap(entities=list(all_entities.values()), macro_rules=list(all_rules)), total_usage

    async def _extract_ontology_from_chunk(
        self, client: LLMClient, compiled_prompt: CompiledPrompt, start_b: str, end_b: str
    ) -> tuple[GlobalOntologyMap, TokenUsage]:
        """Extract ontology elements from a single text packet.

        Args:
            client: The LLM client.
            compiled_prompt: Compiled prompt template with source text.
            start_b: Starting block ID for chunk.
            end_b: Ending block ID for chunk.

        Returns:
            Tuple of GlobalOntologyMap and TokenUsage for the chunk.
        """
        chunk_prompt = self._build_chunk_prompt(compiled_prompt, start_b, end_b)
        result, usage = await self.executor.execute_structured_task(
            client=client,
            messages=chunk_prompt,
            response_model=GlobalOntologyMap,
        )
        return result, usage

    async def execute_phase_1(
        self,
        client: LLMClient,
        hydrated_text: str,
        ontology: GlobalOntologyMap,
        progress_callback: Callable[[int, int], Awaitable[None]] | None = None,
    ) -> tuple[list[ExtractedAtom], TokenUsage]:
        """Extracts atomic claims from chunks utilizing the global ontology.

        Args:
            client: The LLM client.
            hydrated_text: Globally hydrated text with block IDs.
            ontology: The ontology map generated in Phase 0.
            progress_callback: Optional async callback reporting progress (completed, total).

        Returns:
            A tuple of ExtractedAtom objects with fully hydrated Opaque Stripe IDs and aggregated TokenUsage.
        """
        ontology_json = ontology.model_dump_json()
        system_prompt = TemplateProcessor.render_prompt(build_phase_1_system_prompt(ontology_json))

        total_usage = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
        packets = self._calculate_packets(hydrated_text)
        if not packets:
            return [], total_usage

        compiled_prompt = CompiledPrompt(
            static_messages=[
                LLMMessageDTO(role="system", content=system_prompt),
                LLMMessageDTO(
                    role="user",
                    content=TemplateProcessor.render_prompt(t"<source_data>\n{hydrated_text}\n</source_data>"),
                ),
            ],
            dynamic_messages=[],
        )

        await LLMCachingService.pre_cache_document(
            provider_name=client.provider_name,
            compiled_prompt=compiled_prompt,
            model_name=client.model_name,
            config=client.config,
            resolved_credential=client.resolved_credential,
        )

        all_atoms: list[ExtractedAtom] = []
        try:
            async with asyncio.TaskGroup() as tg:
                tasks: list[asyncio.Task[tuple[list[ExtractedAtom], TokenUsage]]] = []
                completed = 0

                async def track_task(
                    start_b: str, end_b: str, packet_keys: list[str], idx: int
                ) -> tuple[list[ExtractedAtom], TokenUsage]:
                    nonlocal completed
                    res = await self._extract_atoms_from_chunk(
                        client, compiled_prompt, start_b, end_b, packet_keys, idx, hydrated_text
                    )
                    completed += 1
                    if progress_callback:
                        await progress_callback(completed, len(packets))
                    return res

                for idx, packet in enumerate(packets):
                    tasks.append(
                        tg.create_task(track_task(packet.start_block, packet.end_block, packet.packet_keys, idx))
                    )

            for task in tasks:
                atoms, chunk_usage = task.result()
                total_usage = total_usage + chunk_usage
                all_atoms.extend(atoms)

        finally:
            await LLMCachingService.teardown_workflow_caches(client.provider_name, "tda_phase_1")

        return all_atoms, total_usage

    async def _extract_atoms_from_chunk(
        self,
        client: LLMClient,
        compiled_prompt: CompiledPrompt,
        start_b: str,
        end_b: str,
        packet_keys: list[str],
        chunk_index: int,
        hydrated_text: str,
    ) -> tuple[list[ExtractedAtom], TokenUsage]:
        """Extract resolved atoms from a single text packet.

        Args:
            client: The LLM client.
            compiled_prompt: Compiled prompt template with source text.
            start_b: Starting block ID for chunk.
            end_b: Ending block ID for chunk.
            packet_keys: List of valid block IDs in this packet.
            chunk_index: Numerical index of the packet.
            hydrated_text: Complete hydrated document string for alias mapping.

        Returns:
            Tuple of list of ExtractedAtom and chunk TokenUsage.
        """
        chunk_prompt = self._build_chunk_prompt(compiled_prompt, start_b, end_b)

        draft_result, usage = await self.executor.execute_structured_task(
            client=client,
            messages=chunk_prompt,
            response_model=LLMDraftAtomList,
        )

        local_alias_map = self._parse_local_alias_map(hydrated_text)
        final_atoms: list[ExtractedAtom] = []
        for draft in draft_result.atoms:
            tda_id = generate_opaque_id(EntityPrefix.TDA)
            atom_quotes: tuple[str, ...] | None = None

            if not draft.is_logical_deduction:
                atom_quotes = self._resolve_bounded_quote(
                    draft.source_block_id, packet_keys, local_alias_map, start_b, end_b
                )
                if atom_quotes is None:
                    continue

            final_atoms.append(
                ExtractedAtom(
                    reasoning=draft.reasoning,
                    resolved_claim=draft.resolved_claim,
                    is_logical_deduction=draft.is_logical_deduction,
                    source_quotes=atom_quotes,
                    tda_id=tda_id,
                    source_id=f"chunk_{chunk_index}",
                    source_sequence_index=chunk_index,
                )
            )
        return final_atoms, usage

    async def execute_phase_1_drafts(
        self,
        client: LLMClient,
        hydrated_text: str,
        ontology: GlobalOntologyMap,
        progress_callback: Callable[[int, int], Awaitable[None]] | None = None,
    ) -> tuple[DraftAtomList, TokenUsage]:
        """Extracts atomic claims from chunks returning raw drafts and handling DLQ routing.

        Args:
            client: The LLM client.
            hydrated_text: Globally hydrated text with block IDs.
            ontology: The ontology map generated in Phase 0.
            progress_callback: Optional async callback reporting progress (completed, total).

        Returns:
            A tuple of DraftAtomList containing DraftExtractedAtom instances and aggregated TokenUsage.
        """
        ontology_json = ontology.model_dump_json()
        system_prompt = TemplateProcessor.render_prompt(build_phase_1_system_prompt(ontology_json))

        total_usage = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
        packets = self._calculate_packets(hydrated_text)
        if not packets:
            return DraftAtomList(atoms=[], dlq_status=None), total_usage

        compiled_prompt = CompiledPrompt(
            static_messages=[
                LLMMessageDTO(role="system", content=system_prompt),
                LLMMessageDTO(
                    role="user",
                    content=TemplateProcessor.render_prompt(t"<source_data>\n{hydrated_text}\n</source_data>"),
                ),
            ],
            dynamic_messages=[],
        )

        await LLMCachingService.pre_cache_document(
            provider_name=client.provider_name,
            compiled_prompt=compiled_prompt,
            model_name=client.model_name,
            config=client.config,
            resolved_credential=client.resolved_credential,
        )

        all_atoms: list[DraftExtractedAtom] = []
        has_dlq = False
        try:
            async with asyncio.TaskGroup() as tg:
                tasks: list[asyncio.Task[tuple[DraftAtomList, TokenUsage]]] = []
                completed = 0

                async def track_task(
                    start_b: str, end_b: str, packet_keys: list[str], idx: int
                ) -> tuple[DraftAtomList, TokenUsage]:
                    nonlocal completed
                    res = await self._extract_drafts_from_chunk(
                        client, compiled_prompt, start_b, end_b, packet_keys, idx, hydrated_text
                    )
                    completed += 1
                    if progress_callback:
                        await progress_callback(completed, len(packets))
                    return res

                for idx, packet in enumerate(packets):
                    tasks.append(
                        tg.create_task(track_task(packet.start_block, packet.end_block, packet.packet_keys, idx))
                    )

            for task in tasks:
                result, chunk_usage = task.result()
                total_usage = total_usage + chunk_usage
                if result.dlq_status:
                    has_dlq = True
                    logger.warning("dlq_chunk_detected", extra={"dlq_status": result.dlq_status})
                all_atoms.extend(result.atoms)

        finally:
            await LLMCachingService.teardown_workflow_caches(client.provider_name, "tda_phase_1_drafts")

        return DraftAtomList(atoms=all_atoms, dlq_status="FAILED/DLQ" if has_dlq else None), total_usage

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
    ) -> tuple[DraftAtomList, TokenUsage]:
        """Extract draft atoms from a single chunk with retry policy.

        Args:
            client: The LLM client.
            compiled_prompt: Compiled prompt template with source text.
            start_b: Starting block ID for chunk.
            end_b: Ending block ID for chunk.
            packet_keys: List of valid block IDs in this packet.
            chunk_index: Numerical index of the packet.
            hydrated_text: Complete hydrated document string for alias mapping.

        Returns:
            Tuple of DraftAtomList and chunk TokenUsage.
        """
        chunk_prompt = self._build_chunk_prompt(compiled_prompt, start_b, end_b)

        draft_result, usage = await self.executor.execute_structured_task(
            client=client,
            messages=chunk_prompt,
            response_model=LLMDraftAtomList,
        )

        local_alias_map = self._parse_local_alias_map(hydrated_text)
        final_drafts: list[DraftExtractedAtom] = []
        for draft in draft_result.atoms:
            if draft.is_logical_deduction:
                final_drafts.append(
                    DraftExtractedAtom(
                        reasoning=draft.reasoning,
                        resolved_claim=draft.resolved_claim,
                        is_logical_deduction=True,
                        source_quotes=None,
                        draft_id=draft.draft_id,
                        source_sequence_index=chunk_index,
                    )
                )
                continue

            draft_quotes = self._resolve_bounded_quote(
                draft.source_block_id, packet_keys, local_alias_map, start_b, end_b
            )
            if draft_quotes is None:
                continue

            final_drafts.append(
                DraftExtractedAtom(
                    reasoning=draft.reasoning,
                    resolved_claim=draft.resolved_claim,
                    is_logical_deduction=False,
                    source_quotes=draft_quotes,
                    draft_id=draft.draft_id,
                    source_sequence_index=chunk_index,
                )
            )

        return DraftAtomList(atoms=final_drafts), usage

    async def _extract_drafts_from_chunk(
        self,
        client: LLMClient,
        compiled_prompt: CompiledPrompt,
        start_b: str,
        end_b: str,
        packet_keys: list[str],
        chunk_index: int,
        hydrated_text: str,
    ) -> tuple[DraftAtomList, TokenUsage]:
        """Execute chunk extraction trapping fatal failures into DLQ.

        Args:
            client: The LLM client.
            compiled_prompt: Compiled prompt template with source text.
            start_b: Starting block ID for chunk.
            end_b: Ending block ID for chunk.
            packet_keys: List of valid block IDs in this packet.
            chunk_index: Numerical index of the packet.
            hydrated_text: Complete hydrated document string for alias mapping.

        Returns:
            Tuple of DraftAtomList and TokenUsage.
        """
        try:
            return await self._extract_drafts_from_chunk_with_retry(
                client, compiled_prompt, start_b, end_b, packet_keys, chunk_index, hydrated_text
            )
        except (ValidationError, AppException, OSError, RuntimeError, ValueError, RetryError) as e:
            return self._dispatch_dlq_failure(e)

    @staticmethod
    def _dispatch_dlq_failure(exc: Exception) -> tuple[DraftAtomList, TokenUsage]:
        """Dispatch unhandled chunk worker failure to typed DLQ result.

        Args:
            exc: Exception that caused chunk extraction failure.

        Returns:
            Tuple of DraftAtomList with DLQ status and zero TokenUsage.
        """
        logger.error("DLQ Worker Failed: %s", exc, exc_info=True)
        return DraftAtomList(atoms=[], dlq_status="FAILED/DLQ"), TokenUsage(
            prompt_tokens=0, completion_tokens=0, total_tokens=0
        )

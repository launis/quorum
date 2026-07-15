import asyncio
import logging
import uuid

from pydantic import BaseModel, ConfigDict, Field

from backend_v2.llm.client import LLMClient
from backend_v2.models.dtos.dag_models import ExtractedAtom, GlobalOntologyMap
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.prompts.atom_extraction import (
    PHASE_0_SYSTEM_PROMPT,
    PHASE_1_SYSTEM_PROMPT,
)
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)


class DraftExtractedAtom(BaseModel):
    """Draft representation of an atom before AliasEngine hydration."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    reasoning: str = Field(description="Chain-of-thought logic.")
    resolved_claim: str = Field(description="The cleaned claim.")
    source_quote: str = Field(description="The exact quote from text.")
    draft_id: str = Field(description="A short temporary ID assigned by LLM, e.g. a0, a1.")


class DraftAtomList(BaseModel):
    """Wrapper for a list of draft atoms returned by structured task execution."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    atoms: list[DraftExtractedAtom]


class TwoPassAtomizer:
    """Orchestrates the Phase 0 Map-Reduce and Phase 1 Local Chunk Extraction."""

    def __init__(self, executor: LLMTaskExecutor) -> None:
        """Initialize the TwoPassAtomizer.

        Args:
            executor: Centralized LLM task orchestrator for executing prompts.
        """
        self.executor = executor

    async def execute_phase_0(self, client: LLMClient, chunks: list[str]) -> GlobalOntologyMap:
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
            for chunk in chunks:
                tasks.append(tg.create_task(self._extract_ontology_from_chunk(client, chunk, sem)))

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
        self, client: LLMClient, chunks: list[str], ontology: GlobalOntologyMap
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
            for idx, chunk in enumerate(chunks):
                tasks.append(tg.create_task(self._extract_atoms_from_chunk(client, chunk, idx, ontology_json, sem)))

        for task in tasks:
            all_atoms.extend(task.result())

        return all_atoms

    async def _extract_atoms_from_chunk(
        self, client: LLMClient, chunk: str, chunk_index: int, ontology_json: str, sem: asyncio.Semaphore
    ) -> list[ExtractedAtom]:
        async with sem:
            system_prompt = PHASE_1_SYSTEM_PROMPT.replace("{ontology_map_json}", ontology_json)
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"<source_data>\n{chunk}\n</source_data>"},
            ]

            draft_result, _ = await self.executor.execute_structured_task(
                client=client,
                messages=messages,
                response_model=DraftAtomList,
            )

            final_atoms = []
            for draft in draft_result.atoms:
                # Generate a compliant Opaque Stripe ID for the extracted atom.
                # AliasEngine integration in 2.2 will refine this mapping.
                tda_id = f"tda_{uuid.uuid4().hex[:8]}"
                final_atoms.append(
                    ExtractedAtom(
                        reasoning=draft.reasoning,
                        resolved_claim=draft.resolved_claim,
                        source_quote=draft.source_quote,
                        tda_id=tda_id,
                        source_id=f"chunk_{chunk_index}",
                    )
                )
            return final_atoms

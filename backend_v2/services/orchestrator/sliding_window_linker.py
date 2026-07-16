"""Global Sliding Window Linker for DAG topology generation.

Uses a sliding window approach over extracted atoms to resolve cross-chunk causal
dependencies without exceeding LLM context windows or losing attention on middle chunks.
"""

from collections import defaultdict

from pydantic import BaseModel, ConfigDict, Field

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.models.dtos.dag_models import (
    CausalEdge,
    ExtractedAtom,
    GlobalOntologyMap,
    LinkedAtomGraph,
)
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.prompt import CompiledPrompt
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.prompts.graph_linking import (
    LINKER_SYSTEM_PROMPT,
    LINKER_USER_PROMPT,
)
from backend_v2.utils.alias_engine import AliasEngine


class LinkerEdgeDTO(BaseModel):
    """Temporary DTO for LLM structured output before hydration."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    edge_reasoning: str = Field(description="Chain-of-thought explaining why the dependency exists.")
    tda_id: str = Field(description="The alias of the parent claim (e.g., 'a0').")
    expected_status: ExecutionStatus = Field(default=ExecutionStatus.PASSED)


class LinkerDependencyDTO(BaseModel):
    """Mapping between a child alias and its parent dependencies."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    child_alias: str = Field(description="The alias of the child claim (e.g., 'a1').")
    parent_dependencies: list[LinkerEdgeDTO] = Field(
        default_factory=list,
        description="List of parent dependencies for this child.",
    )


class LinkerResponseDTO(BaseModel):
    """Temporary DTO for LLM structured output before hydration."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    dependencies: list[LinkerDependencyDTO] = Field(
        default_factory=list,
        description="List of dependencies mapping child aliases to parent aliases.",
    )


class SlidingWindowLinker:
    """Links ExtractedAtoms into a LinkedAtomGraph using a sliding window."""

    def __init__(self, window_size: int = 4, overlap: int = 2) -> None:
        """Initialize the linker.

        Args:
            window_size: Number of chunks per window.
            overlap: Number of chunks to overlap between windows.
        """
        self.window_size = window_size
        self.overlap = overlap

    def _get_sliding_windows(self, chunks: list[list[ExtractedAtom]]) -> list[list[list[ExtractedAtom]]]:
        """Yield sliding windows of chunks."""
        windows: list[list[list[ExtractedAtom]]] = []
        if not chunks:
            return windows
        if len(chunks) <= self.window_size:
            return [chunks]

        step = self.window_size - self.overlap
        if step <= 0:
            step = 1

        for i in range(0, len(chunks), step):
            window = chunks[i : i + self.window_size]
            windows.append(window)
            if i + self.window_size >= len(chunks):
                break

        return windows

    async def link_graph(
        self,
        executor: LLMTaskExecutor,
        client: LLMClient,
        atoms: list[ExtractedAtom],
        ontology_map: GlobalOntologyMap,
    ) -> list[LinkedAtomGraph]:
        """Link atoms together into a causal graph.

        Args:
            executor: The LLM executor to run the generation.
            client: The LLM client.
            atoms: Flat list of extracted atoms.
            ontology_map: The global ontology map for anaphora resolution.

        Returns:
            A list of LinkedAtomGraph objects with populated depends_on.
        """
        if not atoms:
            return []

        # 1. Group atoms by source_id (chunk_index) maintaining insertion order
        chunk_groups: dict[str, list[ExtractedAtom]] = defaultdict(list)
        for atom in atoms:
            chunk_groups[atom.source_id or "default"].append(atom)

        chunks = list(chunk_groups.values())
        windows = self._get_sliding_windows(chunks)

        master_deps: dict[str, dict[str, CausalEdge]] = defaultdict(dict)

        ontology_text = ontology_map.model_dump_json(indent=2)

        for window_chunks in windows:
            # Flatten atoms in the current window
            window_atoms = [atom for chunk in window_chunks for atom in chunk]
            if not window_atoms:
                continue

            alias_engine = AliasEngine()
            claims_text = ""

            for atom in window_atoms:
                alias = alias_engine.register(atom.tda_id, "a")
                claims_text += f"[{alias}] {atom.resolved_claim}\n"
                claims_text += f"Quote: {atom.source_quote}\n\n"

            user_prompt = LINKER_USER_PROMPT.format(
                global_ontology_map=ontology_text,
                claims_window=claims_text.strip(),
            )

            static_messages = [
                {"role": "system", "content": LINKER_SYSTEM_PROMPT},
            ]
            dynamic_messages = [
                {"role": "user", "content": user_prompt},
            ]

            compiled_prompt = CompiledPrompt(
                static_messages=static_messages,
                dynamic_messages=dynamic_messages,
                metadata={"strictness_level": "high"},
            )

            try:
                response, _ = await executor.execute_structured_task(
                    client=client,
                    messages=compiled_prompt,
                    response_model=LinkerResponseDTO,
                )
            except Exception as e:
                # 01-python-backend.md: Zero-Compromise Pledge. No graceful degradation.
                raise AppException(
                    message=f"Failed to link graph window: {str(e)}",
                    status_code=500,
                    details={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.value},
                ) from e

            # Hydrate and merge edges
            for dep_mapping in response.dependencies:
                child_alias = dep_mapping.child_alias
                deps = dep_mapping.parent_dependencies

                child_tda_id = alias_engine.resolve_alias(child_alias)
                child_atom = next((a for a in window_atoms if a.tda_id == child_tda_id), None)
                if not child_atom:
                    continue

                for dep in deps:
                    parent_tda_id = alias_engine.resolve_alias(dep.tda_id)
                    # Self-dependency check to prevent immediate loops
                    if parent_tda_id == child_tda_id:
                        continue

                    edge = CausalEdge(
                        edge_reasoning=dep.edge_reasoning,
                        tda_id=parent_tda_id,
                        source_id=child_atom.source_id or "unknown",
                        expected_status=dep.expected_status,
                    )
                    master_deps[child_tda_id][parent_tda_id] = edge

        # Finally, wrap all atoms into LinkedAtomGraphs
        results = []
        for atom in atoms:
            deps_list = list(master_deps[atom.tda_id].values())
            results.append(LinkedAtomGraph(atom=atom, depends_on=deps_list))

        return results

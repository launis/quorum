"""Global Sliding Window Linker for DAG topology generation.

Uses a sliding window approach over extracted atoms to resolve cross-chunk causal
dependencies without exceeding LLM context windows or losing attention on middle chunks.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import status
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field

from backend_v2.core.template_processor import TemplateProcessor
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.models.core_base import coerce_source_quotes_tuple
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.dag_models import (
    CausalEdge,
    ExtractedAtom,
    GlobalOntologyMap,
    LinkedAtomGraph,
)
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.llm import LLMMessageDTO
from backend_v2.models.prompt import CompiledPrompt, PromptMetadataDTO
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.prompts.graph_linking import (
    LINKER_SYSTEM_PROMPT,
    build_linker_user_prompt,
)
from backend_v2.settings import Settings, get_settings
from backend_v2.utils.alias_engine import AliasEngine

__all__ = [
    "LinkerDependencyDTO",
    "LinkerEdgeDTO",
    "LinkerResponseDTO",
    "SlidingWindowLinker",
    "StructuralAnchorRankDTO",
    "WindowCausalEdgesDTO",
]

logger = logging.getLogger(__name__)


class LinkerEdgeDTO(BaseModel):
    """Temporary DTO for LLM structured output before hydration.

    Attributes:
        edge_reasoning: Chain-of-thought explaining why the dependency exists.
        tda_id: The alias of the parent claim (e.g., 'a0').
        expected_status: Expected execution status of the parent node.
        warrant_quotes: Optional verbatim quotes from source text grounding the Toulmin inferential warrant.
    """

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    edge_reasoning: Annotated[str, Field(description="Chain-of-thought explaining why the dependency exists.")]
    tda_id: Annotated[str, Field(description="The alias of the parent claim (e.g., 'a0').")]
    expected_status: Annotated[ExecutionStatus, Field(default=ExecutionStatus.PASSED)] = ExecutionStatus.PASSED
    warrant_quotes: Annotated[
        tuple[str, ...] | None,
        BeforeValidator(coerce_source_quotes_tuple),
        Field(
            default=None,
            description="Optional verbatim quotes from source text grounding the Toulmin inferential warrant.",
        ),
    ] = None


class LinkerDependencyDTO(BaseModel):
    """Mapping between a child alias and its parent dependencies.

    Attributes:
        child_alias: The alias of the child claim (e.g., 'a1').
        parent_dependencies: List of parent dependencies for this child.
    """

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    child_alias: Annotated[str, Field(description="The alias of the child claim (e.g., 'a1').")]
    parent_dependencies: Annotated[
        list[LinkerEdgeDTO],
        Field(
            default_factory=list,
            description="List of parent dependencies for this child.",
        ),
    ]


class LinkerResponseDTO(BaseModel):
    """Temporary DTO for LLM structured output before hydration.

    Attributes:
        dependencies: List of dependencies mapping child aliases to parent aliases.
    """

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    dependencies: Annotated[
        list[LinkerDependencyDTO],
        Field(
            default_factory=list,
            description="List of dependencies mapping child aliases to parent aliases.",
        ),
    ]


class WindowCausalEdgesDTO(BaseModel):
    """Encapsulates parent causal edges for a child node within a sliding window.

    Attributes:
        edges: Map of parent TDA ID to CausalEdge.
    """

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    edges: Annotated[
        dict[str, CausalEdge],
        Field(
            default_factory=dict,
            description="Map of parent TDA ID to CausalEdge.",
        ),
    ]


class StructuralAnchorRankDTO(BaseModel):
    """Rank key and container for structural anchor candidates.

    Attributes:
        neg_score: Negative composite score for descending priority ordering.
        tie_breaker_index: Signed index for deterministic tie-break ordering (positive for asc, negative for desc).
        atom: The underlying extracted atom.
    """

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    neg_score: Annotated[int, Field(description="Negative score for descending priority ordering.")]
    tie_breaker_index: Annotated[int, Field(description="Signed index for deterministic tie-break ordering.")]
    atom: Annotated[ExtractedAtom, Field(description="The underlying extracted atom.")]

    def __lt__(self, other: StructuralAnchorRankDTO) -> bool:
        """Compare two rank keys deterministically with strict total ordering."""
        if self.neg_score != other.neg_score:
            return self.neg_score < other.neg_score
        if self.tie_breaker_index != other.tie_breaker_index:
            return self.tie_breaker_index < other.tie_breaker_index
        return self.atom.tda_id < other.atom.tda_id


class SlidingWindowLinker:
    """Discovers causal DAG dependencies between ExtractedAtoms using a context-bounded sliding window heuristic.

    Attributes:
        window_size: Number of chunks per window.
        overlap: Number of chunks to overlap between windows.
        max_atoms_per_window: Maximum atoms allowed per sliding window.
        max_global_root_axioms: Global maximum ceiling for injected context anchors.
        min_window_atoms_quota: Minimum window atoms quota.
        max_root_axioms: Maximum persistent deliverable root axioms.
        max_bridge_axioms: Maximum persistent deliverable deductive bridge lemmas.
    """

    def __init__(
        self,
        window_size: int = 4,
        overlap: int = 2,
        settings: Settings | None = None,
    ) -> None:
        """Initialize the linker.

        Args:
            window_size: Number of chunks per window.
            overlap: Number of chunks to overlap between windows.
            settings: Optional application settings for configuration injection.
        """
        self.window_size = window_size
        self.overlap = overlap
        resolved_settings = settings or get_settings()
        self.max_atoms_per_window = resolved_settings.linker_max_atoms_per_window
        self.max_global_root_axioms = resolved_settings.linker_max_global_root_axioms
        self.min_window_atoms_quota = resolved_settings.linker_min_window_atoms_quota
        self.max_root_axioms = resolved_settings.linker_max_root_axioms
        self.max_bridge_axioms = resolved_settings.linker_max_bridge_axioms

    def _select_structural_anchors(
        self,
        processed_atoms: dict[str, ExtractedAtom],
        current_window_ids: set[str],
        master_deps: dict[str, WindowCausalEdgesDTO],
        current_window_size: int,
        deliverable_input_keys: set[str] | None = None,
    ) -> list[ExtractedAtom]:
        """Select persistent deliverable structural anchors (foundational roots & deductive bridges) for header.

        Single-pass O(|V| + |E|) metric precomputation resolves in_degree and out_degree for
        all candidate atoms. Eligible atoms outside current_window_ids and within
        deliverable_input_keys are partitioned into:
          - Candidate Roots (V_root): in_degree == 0, ranked by <-out_degree, sequence_asc>
          - Candidate Bridges (V_bridge): (in_degree >= 1 and out_degree >= 1) or in_degree >= 2,
            ranked by <-in_degree * (out_degree + 1), sequence_desc>
        Single-premise leaf nodes (in_degree == 1 and out_degree == 0) are excluded from both pools.

        Dynamic slack waterfall divides K_eff base quotas evenly before distributing unused capacity,
        guaranteeing foundational roots are never starved when K_eff <= 4.

        Args:
            processed_atoms: Atoms processed in preceding windows.
            current_window_ids: Set of atom TDA IDs in the current window.
            master_deps: Master dictionary of discovered parent dependencies so far.
            current_window_size: Number of atoms in the current window.
            deliverable_input_keys: Optional set of deliverable input keys for scoping.

        Returns:
            List of ExtractedAtom instances representing selected structural anchors for the header.
        """
        out_degree_counts: dict[str, int] = {tda_id: 0 for tda_id in processed_atoms}
        for deps in master_deps.values():
            for edge_target in deps.edges:
                if edge_target in out_degree_counts:
                    out_degree_counts[edge_target] += 1

        candidate_roots: list[StructuralAnchorRankDTO] = []
        candidate_bridges: list[StructuralAnchorRankDTO] = []

        for atom in processed_atoms.values():
            if atom.tda_id in current_window_ids:
                continue
            if deliverable_input_keys is not None and len(deliverable_input_keys) > 0:
                if atom.source_input_key not in deliverable_input_keys:
                    continue

            in_deg = 0
            if atom.tda_id in master_deps:
                in_deg = len(master_deps[atom.tda_id].edges)
            out_deg = out_degree_counts[atom.tda_id]

            if in_deg == 0:
                candidate_roots.append(
                    StructuralAnchorRankDTO(
                        neg_score=-out_deg,
                        tie_breaker_index=atom.source_sequence_index,
                        atom=atom,
                    )
                )
            elif (in_deg >= 1 and out_deg >= 1) or in_deg >= 2:
                candidate_bridges.append(
                    StructuralAnchorRankDTO(
                        neg_score=-(in_deg * (out_deg + 1)),
                        tie_breaker_index=-atom.source_sequence_index,
                        atom=atom,
                    )
                )

        candidate_roots.sort()
        candidate_bridges.sort()

        k_eff = min(self.max_global_root_axioms, max(0, self.max_atoms_per_window - current_window_size))
        if k_eff == 0:
            return []

        base_root_quota = min(self.max_root_axioms, (k_eff + 1) // 2)
        base_bridge_quota = min(self.max_bridge_axioms, k_eff // 2)

        selected_roots = candidate_roots[:base_root_quota]
        selected_bridges = candidate_bridges[:base_bridge_quota]

        # Waterfall surplus slots to roots if bridges did not consume full quota
        remaining_for_roots = k_eff - len(selected_roots) - len(selected_bridges)
        if remaining_for_roots > 0 and len(candidate_roots) > len(selected_roots):
            extra_roots = candidate_roots[len(selected_roots) : len(selected_roots) + remaining_for_roots]
            selected_roots.extend(extra_roots)

        # Waterfall surplus slots to bridges if roots did not consume full quota
        remaining_for_bridges = k_eff - len(selected_roots) - len(selected_bridges)
        if remaining_for_bridges > 0 and len(candidate_bridges) > len(selected_bridges):
            extra_bridges = candidate_bridges[len(selected_bridges) : len(selected_bridges) + remaining_for_bridges]
            selected_bridges.extend(extra_bridges)

        return [anchor.atom for anchor in selected_roots + selected_bridges]

    def _get_sliding_windows(self, chunks: list[list[ExtractedAtom]]) -> list[list[list[ExtractedAtom]]]:
        """Yield sliding windows of chunks.

        Args:
            chunks: A list of atom chunks to be windowed.

        Returns:
            A list of sliding windows, where each window is a list of chunks.
        """
        windows: list[list[list[ExtractedAtom]]] = []
        if not chunks:
            return windows

        max_atoms = self.max_atoms_per_window

        # 1. Pre-subdivide Oversized Chunks
        subdivided_chunks: list[list[ExtractedAtom]] = []
        for chunk in chunks:
            if len(chunk) > max_atoms:
                for j in range(0, len(chunk), max_atoms):
                    subdivided_chunks.append(chunk[j : j + max_atoms])
            else:
                subdivided_chunks.append(chunk)

        if not subdivided_chunks:
            return windows

        # 2. Dynamic Overlap While-Loop
        i = 0
        while i < len(subdivided_chunks):
            window: list[list[ExtractedAtom]] = []
            current_atoms = 0
            chunks_taken = 0

            for j in range(i, len(subdivided_chunks)):
                next_chunk = subdivided_chunks[j]
                if len(window) == self.window_size:
                    break
                if current_atoms + len(next_chunk) > max_atoms and window:
                    break

                window.append(next_chunk)
                current_atoms += len(next_chunk)
                chunks_taken += 1

            windows.append(window)

            if i + chunks_taken >= len(subdivided_chunks):
                break

            step = max(1, chunks_taken - self.overlap)
            i += step

        return windows

    async def link_graph(
        self,
        executor: LLMTaskExecutor,
        client: LLMClient,
        atoms: list[ExtractedAtom],
        ontology_map: GlobalOntologyMap,
        progress_callback: Callable[[int, int], Awaitable[None]] | None = None,
        deliverable_input_keys: set[str] | None = None,
    ) -> tuple[list[LinkedAtomGraph], TokenUsage]:
        """Link atoms together into a causal graph.

        Args:
            executor: The LLM executor to run the generation.
            client: The LLM client.
            atoms: Flat list of extracted atoms.
            ontology_map: The global ontology map for anaphora resolution.
            progress_callback: Optional asynchronous callback for reporting progress.
            deliverable_input_keys: Optional set of deliverable input keys for scoping root axioms.

        Returns:
            A tuple of list[LinkedAtomGraph] objects with populated depends_on and aggregated TokenUsage.

        Raises:
            AppException: If LLM execution fails critically (ErrorCodes.AGENT_EXECUTION_CRITICAL).
        """
        if not atoms:
            return [], TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)

        # 1. Group atoms by source_id (chunk_index) maintaining insertion order
        chunk_groups: dict[str, list[ExtractedAtom]] = {}
        for atom in atoms:
            source_key = atom.source_id
            if not source_key:
                source_key = "default"
            if source_key not in chunk_groups:
                chunk_groups[source_key] = []
            chunk_groups[source_key].append(atom)

        chunks = list(chunk_groups.values())
        windows = self._get_sliding_windows(chunks)

        master_deps: dict[str, WindowCausalEdgesDTO] = {}
        processed_atoms: dict[str, ExtractedAtom] = {}
        total_usage = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)

        ontology_text = ontology_map.model_dump_json(indent=2)

        for i, window_chunks in enumerate(windows):
            if progress_callback:
                await progress_callback(i, len(windows))

            # Flatten atoms in the current window
            window_atoms = [atom for chunk in window_chunks for atom in chunk]
            if not window_atoms:
                continue

            current_window_ids = {atom.tda_id for atom in window_atoms}

            # Phase 5: Select deliverable structural anchors for window index i > 0
            selected_structural_anchors: list[ExtractedAtom] = []
            if i > 0:
                selected_structural_anchors = self._select_structural_anchors(
                    processed_atoms=processed_atoms,
                    current_window_ids=current_window_ids,
                    master_deps=master_deps,
                    current_window_size=len(window_atoms),
                    deliverable_input_keys=deliverable_input_keys,
                )

            alias_engine = AliasEngine()
            header_text = ""
            if selected_structural_anchors:
                header_text = "--- GLOBAL CONTEXT ANCHORS (FOUNDATIONAL ROOTS & DEDUCTIVE BRIDGES) ---\n"
                for atom in selected_structural_anchors:
                    alias = alias_engine.register(atom.tda_id, "a")
                    header_text += f"[{alias}] {atom.resolved_claim}\n"
                    if atom.source_quotes:
                        header_text += f"Quote: {' [...] '.join(atom.source_quotes)}\n\n"
                    else:
                        header_text += "Quote: [None]\n\n"

            current_claims_text = ""
            for atom in window_atoms:
                alias = alias_engine.register(atom.tda_id, "a")
                current_claims_text += f"[{alias}] {atom.resolved_claim}\n"
                if atom.source_quotes:
                    current_claims_text += f"Quote: {' [...] '.join(atom.source_quotes)}\n\n"
                else:
                    current_claims_text += "Quote: [None]\n\n"

            claims_text = (header_text + current_claims_text).strip()

            user_prompt = TemplateProcessor.render_prompt(
                build_linker_user_prompt(
                    global_ontology_map=ontology_text,
                    claims_window=claims_text,
                )
            )

            static_messages = [
                LLMMessageDTO(role="system", content=LINKER_SYSTEM_PROMPT),
            ]
            dynamic_messages = [
                LLMMessageDTO(role="user", content=user_prompt),
            ]

            compiled_prompt = CompiledPrompt(
                static_messages=static_messages,
                dynamic_messages=dynamic_messages,
                metadata=PromptMetadataDTO(),
            )

            try:
                # Phase 3, Step 3.3: Direct task execution delegating rate limiting to LiteLLMProvider
                response, usage = await executor.execute_structured_task(
                    client=client,
                    messages=compiled_prompt,
                    response_model=LinkerResponseDTO,
                )
                total_usage = total_usage + usage
            except Exception as e:
                # 01-python-backend.md: Zero-Compromise Pledge. No graceful degradation.
                msg = f"Failed to link graph window: {str(e)}"
                logger.error(
                    "[SlidingWindowLinker] %s: %s",
                    ErrorCodes.AGENT_EXECUTION_CRITICAL.name,
                    msg,
                    exc_info=True,
                )
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.value},
                ) from e

            # Hydrate and merge edges
            for dep_mapping in response.dependencies:
                child_alias = dep_mapping.child_alias
                deps = dep_mapping.parent_dependencies

                if child_alias not in alias_engine.alias_map:
                    logger.warning(
                        "Hallucinated child alias dropped: %s",
                        child_alias,
                    )
                    continue
                child_tda_id = alias_engine.alias_map[child_alias]

                child_atom = next((a for a in window_atoms if a.tda_id == child_tda_id), None)
                if not child_atom:
                    continue

                for dep in deps:
                    if dep.tda_id not in alias_engine.alias_map:
                        logger.warning(
                            "Hallucinated parent alias dropped: %s (child: %s)",
                            dep.tda_id,
                            child_alias,
                        )
                        continue
                    parent_tda_id = alias_engine.alias_map[dep.tda_id]

                    # Self-dependency check to prevent immediate loops
                    if parent_tda_id == child_tda_id:
                        continue

                    child_source_id = child_atom.source_id
                    if not child_source_id:
                        child_source_id = "unknown"

                    edge = CausalEdge(
                        edge_reasoning=dep.edge_reasoning,
                        tda_id=parent_tda_id,
                        source_id=child_source_id,
                        expected_status=dep.expected_status,
                        warrant_quotes=dep.warrant_quotes,
                    )
                    if child_tda_id in master_deps:
                        current_edges = dict(master_deps[child_tda_id].edges)
                    else:
                        current_edges = {}
                    current_edges[parent_tda_id] = edge
                    master_deps[child_tda_id] = WindowCausalEdgesDTO(edges=current_edges)

            for atom in window_atoms:
                processed_atoms[atom.tda_id] = atom

        # Finally, wrap all atoms into LinkedAtomGraphs
        results = []
        for atom in atoms:
            if atom.tda_id in master_deps:
                deps_list = list(master_deps[atom.tda_id].edges.values())
            else:
                deps_list = []
            results.append(LinkedAtomGraph(atom=atom, depends_on=deps_list))

        return results, total_usage

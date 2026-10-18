"""Autonomous Causal Discovery Engine.

Executes exploratory text DAG argument mining, sliding window causal linking,
and Kahn-based topological evaluation over unconstrained text documents.
"""

from __future__ import annotations

import logging
import re
from typing import Any, override

from fastapi import status

from backend_v2.core.telemetry import get_tracer
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.causal_discovery import (
    CausalEdgeDTO,
    CausalGraphPayloadDTO,
    CausalNodeDTO,
)
from backend_v2.models.dtos.dag_models import (
    AtomEvaluationResultDTO,
    AtomExecutionState,
    ExtractedAtom,
    LinkedAtomGraph,
)
from backend_v2.models.dtos.engine import EngineExecutionRequest, EngineExecutionResult
from backend_v2.models.enums import ExecutionStatus
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.engines.base import ExecutionEngine
from backend_v2.services.orchestrator.sliding_window_linker import SlidingWindowLinker
from backend_v2.services.orchestrator.topological_evaluator import TopologicalEvaluator
from backend_v2.services.orchestrator.two_pass_atomizer import TwoPassAtomizer
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

__all__ = ["CausalDiscoveryEngine"]


class CausalDiscoveryEngine(ExecutionEngine):
    """Engine executing autonomous causal discovery and argument mining over documents."""

    def __init__(self, prompt_compiler: Any) -> None:
        """Initialize CausalDiscoveryEngine with injected prompt compiler.

        Args:
            prompt_compiler: Injected prompt compiler instance.
        """
        self._compiler = prompt_compiler

    @property
    def telemetry_strategy_label(self) -> str:
        """Canonical telemetry strategy label for execution trace recording."""
        return "causal"

    @override
    async def execute(self, request: EngineExecutionRequest) -> EngineExecutionResult:
        """Executes autonomous causal discovery pipeline over source document text.

        Args:
            request: The strongly typed engine execution request.

        Returns:
            The engine execution result containing the causal graph payload and token usage.

        Raises:
            AppException: If document text is empty (CAUSAL_DISCOVERY_EMPTY_DOCUMENT) or
                no valid propositions are extracted (CAUSAL_DISCOVERY_DATA_STARVATION).
        """
        tracer = get_tracer(__name__)
        with tracer.start_as_current_span("causal_discovery.execute") as span:
            span.set_attribute("execution.id", request.context.execution_id)
            span.set_attribute("step.id", request.step.id)

            # Step 3.1: Pre-flight Ingress Check
            document_text = request.global_source_text
            if not document_text or not document_text.strip():
                msg = f"Causal discovery cannot execute on an empty text document for Step '{request.step.id}'."
                logger.error("[CausalDiscoveryEngine] %s: %s", ErrorCodes.CAUSAL_DISCOVERY_EMPTY_DOCUMENT.name, msg)
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    details={
                        "error_code": ErrorCodes.CAUSAL_DISCOVERY_EMPTY_DOCUMENT.value,
                        "step_id": request.step.id,
                    },
                )

            # Step 3.1 / 3.2: Paragraph Indexing & Document Provenance
            directive_pattern = re.compile(
                r'<ai_context_directive\s+document="(?P<doc_key>[A-Za-z0-9_]{1,64})">(?P<body>.*?)</ai_context_directive>',
                re.DOTALL,
            )
            directive_tag_pattern = re.compile(r"</?ai_context_directive[^>]*>")

            paragraphs: list[str] = []
            paragraph_doc_keys: list[str | None] = []

            directive_matches = list(directive_pattern.finditer(document_text))
            if directive_matches:
                first_start = directive_matches[0].start()
                pre_text = document_text[:first_start].strip()
                if pre_text:
                    clean_pre = directive_tag_pattern.sub("", pre_text).strip()
                    for p in clean_pre.split("\n\n"):
                        p_str = p.strip()
                        if p_str:
                            paragraphs.append(p_str)
                            paragraph_doc_keys.append(None)

                for i, match in enumerate(directive_matches):
                    doc_key = match.group("doc_key")
                    seg_start = match.end()
                    seg_end = directive_matches[i + 1].start() if i + 1 < len(directive_matches) else len(document_text)
                    seg_text = document_text[seg_start:seg_end].strip()
                    if seg_text:
                        clean_seg = directive_tag_pattern.sub("", seg_text).strip()
                        for p in clean_seg.split("\n\n"):
                            p_str = p.strip()
                            if p_str:
                                paragraphs.append(p_str)
                                paragraph_doc_keys.append(doc_key)
            else:
                for p in document_text.split("\n\n"):
                    clean_p = directive_tag_pattern.sub("", p).strip()
                    if clean_p:
                        paragraphs.append(clean_p)
                        paragraph_doc_keys.append(None)

            if not paragraphs:
                msg = f"Causal discovery cannot execute on an empty text document for Step '{request.step.id}'."
                logger.error("[CausalDiscoveryEngine] %s: %s", ErrorCodes.CAUSAL_DISCOVERY_EMPTY_DOCUMENT.name, msg)
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    details={
                        "error_code": ErrorCodes.CAUSAL_DISCOVERY_EMPTY_DOCUMENT.value,
                        "step_id": request.step.id,
                    },
                )
            hydrated_text = "\n\n".join(f"[B{i}] {p}" for i, p in enumerate(paragraphs))

            llm_executor = LLMTaskExecutor(
                self._compiler,
                default_validation_context={
                    "execution_id": request.context.execution_id,
                    "step_id": request.step.id,
                },
            )
            atomizer = TwoPassAtomizer(llm_executor)

            # Step 3.3: Two-Pass Atomization with Progress Reporting
            async def p0_cb(c: int, t: int) -> None:
                if request.progress_callback and t > 0:
                    await request.progress_callback(int((c / t) * 30), 100)

            async def p1_cb(c: int, t: int) -> None:
                if request.progress_callback and t > 0:
                    await request.progress_callback(30 + int((c / t) * 30), 100)

            ontology, u_p0 = await atomizer.execute_phase_0(
                request.bound_client, hydrated_text, progress_callback=p0_cb
            )
            raw_atoms, u_p1 = await atomizer.execute_phase_1(
                request.bound_client, hydrated_text, ontology, progress_callback=p1_cb
            )

            # Lexical Verification via str.find & Document Provenance Resolution
            valid_atoms: list[ExtractedAtom] = []
            atom_key_map: dict[str, str | None] = {}
            for atom in raw_atoms:
                matched_key: str | None = None
                if atom.source_id and atom.source_id.startswith("B"):
                    suffix = atom.source_id[1:]
                    if suffix.isdigit():
                        b_idx = int(suffix)
                        if 0 <= b_idx < len(paragraph_doc_keys):
                            matched_key = paragraph_doc_keys[b_idx]

                if atom.source_quotes:
                    anchor_quote = atom.source_quotes[0]
                    if matched_key is None:
                        for p_idx, p in enumerate(paragraphs):
                            if p.find(anchor_quote) != -1:
                                matched_key = paragraph_doc_keys[p_idx]
                                break

                    if matched_key is None and directive_matches:
                        q_pos = document_text.find(anchor_quote)
                        if q_pos != -1:
                            for m in directive_matches:
                                if q_pos >= m.start():
                                    matched_key = m.group("doc_key")
                                else:
                                    break

                    if all(document_text.find(q) != -1 or hydrated_text.find(q) != -1 for q in atom.source_quotes):
                        updated_atom = atom.model_copy(update={"source_input_key": matched_key})
                        valid_atoms.append(updated_atom)
                        atom_key_map[atom.tda_id] = matched_key
                    else:
                        logger.warning("[CausalDiscoveryEngine] Dropping unanchored quote: %s", atom.tda_id)
                elif atom.is_logical_deduction:
                    updated_atom = atom.model_copy(update={"source_input_key": matched_key})
                    valid_atoms.append(updated_atom)
                    atom_key_map[atom.tda_id] = matched_key

            if not valid_atoms:
                msg = f"Causal discovery extracted 0 valid argument propositions for Step '{request.step.id}'."
                logger.error("[CausalDiscoveryEngine] %s: %s", ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION.name, msg)
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    details={
                        "error_code": ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION.value,
                        "step_id": request.step.id,
                    },
                )

            # Step 3.4: Sliding Window Argument Graph Construction
            settings = get_settings()
            linker = SlidingWindowLinker(
                window_size=settings.causal_discovery_window_size,
                overlap=settings.causal_discovery_overlap,
            )

            async def link_cb(c: int, t: int) -> None:
                if request.progress_callback and t > 0:
                    await request.progress_callback(60 + int((c / t) * 20), 100)

            linked_nodes, u_link = await linker.link_graph(
                executor=llm_executor,
                client=request.bound_client,
                atoms=valid_atoms,
                ontology_map=ontology,
                progress_callback=link_cb,
            )

            # Step 3.5: Topological Wave Execution and Cycle Defense
            evaluator = TopologicalEvaluator()

            async def noop_eval(
                nodes: list[LinkedAtomGraph], _: dict[str, AtomExecutionState]
            ) -> dict[str, AtomEvaluationResultDTO]:
                return {
                    n.atom.tda_id: AtomEvaluationResultDTO(
                        status=ExecutionStatus.PASSED,
                        reasoning="Proposition validly extracted.",
                        source_quotes=n.atom.source_quotes,
                        extensions={},
                    )
                    for n in nodes
                }

            final_states = await evaluator.evaluate_graph(linked_nodes, noop_eval)

            cycle_detected = any(
                s.status == ExecutionStatus.SYSTEM_ERROR
                and s.evaluation_reasoning is not None
                and "CYCLIC" in s.evaluation_reasoning
                for s in final_states.values()
            )

            extracted_ids = {a.tda_id for a in valid_atoms}
            causal_edges: list[CausalEdgeDTO] = []
            in_deps: dict[str, list[str]] = {aid: [] for aid in extracted_ids}
            out_deps: dict[str, list[str]] = {aid: [] for aid in extracted_ids}

            for node in linked_nodes:
                cid = node.atom.tda_id
                if cid not in extracted_ids:
                    continue
                for edge in node.depends_on:
                    pid = edge.tda_id
                    if pid in extracted_ids and pid != cid:
                        in_deps[cid].append(pid)
                        out_deps[pid].append(cid)
                        causal_edges.append(CausalEdgeDTO(source_id=pid, target_id=cid, reasoning=edge.edge_reasoning))

            isolated_ids = [aid for aid in extracted_ids if not in_deps[aid] and not out_deps[aid]]

            root_cause_ids: list[str] = [
                aid
                for aid in extracted_ids
                if aid in final_states
                and final_states[aid].status in (ExecutionStatus.SYSTEM_ERROR, ExecutionStatus.BLOCKED)
                and not any(
                    p in final_states
                    and final_states[p].status in (ExecutionStatus.SYSTEM_ERROR, ExecutionStatus.BLOCKED)
                    for p in in_deps[aid]
                )
            ]

            causal_nodes: list[CausalNodeDTO] = []
            for node in linked_nodes:
                nid = node.atom.tda_id
                if nid not in extracted_ids:
                    continue
                node_status = final_states[nid].status if nid in final_states else ExecutionStatus.PASSED

                visited: set[str] = set()
                q = list(in_deps[nid])
                depth = 0
                max_d = len(extracted_ids)
                while q and depth < max_d:
                    depth += 1
                    curr = q.pop(0)
                    if curr in visited:
                        continue
                    visited.add(curr)
                    if curr in final_states and final_states[curr].status in (
                        ExecutionStatus.SYSTEM_ERROR,
                        ExecutionStatus.BLOCKED,
                    ):
                        q.extend(u for u in in_deps[curr] if u not in visited)

                blame_parents = [
                    b
                    for b in visited
                    if b in final_states
                    and final_states[b].status in (ExecutionStatus.SYSTEM_ERROR, ExecutionStatus.BLOCKED)
                ]

                resolved_key = node.atom.source_input_key
                if resolved_key is None and nid in atom_key_map:
                    resolved_key = atom_key_map[nid]

                causal_nodes.append(
                    CausalNodeDTO(
                        node_id=nid,
                        claim=node.atom.resolved_claim,
                        source_quotes=node.atom.source_quotes,
                        paragraph_ref=node.atom.source_id,
                        status=node_status,
                        blame_parent_ids=blame_parents,
                        dependent_child_ids=out_deps[nid],
                        source_input_key=resolved_key,
                    )
                )

            partition_node_ids: dict[str, list[str]] = {}
            for c_node in causal_nodes:
                if c_node.source_input_key is not None:
                    if c_node.source_input_key not in partition_node_ids:
                        partition_node_ids[c_node.source_input_key] = []
                    partition_node_ids[c_node.source_input_key].append(c_node.node_id)

            edge_root_causes: list[str] = []

            graph_payload = CausalGraphPayloadDTO(
                nodes=causal_nodes,
                edges=causal_edges,
                root_cause_node_ids=root_cause_ids,
                cycle_detected=cycle_detected,
                isolated_node_ids=isolated_ids,
                partition_node_ids=partition_node_ids,
                edge_root_causes=edge_root_causes,
            )

            if request.progress_callback:
                await request.progress_callback(100, 100)

            return EngineExecutionResult(
                results=[],
                hydrated_references={},
                synthesis_output=graph_payload,
                usage=u_p0 + u_p1 + u_link,
            )

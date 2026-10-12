"""Unit and integration test suite for Causal Discovery to TDA Fusion pipeline in DAGExecutor.

Covers the test contracts defined in EPIC 154 Phase 4 and Tier 2 Hardening:
- transform_causal_nodes_to_atoms transformations and boundary conditions
- Causal data starvation Fail-Fast (CAUSAL_DISCOVERY_DATA_STARVATION)
- Missing upstream step validation Fail-Fast (VALIDATION_FAILED)
- Upstream causal graph resolution and global_context_vars.shuffled_atoms injection
- Fair scoring deduplication and identity arithmetic
- Prescriptive remediation root cause analysis
- Anti-fluff cohesion auditing
- Standalone causal workflow scoring hook separation
- Evaluative matrices context updates and extracted data scoring
- Blocked step cascading failure in wave execution
- Input delta model serialization variants
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.core.hook_registry import HookDeltaDTO, HookResult
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionStepState, FrozenContext
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.matrix import FlattenedAtom
from backend_v2.models.domain.step import StepRule
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.atom_result import AtomResultDTO, ExtractedValueDTO
from backend_v2.models.dtos.causal_discovery import (
    CausalEdgeDTO,
    CausalGraphPayloadDTO,
    CausalNodeDTO,
    FairScoringBreakdownDTO,
)
from backend_v2.models.dtos.hook_delta import PassivityDetectionResultDTO
from backend_v2.models.dtos.hook_state import ExecutionInputsDTO
from backend_v2.models.dtos.node_execution import StepOutputContentDTO
from backend_v2.models.dtos.trace import TraceEventMetadataDTO
from backend_v2.models.enums import ExecutionStatus, HistoricalContextMode
from backend_v2.models.state import TraceEvent
from backend_v2.services.execution import create_execution_record
from backend_v2.services.orchestrator.dag_executor import (
    DAGExecutor,
    compute_causal_tda_fusion_result,
    transform_causal_nodes_to_atoms,
)
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository

# ---------------------------------------------------------------------------
# Test Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_repo() -> InMemoryUnifiedWorkflowRepository:
    """Provides an in-memory repository seeded with blueprint step definitions.

    Returns:
        InMemoryUnifiedWorkflowRepository instance.
    """
    repo = InMemoryUnifiedWorkflowRepository()
    repo.seed_raw_step(
        "blp_1111222233334444",
        {
            "id": "blp_1111222233334444",
            "type": "causal_discovery",
            "slug": "causal_step",
            "name": {"translations": {"en": "Causal Discovery Step"}},
            "description": {"translations": {"en": "Exploratory Causal Graph"}},
            "engine_type": "causal_discovery",
            "cognitive_tier": "fast",
            "extraction_protocol_block_id": "blk_1111222233334444",
            "post_hooks": [],
        },
    )
    repo.seed_raw_step(
        "blp_5555666677778888",
        {
            "id": "blp_5555666677778888",
            "type": "llm",
            "slug": "tda_step",
            "name": {"translations": {"en": "TDA Fusion Step"}},
            "description": {"translations": {"en": "Downstream TDA Evaluation"}},
            "engine_type": "tda",
            "criteria_block_ids": ["blk_5555666677778888"],
            "extraction_protocol_block_id": "blk_1111222233334444",
            "post_hooks": ["apply_scoring_logic_hook"],
        },
    )
    return repo


@pytest.fixture
def mock_compiler() -> Any:
    """Provides a mocked prompt compiler.

    Returns:
        MagicMock instance for prompt compilation.
    """
    return MagicMock()


# ---------------------------------------------------------------------------
# Contract 1: Positive transformation to FlattenedAtom instances
# ---------------------------------------------------------------------------


def test_causal_to_tda_fusion_transforms_nodes_to_flattened_atoms() -> None:
    """Verifies transform_causal_nodes_to_atoms converts CausalNodeDTO to FlattenedAtom."""
    nodes = [
        CausalNodeDTO(
            node_id="tda_0000000000000001",
            claim="Higher prices decrease customer demand.",
            source_quote="When prices rose by 10%, volume dropped.",
            paragraph_ref="P1",
            status=ExecutionStatus.PASSED,
            blame_parent_ids=[],
            dependent_child_ids=[],
        ),
        CausalNodeDTO(
            node_id="tda_0000000000000002",
            claim="Lower demand reduces quarterly revenues.",
            source_quote="Revenues contracted following the volume drop.",
            paragraph_ref="P2",
            status=ExecutionStatus.PASSED,
            blame_parent_ids=[],
            dependent_child_ids=[],
        ),
        CausalNodeDTO(
            node_id="tda_0000000000000003",
            claim="Supply chain costs offset revenue gains.",
            source_quote="Freight rate surcharges erased margin gains.",
            paragraph_ref="P3",
            status=ExecutionStatus.FAILED,
            blame_parent_ids=[],
            dependent_child_ids=[],
        ),
    ]

    atoms = transform_causal_nodes_to_atoms(nodes)

    assert len(atoms) == 3
    for node, atom in zip(nodes, atoms, strict=True):
        assert isinstance(atom, FlattenedAtom)
        assert atom.atom_id == node.node_id
        assert atom.question == node.claim
        assert atom.anchor_target == node.paragraph_ref
        assert atom.extraction_rule == node.source_quote
        assert atom.depends_on == ()
        assert atom.acceptance_criteria == ()
        assert atom.anti_patterns == ()
        assert atom.syntactic_anchors == ()


# ---------------------------------------------------------------------------
# Contract 2: Empty list boundary condition
# ---------------------------------------------------------------------------


def test_transform_causal_nodes_empty_list_returns_empty_list() -> None:
    """Verifies transform_causal_nodes_to_atoms cleanly returns an empty list for empty input."""
    atoms = transform_causal_nodes_to_atoms([])
    assert atoms == []


# ---------------------------------------------------------------------------
# Contract 3: None quote and paragraph boundary transformation
# ---------------------------------------------------------------------------


def test_transform_causal_nodes_with_none_quote_transforms_cleanly() -> None:
    """Verifies transform_causal_nodes_to_atoms handles None quote and paragraph references cleanly."""
    node = CausalNodeDTO(
        node_id="tda_0000000000000001",
        claim="Market share expanded without explicit source quote.",
        source_quote=None,
        paragraph_ref=None,
        status=ExecutionStatus.PASSED,
        blame_parent_ids=[],
        dependent_child_ids=[],
    )

    atoms = transform_causal_nodes_to_atoms([node])

    assert len(atoms) == 1
    atom = atoms[0]
    assert atom.atom_id == "tda_0000000000000001"
    assert atom.question == "Market share expanded without explicit source quote."
    assert atom.anchor_target == ""
    assert atom.extraction_rule == ""


# ---------------------------------------------------------------------------
# Contract 4: Data starvation Fail-Fast when upstream produces 0 nodes
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_causal_fusion_starvation_empty_nodes_raises_app_exception(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    mock_compiler: Any,
) -> None:
    """Verifies DAGExecutor raises CAUSAL_DISCOVERY_DATA_STARVATION when upstream nodes are empty."""
    executor = DAGExecutor(
        rag_preflight=AsyncMock(),
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        prompt_block_repo=mock_repo,
        output_profile_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )

    step_causal = StepRule(
        id="stp_1111222233334444",
        task_blueprint="blp_1111222233334444",
        depends_on=[],
    )
    step_tda = StepRule(
        id="stp_5555666677778888",
        task_blueprint="blp_5555666677778888",
        depends_on=["stp_1111222233334444"],
        causal_source_step_id="stp_1111222233334444",
    )

    workflow = Workflow(
        historical_context_mode=HistoricalContextMode.DISABLED,
        id="wf_1111222233334444",
        slug="wf_starvation",
        status="draft",
        version=1,
        default_profile_id="prof_1111222233334444",
        model_registry_id="cfg_model_registry_01",
        name=I18nText(translations={"en": "Starvation Workflow"}),
        description=I18nText(translations={"en": "Starvation Test"}),
        steps=[step_causal, step_tda],
    )

    empty_graph = CausalGraphPayloadDTO(
        nodes=[],
        edges=[],
        root_cause_node_ids=[],
        cycle_detected=False,
        isolated_node_ids=[],
    )

    async def fake_node_execute(*args: Any, **kwargs: Any) -> list[TraceEvent]:
        step_arg = kwargs["step"] if "step" in kwargs else None
        if step_arg and step_arg.id == "stp_1111222233334444":
            return [
                TraceEvent(
                    step_name="stp_1111222233334444",
                    event_type="output",
                    content=empty_graph,
                )
            ]
        return []

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", side_effect=fake_node_execute),
    ):
        mock_hooks.execute = AsyncMock(
            return_value=HookResult(
                success=True,
                state_delta=HookDeltaDTO(delta=ExecutionInputsDTO(raw_inputs={"text": "sample"})),
            )
        )

        with pytest.raises(AppException) as exc_info:
            await executor.execute_workflow(
                execution_id="exe_1111222233334444",
                workflow=workflow,
                raw_inputs=WorkflowInputs(dynamic_inputs={"text": "sample"}),
            )

        assert exc_info.value.details is not None
        assert exc_info.value.details["error_code"] == ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION.value
        assert "0 valid proposition nodes" in exc_info.value.message


# ---------------------------------------------------------------------------
# Contract 5: Missing upstream step reference Fail-Fast
# ---------------------------------------------------------------------------


def test_causal_fusion_missing_upstream_step_raises_app_exception() -> None:
    """Verifies that referencing a causal_source_step_id not in depends_on raises VALIDATION_FAILED."""
    with pytest.raises(AppException) as exc_info:
        StepRule(
            id="stp_5555666677778888",
            task_blueprint="blp_5555666677778888",
            causal_source_step_id="stp_9999999999999999",
            depends_on=[],
        )

    assert exc_info.value.status_code == 422
    assert exc_info.value.details is not None
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "which is not declared in depends_on" in exc_info.value.message


# ---------------------------------------------------------------------------
# Contract 6: Upstream causal graph populates global_context_vars.shuffled_atoms
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_causal_fusion_populates_global_context_vars_shuffled_atoms(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    mock_compiler: Any,
) -> None:
    """Verifies downstream step receives transformed FlattenedAtoms in global_context_vars."""
    executor = DAGExecutor(
        rag_preflight=AsyncMock(),
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        prompt_block_repo=mock_repo,
        output_profile_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )

    step_causal = StepRule(
        id="stp_1111222233334444",
        task_blueprint="blp_1111222233334444",
        depends_on=[],
    )
    step_tda = StepRule(
        id="stp_5555666677778888",
        task_blueprint="blp_5555666677778888",
        depends_on=["stp_1111222233334444"],
        causal_source_step_id="stp_1111222233334444",
    )

    workflow = Workflow(
        historical_context_mode=HistoricalContextMode.DISABLED,
        id="wf_1111222233334444",
        slug="wf_fusion_pop",
        status="draft",
        version=1,
        default_profile_id="prof_1111222233334444",
        model_registry_id="cfg_model_registry_01",
        name=I18nText(translations={"en": "Fusion Pop Workflow"}),
        description=I18nText(translations={"en": "Fusion Pop Test"}),
        steps=[step_causal, step_tda],
    )

    node1 = CausalNodeDTO(
        node_id="tda_0000000000000001",
        claim="Discovered proposition 1",
        source_quote="Quote 1",
        paragraph_ref="P1",
        status=ExecutionStatus.PASSED,
        blame_parent_ids=[],
        dependent_child_ids=["tda_0000000000000002"],
    )
    node2 = CausalNodeDTO(
        node_id="tda_0000000000000002",
        claim="Discovered proposition 2",
        source_quote="Quote 2",
        paragraph_ref="P2",
        status=ExecutionStatus.PASSED,
        blame_parent_ids=["tda_0000000000000001"],
        dependent_child_ids=[],
    )
    valid_graph = CausalGraphPayloadDTO(
        nodes=[node1, node2],
        edges=[CausalEdgeDTO(source_id="tda_0000000000000001", target_id="tda_0000000000000002", reasoning="r1")],
        root_cause_node_ids=["tda_0000000000000001"],
        cycle_detected=False,
        isolated_node_ids=[],
    )

    observed_shuffled_atoms: list[FlattenedAtom] | None = None

    async def fake_node_execute(*args: Any, **kwargs: Any) -> list[TraceEvent]:
        nonlocal observed_shuffled_atoms
        step_arg = kwargs["step"] if "step" in kwargs else None
        if step_arg and step_arg.id == "stp_1111222233334444":
            return [
                TraceEvent(
                    step_name="stp_1111222233334444",
                    event_type="output",
                    content=valid_graph,
                )
            ]
        if step_arg and step_arg.id == "stp_5555666677778888":
            gvars = kwargs["global_context_vars"] if "global_context_vars" in kwargs else None
            if gvars is not None:
                observed_shuffled_atoms = gvars.shuffled_atoms
            return [
                TraceEvent(
                    step_name="stp_5555666677778888",
                    event_type="output",
                    content=AtomResultDTO(
                        tda_id="tda_0000000000000001",
                        status=ExecutionStatus.PASSED,
                        evaluation_reasoning="Validly passed downstream TDA.",
                        source_quote="Quote 1",
                        extensions={},
                        depends_on_tda_ids=[],
                        short_circuit_reason_tda_ids=[],
                    ),
                )
            ]
        return []

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", side_effect=fake_node_execute),
    ):
        mock_hooks.execute = AsyncMock(
            return_value=HookResult(
                success=True,
                state_delta=HookDeltaDTO(delta=ExecutionInputsDTO(raw_inputs={"text": "sample"})),
            )
        )

        record = await executor.execute_workflow(
            execution_id="exe_1111222233334444",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={"text": "sample"}),
        )

        assert record.status == ExecutionStatus.RUNNING
        assert observed_shuffled_atoms is not None
        assert len(observed_shuffled_atoms) == 2
        assert observed_shuffled_atoms[0].atom_id == "tda_0000000000000001"
        assert observed_shuffled_atoms[1].atom_id == "tda_0000000000000002"
        assert record.metadata is not None
        assert record.metadata.global_context_vars is not None
        assert record.metadata.global_context_vars.shuffled_atoms is not None


# ---------------------------------------------------------------------------
# Contract 7: Fair scoring deduplication arithmetic
# ---------------------------------------------------------------------------


def test_fair_scoring_deduplication_applies_dampening() -> None:
    """Verifies fair scoring arithmetic dampens secondary faults and satisfies the mathematical identity."""
    node1 = CausalNodeDTO(
        node_id="tda_0000000000000001",
        claim="Root cause error",
        source_quote="Quote 1",
        paragraph_ref="P1",
        status=ExecutionStatus.FAILED,
        blame_parent_ids=[],
        dependent_child_ids=["tda_0000000000000002"],
    )
    node2 = CausalNodeDTO(
        node_id="tda_0000000000000002",
        claim="Cascading secondary fault",
        source_quote="Quote 2",
        paragraph_ref="P2",
        status=ExecutionStatus.FAILED,
        blame_parent_ids=["tda_0000000000000001"],
        dependent_child_ids=[],
    )
    edge = CausalEdgeDTO(
        source_id="tda_0000000000000001",
        target_id="tda_0000000000000002",
        reasoning="Causal dependency",
    )
    graph = CausalGraphPayloadDTO(
        nodes=[node1, node2],
        edges=[edge],
        root_cause_node_ids=["tda_0000000000000001"],
        cycle_detected=False,
        isolated_node_ids=[],
    )

    fusion = compute_causal_tda_fusion_result(
        graph=graph,
        evaluative_matrices=None,
        evaluated_atoms=None,
        dampening_factor=0.25,
    )

    breakdown = fusion.fair_scoring
    assert breakdown.independent_error_count == 1
    assert breakdown.cascading_fault_count == 1
    assert breakdown.raw_penalty_points == 2.0
    assert breakdown.dampened_savings_points == 0.25
    assert breakdown.deduplicated_penalty_points == 1.75
    assert (
        abs(breakdown.raw_penalty_points - (breakdown.deduplicated_penalty_points + breakdown.dampened_savings_points))
        < 1e-4
    )


# ---------------------------------------------------------------------------
# Contract 8: Fair scoring identity violation raises ValueError
# ---------------------------------------------------------------------------


def test_fair_scoring_identity_violation_raises_value_error() -> None:
    """Verifies FairScoringBreakdownDTO raises ValueError if raw != deduplicated + savings."""
    with pytest.raises(ValueError, match="Scoring identity violated"):
        FairScoringBreakdownDTO(
            raw_penalty_points=10.0,
            deduplicated_penalty_points=6.0,
            dampened_savings_points=2.0,  # 6.0 + 2.0 = 8.0 != 10.0
            cascading_fault_count=2,
            independent_error_count=8,
        )


# ---------------------------------------------------------------------------
# Contract 9: Prescriptive remediation identifies root causes
# ---------------------------------------------------------------------------


def test_prescriptive_remediation_identifies_root_causes() -> None:
    """Verifies prescriptive remediation prioritizes root causes with cascading unlocks."""
    node1 = CausalNodeDTO(
        node_id="tda_0000000000000001",
        claim="Fundamental assumption error",
        source_quote="Quote 1",
        paragraph_ref="P1",
        status=ExecutionStatus.FAILED,
        blame_parent_ids=[],
        dependent_child_ids=["tda_0000000000000002", "tda_0000000000000003"],
    )
    node2 = CausalNodeDTO(
        node_id="tda_0000000000000002",
        claim="Derivative projection 1",
        source_quote="Quote 2",
        paragraph_ref="P2",
        status=ExecutionStatus.FAILED,
        blame_parent_ids=["tda_0000000000000001"],
        dependent_child_ids=[],
    )
    node3 = CausalNodeDTO(
        node_id="tda_0000000000000003",
        claim="Derivative projection 2",
        source_quote="Quote 3",
        paragraph_ref="P3",
        status=ExecutionStatus.FAILED,
        blame_parent_ids=["tda_0000000000000001"],
        dependent_child_ids=[],
    )
    edge1 = CausalEdgeDTO(source_id="tda_0000000000000001", target_id="tda_0000000000000002", reasoning="r1")
    edge2 = CausalEdgeDTO(source_id="tda_0000000000000001", target_id="tda_0000000000000003", reasoning="r2")
    graph = CausalGraphPayloadDTO(
        nodes=[node1, node2, node3],
        edges=[edge1, edge2],
        root_cause_node_ids=["tda_0000000000000001"],
        cycle_detected=False,
        isolated_node_ids=[],
    )

    fusion = compute_causal_tda_fusion_result(graph=graph)

    assert len(fusion.prescriptive_remediations) == 1
    remediation = fusion.prescriptive_remediations[0]
    assert remediation.target_node_id == "tda_0000000000000001"
    assert remediation.unlocks_node_ids == ["tda_0000000000000002", "tda_0000000000000003"]
    assert remediation.potential_score_impact == 3.0


# ---------------------------------------------------------------------------
# Contract 10: Anti-fluff audit identifies isolated concepts
# ---------------------------------------------------------------------------


def test_anti_fluff_audit_identifies_isolated_concepts() -> None:
    """Verifies anti-fluff shield calculates isolated concepts and cohesion score correctly."""
    node1 = CausalNodeDTO(
        node_id="tda_0000000000000001",
        claim="Connected core premise",
        source_quote="Quote 1",
        paragraph_ref="P1",
        status=ExecutionStatus.PASSED,
        blame_parent_ids=[],
        dependent_child_ids=["tda_0000000000000002"],
    )
    node2 = CausalNodeDTO(
        node_id="tda_0000000000000002",
        claim="Connected conclusion",
        source_quote="Quote 2",
        paragraph_ref="P2",
        status=ExecutionStatus.PASSED,
        blame_parent_ids=["tda_0000000000000001"],
        dependent_child_ids=[],
    )
    node3 = CausalNodeDTO(
        node_id="tda_0000000000000003",
        claim="Decorative non-sequitur assertion",
        source_quote="Quote 3",
        paragraph_ref="P3",
        status=ExecutionStatus.PASSED,
        blame_parent_ids=[],
        dependent_child_ids=[],
    )
    edge = CausalEdgeDTO(source_id="tda_0000000000000001", target_id="tda_0000000000000002", reasoning="r1")
    graph = CausalGraphPayloadDTO(
        nodes=[node1, node2, node3],
        edges=[edge],
        root_cause_node_ids=[],
        cycle_detected=False,
        isolated_node_ids=["tda_0000000000000003"],
    )

    fusion = compute_causal_tda_fusion_result(graph=graph)

    fluff = fusion.anti_fluff_audit
    assert fluff.isolated_concept_count == 1
    assert fluff.cycle_detected is False
    assert 0.66 <= fluff.logical_cohesion_score <= 0.67
    assert graph.isolated_node_ids == ["tda_0000000000000003"]


# ---------------------------------------------------------------------------
# Contract 11: Standalone causal workflow omits scoring hook
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_standalone_causal_workflow_omits_scoring_hook(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    mock_compiler: Any,
) -> None:
    """Verifies standalone causal workflow without criteria matrices completes without scoring hook."""
    executor = DAGExecutor(
        rag_preflight=AsyncMock(),
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        prompt_block_repo=mock_repo,
        output_profile_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )

    step_causal = StepRule(
        id="stp_1111222233334444",
        task_blueprint="blp_1111222233334444",
        depends_on=[],
    )

    workflow = Workflow(
        historical_context_mode=HistoricalContextMode.DISABLED,
        id="wf_1111222233334444",
        slug="wf_standalone_causal",
        status="draft",
        version=1,
        default_profile_id="prof_1111222233334444",
        model_registry_id="cfg_model_registry_01",
        name=I18nText(translations={"en": "Standalone Causal Workflow"}),
        description=I18nText(translations={"en": "Standalone Causal Test"}),
        steps=[step_causal],
    )

    graph = CausalGraphPayloadDTO(
        nodes=[
            CausalNodeDTO(
                node_id="tda_0000000000000001",
                claim="Autonomous claim",
                source_quote="Quote",
                paragraph_ref="P1",
                status=ExecutionStatus.PASSED,
                blame_parent_ids=[],
                dependent_child_ids=[],
            )
        ],
        edges=[],
        root_cause_node_ids=[],
        cycle_detected=False,
        isolated_node_ids=["tda_0000000000000001"],
    )

    async def fake_node_execute(*args: Any, **kwargs: Any) -> list[TraceEvent]:
        return [
            TraceEvent(
                step_name="stp_1111222233334444",
                event_type="output",
                content=graph,
            )
        ]

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", side_effect=fake_node_execute),
    ):
        mock_hooks.execute = AsyncMock(
            return_value=HookResult(
                success=True,
                state_delta=HookDeltaDTO(delta=ExecutionInputsDTO(raw_inputs={"text": "sample"})),
            )
        )

        record = await executor.execute_workflow(
            execution_id="exe_1111222233334444",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={"text": "sample"}),
        )

        assert record.status == ExecutionStatus.RUNNING
        for call_args in mock_hooks.execute.call_args_list:
            hook_name = call_args[0][0]
            assert hook_name != "apply_scoring_logic_hook"


# ---------------------------------------------------------------------------
# Tier 2 Hardening Additional Branch Coverage
# ---------------------------------------------------------------------------


def test_compute_causal_tda_fusion_evaluative_matrices_and_extracted_data() -> None:
    """Verify lines 166-170 in compute_causal_tda_fusion_result."""
    node1 = CausalNodeDTO(
        node_id="nod_1111222233334444",
        claim="Claim 1",
        status=ExecutionStatus.PENDING,
        blame_parent_ids=[],
        dependent_child_ids=["nod_2222333344445555"],
        source_quote="Quote 1",
        paragraph_ref="P1",
        tda_score=2.0,
    )
    node2 = CausalNodeDTO(
        node_id="nod_2222333344445555",
        claim="Claim 2",
        status=ExecutionStatus.PENDING,
        blame_parent_ids=["nod_1111222233334444"],
        dependent_child_ids=[],
        source_quote="Quote 2",
        paragraph_ref="P2",
        tda_score=3.0,
    )
    graph = CausalGraphPayloadDTO(nodes=[node1, node2], edges=[])

    atom1 = AtomResultDTO(
        tda_id="nod_1111222233334444",
        matrix_id="mat_1111222233334444",
        status=ExecutionStatus.PASSED,
        source_quote="Quote 1",
        evaluation_reasoning="Valid claim verified",
        extracted_data=ExtractedValueDTO(value=4.8),
        short_circuit_reason_tda_ids=[],
    )
    atom2 = AtomResultDTO(
        tda_id="nod_2222333344445555",
        matrix_id=None,
        status=ExecutionStatus.FAILED,
        evaluation_reasoning="Failed evidence",
        extracted_data=ExtractedValueDTO(value=1.5),
        short_circuit_reason_tda_ids=[],
    )

    res = compute_causal_tda_fusion_result(
        graph=graph,
        evaluative_matrices={"mat_1111222233334444": 4.8},
        evaluated_atoms=[atom1, atom2],
        dampening_factor=0.5,
    )
    assert res is not None
    n1_updated = next(n for n in res.graph.nodes if n.node_id == "nod_1111222233334444")
    n2_updated = next(n for n in res.graph.nodes if n.node_id == "nod_2222333344445555")
    assert n1_updated.tda_score == 4.8
    assert n2_updated.tda_score == 1.5


@pytest.mark.asyncio
async def test_dag_executor_scoring_hook_separation_contract() -> None:
    """Verify lines 465-473 & 721-724 in dag_executor.py."""
    repo = InMemoryUnifiedWorkflowRepository()
    repo.seed_raw_step(
        "blp_1111222233334444",
        {
            "id": "blp_1111222233334444",
            "type": "logic",
            "slug": "causal_step",
            "name": {"translations": {"en": "Causal Step"}},
            "description": {"translations": {"en": "Standalone causal"}},
            "hook": "mock_hook",
            "post_hooks": ["apply_scoring_logic_hook"],
            "criteria_block_ids": [],
        },
    )

    workflow = Workflow(
        historical_context_mode="DISABLED",
        id="wf_1111222233334444",
        slug="wf_causal_slug",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        model_registry_id="cfg_model_registry_01",
        name=I18nText(translations={"en": "Test WF", "fi": "Test WF"}),
        description=I18nText(translations={"en": "Desc", "fi": "Desc"}),
        steps=[
            StepRule(
                id="stp_1111222233334444",
                task_blueprint="blp_1111222233334444",
                expected_sdui_type="markdown",
            )
        ],
    )

    initial_record = create_execution_record(
        execution_id="exe_1111222233334444",
        workflow_id=workflow.id,
        raw_inputs=WorkflowInputs(dynamic_inputs={"doc": "text"}),
        frozen_context=FrozenContext(),
        source_identity_manifest={},
        status=ExecutionStatus.PENDING,
        steps=[],
        step_states={},
    )
    await repo.save_execution(initial_record)

    executor = DAGExecutor(
        rag_preflight=AsyncMock(),
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
        prompt_compiler=MagicMock(),
    )

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", return_value=[]),
    ):
        mock_hooks.execute = AsyncMock(
            return_value=HookResult(
                success=True,
                state_delta=HookDeltaDTO(delta=ExecutionInputsDTO(raw_inputs={"doc": "text"})),
            )
        )
        rec = await executor.execute_workflow(
            execution_id="exe_1111222233334444",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={"doc": "text"}),
        )
        assert rec.status in (ExecutionStatus.PASSED, ExecutionStatus.RUNNING)
        persisted = await repo.get_execution("exe_1111222233334444")
        assert persisted is not None
        assert persisted.step_states["stp_1111222233334444"].status == ExecutionStatus.PASSED


@pytest.mark.asyncio
async def test_dag_executor_blocked_cascading_failure() -> None:
    """Verify lines 993-1006 cascading failure when dependency failed."""
    repo = InMemoryUnifiedWorkflowRepository()
    repo.seed_raw_step(
        "blp_1111222233334444",
        {
            "id": "blp_1111222233334444",
            "type": "logic",
            "slug": "s1",
            "name": {"translations": {"en": "S1"}},
            "description": {"translations": {"en": "D1"}},
            "hook": "mock_hook",
        },
    )
    repo.seed_raw_step(
        "blp_2222333344445555",
        {
            "id": "blp_2222333344445555",
            "type": "logic",
            "slug": "s2",
            "name": {"translations": {"en": "S2"}},
            "description": {"translations": {"en": "D2"}},
            "hook": "mock_hook",
        },
    )

    workflow = Workflow(
        historical_context_mode="DISABLED",
        id="wf_1111222233334444",
        slug="wf_cascade_slug",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        model_registry_id="cfg_model_registry_01",
        name=I18nText(translations={"en": "Test WF", "fi": "Test WF"}),
        description=I18nText(translations={"en": "Desc", "fi": "Desc"}),
        steps=[
            StepRule(id="stp_1111222233334444", task_blueprint="blp_1111222233334444", expected_sdui_type="markdown"),
            StepRule(
                id="stp_2222333344445555",
                task_blueprint="blp_2222333344445555",
                depends_on=["stp_1111222233334444"],
                expected_sdui_type="markdown",
            ),
        ],
    )

    initial_record = create_execution_record(
        execution_id="exe_1111222233334444",
        workflow_id=workflow.id,
        raw_inputs=WorkflowInputs(dynamic_inputs={"doc": "text"}),
        frozen_context=FrozenContext(),
        source_identity_manifest={},
        status=ExecutionStatus.PENDING,
        steps=[],
        step_states={},
    )
    await repo.save_execution(initial_record)

    executor = DAGExecutor(
        rag_preflight=AsyncMock(),
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
        prompt_compiler=MagicMock(),
    )

    async def mock_node_execute(*args: Any, **kwargs: Any) -> list[Any]:
        step = kwargs["step"]
        if step.id == "stp_1111222233334444":
            raise RuntimeError("Step 1 failed")
        return []

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", side_effect=mock_node_execute),
    ):
        mock_hooks.execute = AsyncMock(
            return_value=HookResult(
                success=True,
                state_delta=HookDeltaDTO(delta=ExecutionInputsDTO(raw_inputs={"doc": "text"})),
            )
        )
        with pytest.raises((BaseExceptionGroup, Exception)):
            await executor.execute_workflow(
                execution_id="exe_1111222233334444",
                workflow=workflow,
                raw_inputs=WorkflowInputs(dynamic_inputs={"doc": "text"}),
            )

        persisted = await repo.get_execution("exe_1111222233334444")
        assert persisted is not None
        assert persisted.step_states["stp_1111222233334444"].status == ExecutionStatus.FAILED
        assert persisted.step_states["stp_2222333344445555"].status == ExecutionStatus.BLOCKED


@pytest.mark.asyncio
async def test_dag_executor_causal_step_output_content_and_context_updates() -> None:
    """Verify lines 1044-1060 & 1309-1327 in dag_executor.py."""
    repo = InMemoryUnifiedWorkflowRepository()
    repo.seed_raw_step(
        "blp_1111222233334444",
        {
            "id": "blp_1111222233334444",
            "type": "logic",
            "slug": "causal_source",
            "name": {"translations": {"en": "Causal Source"}},
            "description": {"translations": {"en": "D1"}},
            "hook": "mock_hook",
        },
    )
    repo.seed_raw_step(
        "blp_2222333344445555",
        {
            "id": "blp_2222333344445555",
            "type": "logic",
            "slug": "tda_downstream",
            "name": {"translations": {"en": "TDA Downstream"}},
            "description": {"translations": {"en": "D2"}},
            "hook": "mock_hook",
        },
    )

    workflow = Workflow(
        historical_context_mode="DISABLED",
        id="wf_1111222233334444",
        slug="wf_causal_fusion_slug",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        model_registry_id="cfg_model_registry_01",
        name=I18nText(translations={"en": "Test WF", "fi": "Test WF"}),
        description=I18nText(translations={"en": "Desc", "fi": "Desc"}),
        steps=[
            StepRule(id="stp_1111222233334444", task_blueprint="blp_1111222233334444", expected_sdui_type="markdown"),
            StepRule(
                id="stp_2222333344445555",
                task_blueprint="blp_2222333344445555",
                depends_on=["stp_1111222233334444"],
                causal_source_step_id="stp_1111222233334444",
                expected_sdui_type="markdown",
            ),
        ],
    )

    initial_record = create_execution_record(
        execution_id="exe_1111222233334444",
        workflow_id=workflow.id,
        raw_inputs=WorkflowInputs(dynamic_inputs={"doc": "text"}),
        frozen_context=FrozenContext(),
        source_identity_manifest={},
        status=ExecutionStatus.PENDING,
        steps=[],
        step_states={},
    )
    await repo.save_execution(initial_record)

    executor = DAGExecutor(
        rag_preflight=AsyncMock(),
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
        prompt_compiler=MagicMock(),
    )

    node = CausalNodeDTO(
        node_id="nod_1111222233334444",
        claim="Claim 1",
        status=ExecutionStatus.PENDING,
        blame_parent_ids=[],
        dependent_child_ids=[],
        source_quote="Quote 1",
        paragraph_ref="P1",
        tda_score=2.0,
    )
    graph = CausalGraphPayloadDTO(nodes=[node], edges=[])

    async def mock_node_execute(*args: Any, **kwargs: Any) -> list[Any]:
        step = kwargs["step"]
        if step.id == "stp_1111222233334444":
            return [
                TraceEvent(
                    step_name=step.id,
                    event_type="output",
                    content=StepOutputContentDTO(data=graph.model_dump(mode="json")),
                )
            ]
        else:
            return [
                TraceEvent(
                    step_name=step.id,
                    event_type="decision",
                    metadata=TraceEventMetadataDTO(is_context_update=True),
                    content={"evaluative_matrices": {"mat_x": 4.5}, "passivity_detected": True},
                ),
                TraceEvent(
                    step_name=step.id,
                    event_type="output",
                    content=AtomResultDTO(
                        tda_id="nod_1111222233334444",
                        matrix_id="mat_x",
                        status=ExecutionStatus.PASSED,
                        source_quote="Quote 1",
                        evaluation_reasoning="Passed valid claim",
                        extracted_data=ExtractedValueDTO(value=4.5),
                        short_circuit_reason_tda_ids=[],
                    ),
                ),
            ]

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", side_effect=mock_node_execute),
    ):
        mock_hooks.execute = AsyncMock(
            return_value=HookResult(
                success=True,
                state_delta=HookDeltaDTO(delta=ExecutionInputsDTO(raw_inputs={"doc": "text"})),
            )
        )
        rec = await executor.execute_workflow(
            execution_id="exe_1111222233334444",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={"doc": "text"}),
        )
        assert rec.status in (ExecutionStatus.PASSED, ExecutionStatus.RUNNING)
        persisted = await repo.get_execution("exe_1111222233334444")
        assert persisted is not None
        assert persisted.step_states["stp_2222333344445555"].status == ExecutionStatus.PASSED


@pytest.mark.asyncio
async def test_dag_executor_input_delta_variants() -> None:
    """Verify lines 880-891 delta_content_dict serialization variants."""
    repo = InMemoryUnifiedWorkflowRepository()
    repo.seed_raw_step(
        "blp_1111222233334444",
        {
            "id": "blp_1111222233334444",
            "type": "logic",
            "slug": "s1",
            "name": {"translations": {"en": "S1"}},
            "description": {"translations": {"en": "D1"}},
            "hook": "mock_hook",
        },
    )
    workflow = Workflow(
        historical_context_mode="DISABLED",
        id="wf_1111222233334444",
        slug="wf_delta_slug",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        model_registry_id="cfg_model_registry_01",
        name=I18nText(translations={"en": "Test WF", "fi": "Test WF"}),
        description=I18nText(translations={"en": "Desc", "fi": "Desc"}),
        steps=[
            StepRule(id="stp_1111222233334444", task_blueprint="blp_1111222233334444", expected_sdui_type="markdown"),
        ],
    )
    initial_record = create_execution_record(
        execution_id="exe_1111222233334444",
        workflow_id=workflow.id,
        raw_inputs=WorkflowInputs(dynamic_inputs={"doc": "text"}),
        frozen_context=FrozenContext(),
        source_identity_manifest={},
        status=ExecutionStatus.PENDING,
        steps=[],
        step_states={},
    )
    await repo.save_execution(initial_record)

    executor = DAGExecutor(
        rag_preflight=AsyncMock(),
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
        prompt_compiler=MagicMock(),
    )

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", return_value=[]),
    ):
        # Variant 1: delta is a BaseModel (PassivityDetectionResultDTO)
        mock_hooks.execute = AsyncMock(
            return_value=HookResult(
                success=True,
                state_delta=HookDeltaDTO(delta=PassivityDetectionResultDTO(passivity_detected=True)),
            )
        )
        rec = await executor.execute_workflow(
            execution_id="exe_1111222233334444",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={"doc": "text"}),
        )
        assert rec.status in (ExecutionStatus.PASSED, ExecutionStatus.RUNNING)

        # Variant 2: delta is None
        mock_hooks.execute = AsyncMock(
            return_value=HookResult(
                success=True,
                state_delta=HookDeltaDTO(delta=None),
            )
        )
        rec2 = await executor.execute_workflow(
            execution_id="exe_1111222233334444",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={"doc": "text"}),
        )
        assert rec2.status in (ExecutionStatus.PASSED, ExecutionStatus.RUNNING)


@pytest.mark.asyncio
async def test_dag_executor_causal_step_output_validation_error() -> None:
    """Verify lines 1050-1076 when upstream step output has invalid structure."""
    repo = InMemoryUnifiedWorkflowRepository()
    repo.seed_raw_step(
        "blp_1111222233334444",
        {
            "id": "blp_1111222233334444",
            "type": "logic",
            "slug": "causal_source",
            "name": {"translations": {"en": "Causal Source"}},
            "description": {"translations": {"en": "D1"}},
            "hook": "mock_hook",
        },
    )
    repo.seed_raw_step(
        "blp_2222333344445555",
        {
            "id": "blp_2222333344445555",
            "type": "logic",
            "slug": "tda_downstream",
            "name": {"translations": {"en": "TDA Downstream"}},
            "description": {"translations": {"en": "D2"}},
            "hook": "mock_hook",
        },
    )

    workflow = Workflow(
        historical_context_mode="DISABLED",
        id="wf_1111222233334444",
        slug="wf_causal_fusion_invalid",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        model_registry_id="cfg_model_registry_01",
        name=I18nText(translations={"en": "Test WF", "fi": "Test WF"}),
        description=I18nText(translations={"en": "Desc", "fi": "Desc"}),
        steps=[
            StepRule(id="stp_1111222233334444", task_blueprint="blp_1111222233334444", expected_sdui_type="markdown"),
            StepRule(
                id="stp_2222333344445555",
                task_blueprint="blp_2222333344445555",
                depends_on=["stp_1111222233334444"],
                causal_source_step_id="stp_1111222233334444",
                expected_sdui_type="markdown",
            ),
        ],
    )

    initial_record = create_execution_record(
        execution_id="exe_1111222233334444",
        workflow_id=workflow.id,
        raw_inputs=WorkflowInputs(dynamic_inputs={"doc": "text"}),
        frozen_context=FrozenContext(),
        source_identity_manifest={},
        status=ExecutionStatus.PENDING,
        steps=[],
        step_states={},
    )
    await repo.save_execution(initial_record)

    executor = DAGExecutor(
        rag_preflight=AsyncMock(),
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
        prompt_compiler=MagicMock(),
    )

    async def mock_node_execute(*args: Any, **kwargs: Any) -> list[Any]:
        step = kwargs["step"]
        if step.id == "stp_1111222233334444":
            return [
                TraceEvent(
                    step_name=step.id,
                    event_type="output",
                    content=StepOutputContentDTO(data={"nodes": "invalid_not_a_list"}),
                )
            ]
        return []

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", side_effect=mock_node_execute),
    ):
        mock_hooks.execute = AsyncMock(
            return_value=HookResult(
                success=True,
                state_delta=HookDeltaDTO(delta=ExecutionInputsDTO(raw_inputs={"doc": "text"})),
            )
        )
        with pytest.raises(AppException) as exc_info:
            await executor.execute_workflow(
                execution_id="exe_1111222233334444",
                workflow=workflow,
                raw_inputs=WorkflowInputs(dynamic_inputs={"doc": "text"}),
            )
        assert exc_info.value.details is not None
        assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_dag_executor_causal_snapshot_resolution_and_raw_results() -> None:
    """Verify lines 1079-1084 and 1258-1269 resolution from projector snapshot and raw results dict."""
    repo = InMemoryUnifiedWorkflowRepository()
    repo.seed_raw_step(
        "blp_1111222233334444",
        {
            "id": "blp_1111222233334444",
            "type": "logic",
            "slug": "causal_source",
            "name": {"translations": {"en": "Causal Source"}},
            "description": {"translations": {"en": "D1"}},
            "hook": "mock_hook",
        },
    )
    repo.seed_raw_step(
        "blp_2222333344445555",
        {
            "id": "blp_2222333344445555",
            "type": "logic",
            "slug": "tda_downstream",
            "name": {"translations": {"en": "TDA Downstream"}},
            "description": {"translations": {"en": "D2"}},
            "hook": "mock_hook",
        },
    )

    workflow = Workflow(
        historical_context_mode="DISABLED",
        id="wf_1111222233334444",
        slug="wf_snap_slug",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        model_registry_id="cfg_model_registry_01",
        name=I18nText(translations={"en": "Test WF", "fi": "Test WF"}),
        description=I18nText(translations={"en": "Desc", "fi": "Desc"}),
        steps=[
            StepRule(id="stp_1111222233334444", task_blueprint="blp_1111222233334444", expected_sdui_type="markdown"),
            StepRule(
                id="stp_2222333344445555",
                task_blueprint="blp_2222333344445555",
                depends_on=["stp_1111222233334444"],
                causal_source_step_id="stp_1111222233334444",
                expected_sdui_type="markdown",
            ),
        ],
    )

    initial_record = create_execution_record(
        execution_id="exe_1111222233334444",
        workflow_id=workflow.id,
        raw_inputs=WorkflowInputs(dynamic_inputs={"doc": "text"}),
        frozen_context=FrozenContext(),
        source_identity_manifest={},
        status=ExecutionStatus.PENDING,
        steps=[],
        step_states={},
    )
    await repo.save_execution(initial_record)

    executor = DAGExecutor(
        rag_preflight=AsyncMock(),
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
        prompt_compiler=MagicMock(),
    )

    node = CausalNodeDTO(
        node_id="nod_1111222233334444",
        claim="Claim 1",
        status=ExecutionStatus.PENDING,
        blame_parent_ids=[],
        dependent_child_ids=[],
        source_quote="Quote 1",
        paragraph_ref="P1",
        tda_score=2.0,
    )
    graph = CausalGraphPayloadDTO(nodes=[node], edges=[])

    atom = AtomResultDTO(
        tda_id="nod_1111222233334444",
        matrix_id="mat_x",
        status=ExecutionStatus.PASSED,
        source_quote="Quote 1",
        evaluation_reasoning="Passed valid claim",
        extracted_data=ExtractedValueDTO(value=4.5),
        short_circuit_reason_tda_ids=[],
    )

    async def mock_node_execute(*args: Any, **kwargs: Any) -> list[Any]:
        step = kwargs["step"]
        if step.id == "stp_1111222233334444":
            return [
                TraceEvent(
                    step_name=step.id,
                    event_type="input",
                    content=StepOutputContentDTO(data={"blk_1111222233334444": graph}),
                )
            ]
        else:
            return [
                TraceEvent(
                    step_name=step.id,
                    event_type="output",
                    content={"results": [atom]},
                )
            ]

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", side_effect=mock_node_execute),
    ):
        mock_hooks.execute = AsyncMock(
            return_value=HookResult(
                success=True,
                state_delta=HookDeltaDTO(delta=ExecutionInputsDTO(raw_inputs={"doc": "text"})),
            )
        )
        rec = await executor.execute_workflow(
            execution_id="exe_1111222233334444",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={"doc": "text"}),
        )
        assert rec.status in (ExecutionStatus.PASSED, ExecutionStatus.RUNNING)


@pytest.mark.asyncio
async def test_dag_executor_causal_source_missing_from_steps_by_id() -> None:
    """Verify lines 1012-1021 when causal_source_step_id is not in workflow steps."""
    repo = InMemoryUnifiedWorkflowRepository()
    repo.seed_raw_step(
        "blp_2222333344445555",
        {
            "id": "blp_2222333344445555",
            "type": "logic",
            "slug": "tda_downstream",
            "name": {"translations": {"en": "TDA Downstream"}},
            "description": {"translations": {"en": "D2"}},
            "hook": "mock_hook",
        },
    )

    workflow = Workflow.model_construct(
        historical_context_mode="DISABLED",
        id="wf_1111222233334444",
        slug="wf_missing_source_slug",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        model_registry_id="cfg_model_registry_01",
        name=I18nText(translations={"en": "Test WF", "fi": "Test WF"}),
        description=I18nText(translations={"en": "Desc", "fi": "Desc"}),
        steps=[
            StepRule.model_construct(
                id="stp_2222333344445555",
                task_blueprint="blp_2222333344445555",
                depends_on=[],
                causal_source_step_id="stp_9999888877776666",
                expected_sdui_type="markdown",
            ),
        ],
    )

    initial_record = create_execution_record(
        execution_id="exe_1111222233334444",
        workflow_id=workflow.id,
        raw_inputs=WorkflowInputs(dynamic_inputs={"doc": "text"}),
        frozen_context=FrozenContext(),
        source_identity_manifest={},
        status=ExecutionStatus.PENDING,
        steps=[],
        step_states={},
    )
    await repo.save_execution(initial_record)

    executor = DAGExecutor(
        rag_preflight=AsyncMock(),
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
        prompt_compiler=MagicMock(),
    )

    with patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks:
        mock_hooks.execute = AsyncMock(
            return_value=HookResult(
                success=True,
                state_delta=HookDeltaDTO(delta=ExecutionInputsDTO(raw_inputs={"doc": "text"})),
            )
        )
        with pytest.raises(AppException) as exc_info:
            await executor.execute_workflow(
                execution_id="exe_1111222233334444",
                workflow=workflow,
                raw_inputs=WorkflowInputs(dynamic_inputs={"doc": "text"}),
            )
        assert exc_info.value.status_code == 400
        assert exc_info.value.details is not None
        assert exc_info.value.details["error_code"] in (
            ErrorCodes.VALIDATION_FAILED,
            ErrorCodes.VALIDATION_FAILED.value,
        )


@pytest.mark.asyncio
async def test_dag_executor_causal_upstream_not_passed() -> None:
    """Verify lines 1027-1035 when upstream causal step status is not PASSED."""
    repo = InMemoryUnifiedWorkflowRepository()
    repo.seed_raw_step(
        "blp_1111222233334444",
        {
            "id": "blp_1111222233334444",
            "type": "logic",
            "slug": "causal_up",
            "name": {"translations": {"en": "Causal Up"}},
            "description": {"translations": {"en": "D1"}},
            "hook": "mock_hook",
        },
    )
    repo.seed_raw_step(
        "blp_2222333344445555",
        {
            "id": "blp_2222333344445555",
            "type": "logic",
            "slug": "tda_downstream",
            "name": {"translations": {"en": "TDA Downstream"}},
            "description": {"translations": {"en": "D2"}},
            "hook": "mock_hook",
        },
    )

    workflow = Workflow.model_construct(
        historical_context_mode="DISABLED",
        id="wf_1111222233334444",
        slug="wf_failed_causal_slug",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        model_registry_id="cfg_model_registry_01",
        name=I18nText(translations={"en": "Test WF", "fi": "Test WF"}),
        description=I18nText(translations={"en": "Desc", "fi": "Desc"}),
        steps=[
            StepRule(
                id="stp_1111222233334444",
                task_blueprint="blp_1111222233334444",
                expected_sdui_type="markdown",
            ),
            StepRule.model_construct(
                id="stp_2222333344445555",
                task_blueprint="blp_2222333344445555",
                depends_on=[],
                causal_source_step_id="stp_1111222233334444",
                expected_sdui_type="markdown",
            ),
        ],
    )

    initial_record = create_execution_record(
        execution_id="exe_1111222233334444",
        workflow_id=workflow.id,
        raw_inputs=WorkflowInputs(dynamic_inputs={"doc": "text"}),
        frozen_context=FrozenContext(),
        source_identity_manifest={},
        status=ExecutionStatus.PENDING,
        steps=[],
        step_states={
            "stp_1111222233334444": ExecutionStepState(
                id="stp_1111222233334444", label="Causal Up", status=ExecutionStatus.FAILED
            ),
        },
    )
    await repo.save_execution(initial_record)

    executor = DAGExecutor(
        rag_preflight=AsyncMock(),
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
        prompt_compiler=MagicMock(),
    )

    import asyncio

    async def mock_node_execute(*args: Any, **kwargs: Any) -> list[Any]:
        step = kwargs["step"]
        if step.id == "stp_1111222233334444":
            await asyncio.sleep(0.5)
            return []
        return []

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", side_effect=mock_node_execute),
    ):
        mock_hooks.execute = AsyncMock(
            return_value=HookResult(
                success=True,
                state_delta=HookDeltaDTO(delta=ExecutionInputsDTO(raw_inputs={"doc": "text"})),
            )
        )
        with pytest.raises(AppException) as exc_info:
            await executor.execute_workflow(
                execution_id="exe_1111222233334444",
                workflow=workflow,
                raw_inputs=WorkflowInputs(dynamic_inputs={"doc": "text"}),
            )
        assert exc_info.value.status_code == 500
        assert exc_info.value.details is not None
        assert exc_info.value.details["error_code"] in (
            ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION,
            ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION.value,
        )


@pytest.mark.asyncio
async def test_dag_executor_causal_snapshot_invalid_payload_error() -> None:
    """Verify lines 1108-1115 when snapshot payload fails CausalGraphPayloadDTO validation."""
    repo = InMemoryUnifiedWorkflowRepository()
    repo.seed_raw_step(
        "blp_1111222233334444",
        {
            "id": "blp_1111222233334444",
            "type": "logic",
            "slug": "causal_up",
            "name": {"translations": {"en": "Causal Up"}},
            "description": {"translations": {"en": "D1"}},
            "hook": "mock_hook",
        },
    )
    repo.seed_raw_step(
        "blp_2222333344445555",
        {
            "id": "blp_2222333344445555",
            "type": "logic",
            "slug": "tda_downstream",
            "name": {"translations": {"en": "TDA Downstream"}},
            "description": {"translations": {"en": "D2"}},
            "hook": "mock_hook",
        },
    )

    workflow = Workflow(
        historical_context_mode="DISABLED",
        id="wf_1111222233334444",
        slug="wf_snap_err_slug",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        model_registry_id="cfg_model_registry_01",
        name=I18nText(translations={"en": "Test WF", "fi": "Test WF"}),
        description=I18nText(translations={"en": "Desc", "fi": "Desc"}),
        steps=[
            StepRule(
                id="stp_1111222233334444",
                task_blueprint="blp_1111222233334444",
                expected_sdui_type="markdown",
            ),
            StepRule(
                id="stp_2222333344445555",
                task_blueprint="blp_2222333344445555",
                depends_on=["stp_1111222233334444"],
                causal_source_step_id="stp_1111222233334444",
                expected_sdui_type="markdown",
            ),
        ],
    )

    initial_record = create_execution_record(
        execution_id="exe_1111222233334444",
        workflow_id=workflow.id,
        raw_inputs=WorkflowInputs(dynamic_inputs={"doc": "text"}),
        frozen_context=FrozenContext(),
        source_identity_manifest={},
        status=ExecutionStatus.PENDING,
        steps=[],
        step_states={},
    )
    await repo.save_execution(initial_record)

    executor = DAGExecutor(
        rag_preflight=AsyncMock(),
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
        prompt_compiler=MagicMock(),
    )

    async def mock_node_execute(*args: Any, **kwargs: Any) -> list[Any]:
        step = kwargs["step"]
        if step.id == "stp_1111222233334444":
            return [
                TraceEvent(
                    step_name=step.id,
                    event_type="input",
                    content=StepOutputContentDTO(data={"blk_1111222233334444": "invalid-graph-string"}),
                )
            ]
        return []

    with (
        patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks,
        patch.object(executor.node_executor, "execute", side_effect=mock_node_execute),
    ):
        mock_hooks.execute = AsyncMock(
            return_value=HookResult(
                success=True,
                state_delta=HookDeltaDTO(delta=ExecutionInputsDTO(raw_inputs={"doc": "text"})),
            )
        )
        with pytest.raises(AppException) as exc_info:
            await executor.execute_workflow(
                execution_id="exe_1111222233334444",
                workflow=workflow,
                raw_inputs=WorkflowInputs(dynamic_inputs={"doc": "text"}),
            )
        assert exc_info.value.status_code == 500
        assert exc_info.value.details is not None
        assert exc_info.value.details["error_code"] in (
            ErrorCodes.VALIDATION_FAILED,
            ErrorCodes.VALIDATION_FAILED.value,
        )

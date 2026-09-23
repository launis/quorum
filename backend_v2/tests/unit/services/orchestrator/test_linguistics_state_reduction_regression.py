"""Regression test for LinguisticsResultDTO reduction and variance validation pipeline.

Reproduces the bug where LinguisticsResultDTO was reduced into inputs/global_context_vars
in state_reducer.py without emitting a decision TraceEvent, causing step_linguistics to be
lost from execution_trace and context_variables.json, leading to variance_synthesis returning
(None, None) and VarianceAdapter crashing with HTTP 500:
"Strict Fail-Fast Enforced: 'variance_validation' requested but extension_metrics is missing in cache."
"""

from __future__ import annotations

import pytest

from backend_v2.core.hook_registry import HookState
from backend_v2.exceptions import AppException
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.linguistics import LinguisticsResultDTO, PerformativePatternDTO
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.dtos.global_context import GlobalContextVarsDTO
from backend_v2.models.dtos.hook_delta import HookDeltaDTO
from backend_v2.models.dtos.hook_state import ExecutionInputsDTO
from backend_v2.models.enums import ExecutionStatus, TargetBlockType, XaiExtensionType
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import RenderedSynthesisCache
from backend_v2.services.orchestrator.state_reducer import reduce_hook_delta
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.variance_adapter import VarianceAdapter


def _build_test_hook_state(step_id: str = "sr_f0a26d17cc9b48a7") -> HookState:
    """Build a standard HookState for testing."""
    return HookState(
        execution_id="exe_test_linguistics_001",
        workflow_id="wf_9d68c573802341db",
        step_id=step_id,
        metadata=ExecutionMetadata(matrix_sampling_strategy=10, workflow_version=1),
        global_context_vars=GlobalContextVarsDTO(language="fi"),
        inputs=ExecutionInputsDTO(raw_inputs={"product_text": "sample text", "chat_log": "sample log"}),
    )


def test_reduce_hook_delta_linguistics_must_emit_decision_trace_event() -> None:
    """RED TEST: reduce_hook_delta MUST emit a decision TraceEvent for LinguisticsResultDTO.

    Without this event, dag_executor does not update execution.context_variables and
    execution_trace lacks the decision event, causing step_linguistics to be discarded.
    """
    state = _build_test_hook_state(step_id="sr_f0a26d17cc9b48a7")
    pat = PerformativePatternDTO(
        pattern_id="ptrn_test01",
        detected_phrase="luonnollisesti",
        category="performative_filler",
    )
    ling_dto = LinguisticsResultDTO(
        performative_patterns=[pat],
        total_word_count=120,
    )
    delta_dto = HookDeltaDTO(delta=ling_dto)

    new_state, emitted_events = reduce_hook_delta(state, delta_dto, step_id="sr_f0a26d17cc9b48a7")

    # In current buggy code, emitted_events is []
    # This assertion EXPECTS emitted_events to contain the decision event for context updates!
    assert len(emitted_events) == 1, (
        f"Expected exactly 1 decision TraceEvent for LinguisticsResultDTO, but got {len(emitted_events)}. "
        "LinguisticsResultDTO reduction must emit a TraceEvent with is_context_update=True so that "
        "dag_executor commits step_linguistics into execution.context_variables and execution_trace."
    )

    evt = emitted_events[0]
    assert evt.event_type == "decision"
    assert evt.step_name == "sr_f0a26d17cc9b48a7"
    assert evt.metadata == {"is_context_update": True}
    assert isinstance(evt.content, dict)
    assert "step_linguistics" in evt.content
    assert evt.content["step_linguistics"]["total_word_count"] == 120
    assert len(evt.content["step_linguistics"]["performative_patterns"]) == 1


def test_variance_adapter_crashes_when_extension_metrics_missing() -> None:
    """Proves the exact crash site in VarianceAdapter when extension_metrics is None."""
    prof = OutputProfile(
        id="prf_5d6e7f8091a2b3c4",
        slug="holistic_audit",
        workflow_id="wf_9d68c573802341db",
        name=I18nText(translations={"en": "Holistic Audit", "fi": "Kokonaisvaltainen Auditointi"}),
        visible_workflow_extensions=[XaiExtensionType.VARIANCE_VALIDATION],
        variance_target_block="blk_53f32679aa514fcb",
        variance_synthesis_directive="Synthesize cognitive variance.",
        target_block_order=[TargetBlockType.VARIANCE_VALIDATION_BLOCK],
    )
    rec = ExecutionRecord(
        id="exe_b3bd261ce76e41d0",
        workflow_id="wf_9d68c573802341db",
        output_profile_id="prf_5d6e7f8091a2b3c4",
        status=ExecutionStatus.PASSED,
        target_locale="fi",
        metadata=ExecutionMetadata(),
        execution_trace=[],
        context_variables={},
    )
    # Cache with extension_metrics=None (as produced by synthesis_worker when metrics missing)
    cache = RenderedSynthesisCache(extension_metrics=None)
    context = AdapterContext(
        execution=rec,
        locale="fi",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=prof,
        profile_cache=cache,
        user_name=None,
        org_name=None,
        parsed_matrices={},
    )

    with pytest.raises(AppException) as exc_info:
        VarianceAdapter.build(context)

    assert exc_info.value.status_code == 500
    assert (
        "Strict Fail-Fast Enforced: 'variance_validation' requested but extension_metrics is missing in cache."
        in exc_info.value.message
    )


def test_reduce_hook_delta_linguistics_boundary_empty_and_none_gvars() -> None:
    """Boundary test: LinguisticsResultDTO with 0 word count, empty patterns, and None global_context_vars.

    Verifies:
    1. HookState with global_context_vars=None correctly instantiates GlobalContextVarsDTO(step_linguistics=delta).
    2. Zero word count and empty performative_patterns correctly emit a decision TraceEvent.
    """
    state_empty_gvars = HookState(
        execution_id="exe_test_boundary_001",
        workflow_id="wf_9d68c573802341db",
        step_id="sr_test_boundary",
        metadata=ExecutionMetadata(matrix_sampling_strategy=10, workflow_version=1),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(raw_inputs={"text": "none"}),
    )
    ling_dto = LinguisticsResultDTO(
        performative_patterns=[],
        total_word_count=0,
    )
    delta_dto = HookDeltaDTO(delta=ling_dto)

    new_state, emitted_events = reduce_hook_delta(state_empty_gvars, delta_dto, step_id="sr_test_boundary")

    assert len(emitted_events) == 1
    evt = emitted_events[0]
    assert evt.event_type == "decision"
    assert evt.step_name == "sr_test_boundary"
    assert evt.metadata == {"is_context_update": True}
    assert evt.content["step_linguistics"]["total_word_count"] == 0
    assert evt.content["step_linguistics"]["performative_patterns"] == []

    assert new_state.global_context_vars is not None
    assert new_state.global_context_vars.step_linguistics == ling_dto
    assert new_state.inputs.dynamic_inputs["step_linguistics"] == ling_dto

    # Partition 2: global_context_vars is explicitly None (via model_construct)
    state_none_gvars = HookState.model_construct(
        execution_id="exe_test_boundary_002",
        workflow_id="wf_9d68c573802341db",
        step_id="sr_test_boundary_2",
        metadata=ExecutionMetadata(matrix_sampling_strategy=10, workflow_version=1),
        global_context_vars=None,
        inputs=ExecutionInputsDTO(raw_inputs={"text": "none"}),
    )
    new_state_none, events_none = reduce_hook_delta(state_none_gvars, delta_dto, step_id="sr_test_boundary_2")
    assert len(events_none) == 1
    assert new_state_none.global_context_vars is not None
    assert new_state_none.global_context_vars.step_linguistics == ling_dto

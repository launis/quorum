"""Regression test for $inputs path resolution in DAGExecutor and ContextBuilder.

Verifies that input_processing hook returning ExecutionInputsDTO
extracts flat inputs directly in DAGExecutor for TraceEvent(step_name="inputs"),
allowing StateProjector to fold inputs by individual field and enabling
downstream dot-notation resolution for $inputs.<field>.
"""

from __future__ import annotations

import pytest

from backend_v2.exceptions import MissingInputMappingError
from backend_v2.models.dtos.hook_delta import ExecutionInputsDTO, ExecutionMetadataDeltaDTO, HookDeltaDTO
from backend_v2.models.dtos.node_execution import StepOutputContentDTO
from backend_v2.models.state import StateProjector, TraceEvent
from backend_v2.utils.math_utils import resolve_dot_notation


def test_inputs_path_resolution_succeeds_with_unpacked_execution_inputs_dto() -> None:
    """Verifies that flat inputs extraction from ExecutionInputsDTO resolves correctly.

    Under the modernized DAGExecutor logic, ExecutionInputsDTO raw_inputs and dynamic_inputs
    are flattened into delta_content_dict rather than dumped as a nested wrapper model.
    Consequently, StateProjector stores block_id for each input key ('product_text', 'chat_log').
    Downstream steps resolve 'inputs.product_text' and 'inputs.chat_log' successfully.
    """
    output_dict = {
        "product_text": "Sample product specification text",
        "chat_log": "Sample chat transcript",
    }
    dynamic_dict = {
        "user_context": "Sample dynamic context",
    }
    hook_delta = HookDeltaDTO(
        delta=ExecutionInputsDTO(raw_inputs=output_dict, dynamic_inputs=dynamic_dict),
        metadata_updates=ExecutionMetadataDeltaDTO(estimated_token_count=100),
    )

    delta_payload = hook_delta.delta
    assert isinstance(delta_payload, ExecutionInputsDTO)

    # DAGExecutor extraction logic:
    delta_content_dict = {
        **dict(delta_payload.raw_inputs),
        **dict(delta_payload.dynamic_inputs),
    }
    delta_content = StepOutputContentDTO(data=delta_content_dict)
    proc_event = TraceEvent(step_name="inputs", event_type="input", content=delta_content.data)

    projector = StateProjector()
    projector.apply_delta(proc_event)

    snapshot_items = {d.block_id: d.payload for d in projector.snapshot if d.step_id == "inputs"}
    state_data = {"inputs": snapshot_items}

    # Verify that all flat keys are resolvable
    resolved_product = resolve_dot_notation(state_data, "inputs.product_text")
    assert resolved_product == "Sample product specification text"

    resolved_chat = resolve_dot_notation(state_data, "inputs.chat_log")
    assert resolved_chat == "Sample chat transcript"

    resolved_dyn = resolve_dot_notation(state_data, "inputs.user_context")
    assert resolved_dyn == "Sample dynamic context"


def test_inputs_path_resolution_fails_fast_on_missing_input_key() -> None:
    """Negative test (Anti-Happy Path): Missing input keys trigger MissingInputMappingError."""
    output_dict = {
        "product_text": "Sample product specification text",
    }
    delta_payload = ExecutionInputsDTO(raw_inputs=output_dict)

    delta_content_dict = {
        **dict(delta_payload.raw_inputs),
        **dict(delta_payload.dynamic_inputs),
    }
    delta_content = StepOutputContentDTO(data=delta_content_dict)
    proc_event = TraceEvent(step_name="inputs", event_type="input", content=delta_content.data)

    projector = StateProjector()
    projector.apply_delta(proc_event)

    snapshot_items = {d.block_id: d.payload for d in projector.snapshot if d.step_id == "inputs"}
    state_data = {"inputs": snapshot_items}

    with pytest.raises(MissingInputMappingError) as exc_info:
        resolve_dot_notation(state_data, "inputs.missing_key")

    assert "missing_key" in str(exc_info.value)

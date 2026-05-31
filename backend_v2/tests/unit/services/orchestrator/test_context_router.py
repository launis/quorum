import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.dtos.lightweight_matrix import OutputProfileConfig
from backend_v2.models.enums import XaiExtensionType
from backend_v2.models.state import StepOutputDTO
from backend_v2.services.orchestrator.context_router import ContextRouter


def test_normalize_and_validate_variable_legacy_output_rejected() -> None:
    # Epic 43: State must be a list of StepOutputDTOs under the 'steps' key
    snapshot = {"steps": [StepOutputDTO(step_id="step_1", block_id="b", data_type="text", payload={})]}
    path = "$steps.step_1.output"

    # It should strictly reject legacy .output with a 400 error
    with pytest.raises(AppException) as exc_info:
        ContextRouter.normalize_and_validate_variable(path, snapshot)

    assert "Legacy V1 '.output' variable format is strictly forbidden." in str(exc_info.value)
    assert exc_info.value.status_code == 400


def test_normalize_and_validate_variable_orphaned_step() -> None:
    snapshot = {"steps": [StepOutputDTO(step_id="step_2", block_id="b", data_type="text", payload={})]}
    path = "$steps.step_1.output"

    # It should fail-fast since step_1 is not in snapshot
    with pytest.raises(AppException) as exc_info:
        ContextRouter.normalize_and_validate_variable(path, snapshot)

    assert "Fail-Fast: Required step 'step_1' not found in state (Orphaned Step)." in str(exc_info.value)
    assert exc_info.value.status_code == 500


def test_normalize_and_validate_variable_no_output_suffix() -> None:
    snapshot = {"steps": [StepOutputDTO(step_id="step_1", block_id="b", data_type="text", payload={})]}
    path = "$steps.step_1.some_data"

    # Should validate and not strip because it's not .output
    result = ContextRouter.normalize_and_validate_variable(path, snapshot)
    assert result == "$steps.step_1.some_data"


def test_normalize_and_validate_variable_nested_output_rejected() -> None:
    snapshot = {"steps": [StepOutputDTO(step_id="step_1", block_id="b", data_type="text", payload={})]}
    path = "$steps.step_1.output.nested_key"

    # It should strictly reject legacy .output with a 400 error even if nested
    with pytest.raises(AppException) as exc_info:
        ContextRouter.normalize_and_validate_variable(path, snapshot)

    assert "Legacy V1 '.output' variable format is strictly forbidden." in str(exc_info.value)
    assert exc_info.value.status_code == 400


def test_normalize_and_validate_variable_inputs_path() -> None:
    snapshot = {"raw_inputs": {"doc": "123"}}
    path = "$inputs.doc"

    # Non-steps path should be returned unchanged
    result = ContextRouter.normalize_and_validate_variable(path, snapshot)
    assert result == "$inputs.doc"


def test_route_and_prune_bypasses_variance_validation() -> None:
    # Set up an output profile that demands 'variance_validation'
    output_profile = OutputProfileConfig(
        visible_extensions=[
            XaiExtensionType.FALSIFICATION,
            XaiExtensionType.VARIANCE_VALIDATION,
        ]
    )

    # Trace event that contains falsification but NOT variance_validation
    trace_event = {
        "raw_score": 3.0,
        "normalized_score": 100.0,
        "justification": "Test justification",
        "extensions": {"falsification": "Some falsification evidence"},
    }

    # This should succeed because variance_validation is a global extension
    # and should be bypassed during local matrix trace pruning.
    pruned = ContextRouter.route_and_prune(trace_event, output_profile)

    assert pruned.raw_score == 3.0
    assert "falsification" in pruned.extensions
    assert "variance_validation" not in pruned.extensions

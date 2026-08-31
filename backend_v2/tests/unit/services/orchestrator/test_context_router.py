import pytest

from backend_v2.exceptions import (
    AppException,
    ConfigurationError,
    MissingRoutingModeError,
)
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


def test_route_and_prune_strictly_follows_block_extensions() -> None:
    # Output profile demands ONLY falsification at the block level.
    # variance_validation is a workflow extension, so it's handled elsewhere.
    output_profile = OutputProfileConfig(
        visible_block_extensions=[XaiExtensionType.FALSIFICATION],
        visible_workflow_extensions=[XaiExtensionType.VARIANCE_VALIDATION],
    )

    trace_event = {
        "raw_score": 3.0,
        "normalized_score": 100.0,
        "justification": "Test justification",
        "evaluated_atoms": {},
        "extensions": {"falsification": "Some falsification evidence"},
    }

    # Should only prune based on visible_block_extensions and succeed
    pruned = ContextRouter.route_and_prune(trace_event, output_profile)

    assert pruned.raw_score == 3.0
    assert "falsification" in pruned.extensions
    assert "variance_validation" not in pruned.extensions


def test_route_and_prune_with_allowed_extensions() -> None:
    # Output profile requires falsification, coaching AND emotional_sentiment
    output_profile = OutputProfileConfig(
        visible_block_extensions=[
            XaiExtensionType.FALSIFICATION,
            XaiExtensionType.COACHING,
            XaiExtensionType.EMOTIONAL_SENTIMENT,
        ],
        visible_workflow_extensions=[],
    )

    # The block ONLY allows Falsification and Coaching. Sentiment is not supported by this block.
    trace_event = {
        "raw_score": 4.0,
        "normalized_score": 80.0,
        "justification": "Block logic.",
        "evaluated_atoms": {},
        "extensions": {
            "falsification": "Valid falsification",
            "coaching": "Good coaching insight",
        },
        "allowed_extensions": [
            XaiExtensionType.FALSIFICATION,
            XaiExtensionType.COACHING,
        ],
    }

    # 1. Success case: emotional_sentiment is required by output_profile, but not allowed by this block.
    # Therefore, prune should skip it and succeed!
    pruned = ContextRouter.route_and_prune(trace_event, output_profile)
    assert pruned.raw_score == 4.0
    assert "falsification" in pruned.extensions
    assert "coaching" in pruned.extensions
    assert "emotional_sentiment" not in pruned.extensions

    # 2. Failure case: coaching is in allowed_extensions, but missing from extensions.
    # It must gracefully skip the extension instead of raising an error or inserting a fallback!
    trace_event_missing = {
        "raw_score": 4.0,
        "normalized_score": 80.0,
        "justification": "Block logic.",
        "evaluated_atoms": {},
        "extensions": {
            "falsification": "Valid falsification",
        },
        "allowed_extensions": [
            XaiExtensionType.FALSIFICATION,
            XaiExtensionType.COACHING,
        ],
    }

    pruned_missing = ContextRouter.route_and_prune(trace_event_missing, output_profile)
    assert pruned_missing.raw_score == 4.0
    assert "falsification" in pruned_missing.extensions
    assert "coaching" not in pruned_missing.extensions


def test_route_and_prune_success() -> None:
    """Test successful pruning of a trace event."""
    from backend_v2.models.enums import ExecutionStatus

    trace_event = {
        "normalized_score": 85.0,
        "level_breakdown": {"4.0": {"hits": 1, "total": 1}},
        "justification": "Good logic.",
        "evaluated_atoms": {"atom_1": ExecutionStatus.PASSED, "atom_2": ExecutionStatus.FAILED},
        "extensions": {
            XaiExtensionType.CITATION: "Source A",
            XaiExtensionType.COACHING: "Improve here.",
            "falsification": "No issues found.",
        },
    }

    output_profile = OutputProfileConfig(
        visible_block_extensions=[XaiExtensionType.CITATION, XaiExtensionType.FALSIFICATION],
        visible_workflow_extensions=[],
    )

    result = ContextRouter.route_and_prune(trace_event, output_profile)

    assert result.normalized_score == 85.0
    assert result.level_breakdown == {"4.0": {"hits": 1, "total": 1}}
    assert result.justification == "Good logic."
    assert result.evaluated_atoms == {"atom_1": ExecutionStatus.PASSED, "atom_2": ExecutionStatus.FAILED}

    # Extensions should ONLY contain the requested ones, and handle Enum vs string keys
    assert len(result.extensions) == 2
    assert result.extensions[XaiExtensionType.CITATION] == "Source A"
    assert result.extensions[XaiExtensionType.FALSIFICATION] == "No issues found."


def test_route_and_prune_missing_profile() -> None:
    """Test that all extensions are returned when output profile is missing."""
    trace_event = {
        "normalized_score": 50.0,
        "level_breakdown": {"2.0": {"hits": 1, "total": 1}},
        "justification": "Test",
        "evaluated_atoms": {},
        "extensions": {"falsification": "Some falsification"},
    }

    result = ContextRouter.route_and_prune(trace_event, None)
    assert result.extensions[XaiExtensionType.FALSIFICATION] == "Some falsification"


def test_route_and_prune_missing_base_field() -> None:
    """Test that ConfigurationError is raised when a base field is missing."""
    trace_event = {
        "normalized_score": 50.0,
        "level_breakdown": {"2.0": {"hits": 1, "total": 1}},
        "justification": "Test",
        # evaluated_atoms is missing
        "extensions": {},
    }

    output_profile = OutputProfileConfig(visible_block_extensions=[], visible_workflow_extensions=[])

    with pytest.raises(ConfigurationError) as exc_info:
        ContextRouter.route_and_prune(trace_event, output_profile)

    assert "Missing required base field" in exc_info.value.message


def test_route_and_prune_missing_extension() -> None:
    """Test that missing required extensions are gracefully skipped."""
    trace_event = {
        "normalized_score": 50.0,
        "level_breakdown": {"2.0": {"hits": 1, "total": 1}},
        "justification": "Test",
        "evaluated_atoms": {},
        "extensions": {XaiExtensionType.CITATION: "Source A"},
    }

    # We require COACHING, but it's not in the trace
    output_profile = OutputProfileConfig(
        visible_block_extensions=[XaiExtensionType.CITATION, XaiExtensionType.COACHING], visible_workflow_extensions=[]
    )

    pruned = ContextRouter.route_and_prune(trace_event, output_profile)

    assert pruned.extensions[XaiExtensionType.CITATION] == "Source A"
    assert XaiExtensionType.COACHING not in pruned.extensions


def test_validate_routing_mode_success() -> None:
    """Test successful validation of routing mode."""
    mapping_config = {"routing_mode": "strict_booleans_only", "other_key": "value"}
    result = ContextRouter.validate_routing_mode("$steps.step_A", mapping_config)
    assert result == "strict_booleans_only"


def test_validate_routing_mode_missing() -> None:
    """Test that MissingRoutingModeError is raised when routing mode is missing."""
    mapping_config = {"other_key": "value"}
    with pytest.raises(MissingRoutingModeError) as exc_info:
        ContextRouter.validate_routing_mode("$steps.step_A", mapping_config)

    assert exc_info.value.details["mapping_path"] == "$steps.step_A"


def test_normalize_and_validate_variable_empty_path() -> None:
    """Test that empty or falsy path is returned as is."""
    assert ContextRouter.normalize_and_validate_variable("", {}) == ""


def test_normalize_and_validate_variable_invalid_snapshot_state() -> None:
    """Test that invalid snapshot structure raises AppException."""
    with pytest.raises(AppException) as exc_info:
        ContextRouter.normalize_and_validate_variable("$steps.step_1", "not_a_valid_snapshot_structure")

    assert "Snapshot validation failed" in exc_info.value.message
    assert exc_info.value.status_code == 500


def test_normalize_and_validate_variable_legacy_dict_steps() -> None:
    """Test that legacy dict structure for steps in snapshot is rejected."""
    # When steps is a dict inside the snapshot dictionary
    legacy_snapshot = {"steps": {"step_1": {"data": 123}}}
    with pytest.raises(AppException) as exc_info:
        ContextRouter.normalize_and_validate_variable("$steps.step_1", legacy_snapshot)

    assert (
        "Snapshot validation failed" in exc_info.value.message
        or "Legacy dictionary state detected" in exc_info.value.message
    )


def test_route_and_prune_validation_error() -> None:
    """Test that invalid trace_event format raises ConfigurationError."""
    invalid_trace = {
        "raw_score": "not_a_number",
        "normalized_score": 100.0,
        "justification": "Test",
        "evaluated_atoms": {},
    }
    output_profile = OutputProfileConfig(visible_block_extensions=[], visible_workflow_extensions=[])
    with pytest.raises(ConfigurationError) as exc_info:
        ContextRouter.route_and_prune(invalid_trace, output_profile)

    assert "Fail-Fast: Invalid trace_event format" in exc_info.value.message

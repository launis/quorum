import pytest

from backend_v2.exceptions import (
    AppException,
    ConfigurationError,
    MissingRoutingModeError,
    MissingXaiExtensionError,
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
        "evaluated_atoms": {},
        "extensions": {"falsification": "Some falsification evidence"},
    }

    # This should succeed because variance_validation is a global extension
    # and should be bypassed during local matrix trace pruning.
    pruned = ContextRouter.route_and_prune(trace_event, output_profile)

    assert pruned.raw_score == 3.0
    assert "falsification" in pruned.extensions
    assert "variance_validation" not in pruned.extensions


def test_route_and_prune_with_allowed_extensions() -> None:
    from backend_v2.exceptions import MissingXaiExtensionError

    # Output profile requires falsification, coaching AND emotional_sentiment
    output_profile = OutputProfileConfig(
        visible_extensions=[
            XaiExtensionType.FALSIFICATION,
            XaiExtensionType.COACHING,
            XaiExtensionType.EMOTIONAL_SENTIMENT,
        ]
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
    # It must strictly raise MissingXaiExtensionError!
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

    with pytest.raises(MissingXaiExtensionError) as exc_info:
        ContextRouter.route_and_prune(trace_event_missing, output_profile)

    assert exc_info.value.details["extension"] == str(XaiExtensionType.COACHING)


def test_route_and_prune_success():
    """Test successful pruning of a trace event."""
    trace_event = {
        "normalized_score": 85.0,
        "level_breakdown": {"4.0": {"hits": 1, "total": 1}},
        "justification": "Good logic.",
        "evaluated_atoms": {"atom_1": True, "atom_2": False},
        "extensions": {
            XaiExtensionType.CITATION: "Source A",
            XaiExtensionType.COACHING: "Improve here.",
            "falsification": "No issues found."
        }
    }
    
    output_profile = OutputProfileConfig(
        visible_extensions=[XaiExtensionType.CITATION, XaiExtensionType.FALSIFICATION]
    )
    
    result = ContextRouter.route_and_prune(trace_event, output_profile)
    
    assert result.normalized_score == 85.0
    assert result.level_breakdown == {"4.0": {"hits": 1, "total": 1}}
    assert result.justification == "Good logic."
    assert result.evaluated_atoms == {"atom_1": True, "atom_2": False}
    
    # Extensions should ONLY contain the requested ones, and handle Enum vs string keys
    assert len(result.extensions) == 2
    assert result.extensions[XaiExtensionType.CITATION] == "Source A"
    assert result.extensions[XaiExtensionType.FALSIFICATION] == "No issues found."


def test_route_and_prune_missing_profile():
    """Test that all extensions are returned when output profile is missing."""
    trace_event = {
        "normalized_score": 50.0,
        "level_breakdown": {"2.0": {"hits": 1, "total": 1}},
        "justification": "Test",
        "evaluated_atoms": {},
        "extensions": {"falsification": "Some falsification"}
    }
    
    result = ContextRouter.route_and_prune(trace_event, None)
    assert result.extensions["falsification"] == "Some falsification"


def test_route_and_prune_missing_base_field():
    """Test that ConfigurationError is raised when a base field is missing."""
    trace_event = {
        "normalized_score": 50.0,
        "level_breakdown": {"2.0": {"hits": 1, "total": 1}},
        "justification": "Test",
        # evaluated_atoms is missing
        "extensions": {}
    }
    
    output_profile = OutputProfileConfig(visible_extensions=[])
    
    with pytest.raises(ConfigurationError) as exc_info:
        ContextRouter.route_and_prune(trace_event, output_profile)
    
    assert "Missing required base field" in exc_info.value.message


def test_route_and_prune_missing_extension():
    """Test that MissingXaiExtensionError is raised when a required extension is missing."""
    trace_event = {
        "normalized_score": 50.0,
        "level_breakdown": {"2.0": {"hits": 1, "total": 1}},
        "justification": "Test",
        "evaluated_atoms": {},
        "extensions": {
            XaiExtensionType.CITATION: "Source A"
        }
    }
    
    # We require COACHING, but it's not in the trace
    output_profile = OutputProfileConfig(
        visible_extensions=[XaiExtensionType.CITATION, XaiExtensionType.COACHING]
    )
    
    with pytest.raises(MissingXaiExtensionError) as exc_info:
        ContextRouter.route_and_prune(trace_event, output_profile)
    
    assert exc_info.value.details["extension"] == str(XaiExtensionType.COACHING)


def test_validate_routing_mode_success():
    """Test successful validation of routing mode."""
    mapping_config = {"routing_mode": "strict_booleans_only", "other_key": "value"}
    result = ContextRouter.validate_routing_mode("$steps.step_A", mapping_config)
    assert result == "strict_booleans_only"


def test_validate_routing_mode_missing():
    """Test that MissingRoutingModeError is raised when routing mode is missing."""
    mapping_config = {"other_key": "value"}
    with pytest.raises(MissingRoutingModeError) as exc_info:
        ContextRouter.validate_routing_mode("$steps.step_A", mapping_config)
    
    assert exc_info.value.details["mapping_path"] == "$steps.step_A"

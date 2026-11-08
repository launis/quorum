"""Unit tests for ContextRouter variable normalization and XAI extension pruning."""

from __future__ import annotations

from typing import Any

import pytest

from backend_v2.exceptions import (
    AppException,
    ConfigurationError,
    MissingRoutingModeError,
)
from backend_v2.models.dtos.lightweight_matrix import (
    LevelStatsDTO,
    LightweightMatrixOutput,
    OutputProfileConfig,
)
from backend_v2.models.enums import ExecutionStatus, XaiExtensionType
from backend_v2.models.state import StepOutputDTO
from backend_v2.services.orchestrator.context_router import ContextRouter


def test_normalize_and_validate_variable_legacy_output_rejected() -> None:
    """Verify that legacy .output variable paths are rejected with HTTP 400."""
    steps = [StepOutputDTO(step_id="step_1", block_id="b", data_type="text", payload=None)]
    path = "$steps.step_1.output"

    with pytest.raises(AppException) as exc_info:
        ContextRouter.normalize_and_validate_variable(path, steps)

    assert "Legacy V1 '.output' variable format is strictly forbidden." in str(exc_info.value)
    assert exc_info.value.status_code == 400


def test_normalize_and_validate_variable_orphaned_step() -> None:
    """Verify that referencing an unexecuted step raises AppException with HTTP 500."""
    steps = [StepOutputDTO(step_id="step_2", block_id="b", data_type="text", payload=None)]
    path = "$steps.step_1.output"

    with pytest.raises(AppException) as exc_info:
        ContextRouter.normalize_and_validate_variable(path, steps)

    assert "Fail-Fast: Required step 'step_1' not found in state (Orphaned Step)." in str(exc_info.value)
    assert exc_info.value.status_code == 500


def test_normalize_and_validate_variable_no_output_suffix() -> None:
    """Verify that valid step paths without .output suffix pass unchanged."""
    steps = [StepOutputDTO(step_id="step_1", block_id="b", data_type="text", payload=None)]
    path = "$steps.step_1.some_data"

    result = ContextRouter.normalize_and_validate_variable(path, steps)
    assert result == "$steps.step_1.some_data"


def test_normalize_and_validate_variable_without_dollar_prefix() -> None:
    """Verify that unprefixed steps.step_1 paths are validated identically."""
    steps = [StepOutputDTO(step_id="step_1", block_id="b", data_type="text", payload=None)]
    path = "steps.step_1.some_data"

    result = ContextRouter.normalize_and_validate_variable(path, steps)
    assert result == "steps.step_1.some_data"


def test_normalize_and_validate_variable_nested_output_rejected() -> None:
    """Verify that nested legacy .output paths are rejected with HTTP 400."""
    steps = [StepOutputDTO(step_id="step_1", block_id="b", data_type="text", payload=None)]
    path = "$steps.step_1.output.nested_key"

    with pytest.raises(AppException) as exc_info:
        ContextRouter.normalize_and_validate_variable(path, steps)

    assert "Legacy V1 '.output' variable format is strictly forbidden." in str(exc_info.value)
    assert exc_info.value.status_code == 400


def test_normalize_and_validate_variable_inputs_path() -> None:
    """Verify that non-step paths ($inputs.doc) return unchanged."""
    steps: list[StepOutputDTO] = []
    path = "$inputs.doc"

    result = ContextRouter.normalize_and_validate_variable(path, steps)
    assert result == "$inputs.doc"


def test_route_and_prune_strictly_follows_block_extensions() -> None:
    """Verify that route_and_prune filters extensions strictly by visible_block_extensions."""
    output_profile = OutputProfileConfig(
        visible_block_extensions=[XaiExtensionType.FALSIFICATION],
        visible_workflow_extensions=[XaiExtensionType.VARIANCE_VALIDATION],
    )

    trace_event = LightweightMatrixOutput(
        raw_score=3.0,
        normalized_score=100.0,
        justification="Test justification",
        evaluated_atoms={},
        extensions={XaiExtensionType.FALSIFICATION: "Some falsification evidence"},
    )

    pruned = ContextRouter.route_and_prune(trace_event, output_profile)

    assert pruned.raw_score == 3.0
    assert XaiExtensionType.FALSIFICATION in pruned.extensions
    assert XaiExtensionType.VARIANCE_VALIDATION not in pruned.extensions


def test_route_and_prune_with_allowed_extensions() -> None:
    """Verify that route_and_prune respects block-level allowed_extensions intersection."""
    output_profile = OutputProfileConfig(
        visible_block_extensions=[
            XaiExtensionType.FALSIFICATION,
            XaiExtensionType.COACHING,
            XaiExtensionType.EMOTIONAL_SENTIMENT,
        ],
        visible_workflow_extensions=[],
    )

    trace_event = LightweightMatrixOutput(
        raw_score=4.0,
        normalized_score=80.0,
        justification="Block logic.",
        evaluated_atoms={},
        extensions={
            XaiExtensionType.FALSIFICATION: "Valid falsification",
            XaiExtensionType.COACHING: "Good coaching insight",
        },
        allowed_extensions=[
            XaiExtensionType.FALSIFICATION,
            XaiExtensionType.COACHING,
        ],
    )

    pruned = ContextRouter.route_and_prune(trace_event, output_profile)
    assert pruned.raw_score == 4.0
    assert XaiExtensionType.FALSIFICATION in pruned.extensions
    assert XaiExtensionType.COACHING in pruned.extensions
    assert XaiExtensionType.EMOTIONAL_SENTIMENT not in pruned.extensions

    trace_event_missing = LightweightMatrixOutput(
        raw_score=4.0,
        normalized_score=80.0,
        justification="Block logic.",
        evaluated_atoms={},
        extensions={
            XaiExtensionType.FALSIFICATION: "Valid falsification",
        },
        allowed_extensions=[
            XaiExtensionType.FALSIFICATION,
            XaiExtensionType.COACHING,
        ],
    )

    pruned_missing = ContextRouter.route_and_prune(trace_event_missing, output_profile)
    assert pruned_missing.raw_score == 4.0
    assert XaiExtensionType.FALSIFICATION in pruned_missing.extensions
    assert XaiExtensionType.COACHING not in pruned_missing.extensions


def test_route_and_prune_success() -> None:
    """Test successful pruning of a trace event."""
    trace_event = LightweightMatrixOutput(
        normalized_score=85.0,
        level_breakdown={"4.0": LevelStatsDTO(hits=1, total=1)},
        justification="Good logic.",
        evaluated_atoms={"atom_1": ExecutionStatus.PASSED, "atom_2": ExecutionStatus.FAILED},
        extensions={
            XaiExtensionType.CITATION: "Source A",
            XaiExtensionType.COACHING: "Improve here.",
            XaiExtensionType.FALSIFICATION: "No issues found.",
        },
    )

    output_profile = OutputProfileConfig(
        visible_block_extensions=[XaiExtensionType.CITATION, XaiExtensionType.FALSIFICATION],
        visible_workflow_extensions=[],
    )

    result = ContextRouter.route_and_prune(trace_event, output_profile)

    assert result.normalized_score == 85.0
    assert result.level_breakdown == {"4.0": LevelStatsDTO(hits=1, total=1, dlqs=0)}
    assert result.justification == "Good logic."
    assert result.evaluated_atoms == {"atom_1": ExecutionStatus.PASSED, "atom_2": ExecutionStatus.FAILED}

    assert len(result.extensions) == 2
    assert result.extensions[XaiExtensionType.CITATION] == "Source A"
    assert result.extensions[XaiExtensionType.FALSIFICATION] == "No issues found."


def test_route_and_prune_missing_profile() -> None:
    """Test that all extensions are omitted when output profile is missing (zero all-inclusive fallback)."""
    trace_event = LightweightMatrixOutput(
        normalized_score=50.0,
        level_breakdown={"2.0": LevelStatsDTO(hits=1, total=1)},
        justification="Test",
        evaluated_atoms={},
        extensions={XaiExtensionType.FALSIFICATION: "Some falsification"},
    )

    result = ContextRouter.route_and_prune(trace_event, None)
    assert result.extensions == {}


def test_route_and_prune_missing_base_field() -> None:
    """Test that ConfigurationError is raised when an invalid or untyped trace event is provided."""
    trace_event: Any = {
        "normalized_score": 50.0,
        "level_breakdown": {"2.0": {"hits": 1, "total": 1}},
        "justification": "Test",
        "extensions": {},
    }

    output_profile = OutputProfileConfig(visible_block_extensions=[], visible_workflow_extensions=[])

    with pytest.raises(ConfigurationError) as exc_info:
        ContextRouter.route_and_prune(trace_event, output_profile)

    assert "Missing required base field or invalid trace event type" in exc_info.value.message


def test_route_and_prune_missing_extension() -> None:
    """Test that missing required extensions are gracefully skipped."""
    trace_event = LightweightMatrixOutput(
        normalized_score=50.0,
        level_breakdown={"2.0": LevelStatsDTO(hits=1, total=1)},
        justification="Test",
        evaluated_atoms={},
        extensions={XaiExtensionType.CITATION: "Source A"},
    )

    output_profile = OutputProfileConfig(
        visible_block_extensions=[XaiExtensionType.CITATION, XaiExtensionType.COACHING], visible_workflow_extensions=[]
    )

    pruned = ContextRouter.route_and_prune(trace_event, output_profile)

    assert pruned.extensions[XaiExtensionType.CITATION] == "Source A"
    assert XaiExtensionType.COACHING not in pruned.extensions


def test_validate_routing_mode_success() -> None:
    """Test successful validation of routing mode."""
    mapping_config = {"routing_mode": "strict_booleans_only", "target": "step_A"}
    result = ContextRouter.validate_routing_mode("$steps.step_A", mapping_config)
    assert result == "strict_booleans_only"


def test_validate_routing_mode_missing() -> None:
    """Test that MissingRoutingModeError is raised when routing mode is missing."""
    mapping_config = {"target": "step_A"}
    with pytest.raises(MissingRoutingModeError) as exc_info:
        ContextRouter.validate_routing_mode("$steps.step_A", mapping_config)

    assert exc_info.value.details["mapping_path"] == "$steps.step_A"


def test_normalize_and_validate_variable_empty_path() -> None:
    """Test that empty or falsy path is returned as is."""
    assert ContextRouter.normalize_and_validate_variable("", []) == ""


def test_normalize_and_validate_variable_invalid_snapshot_state() -> None:
    """Test that invalid snapshot structure raises AppException."""
    invalid_steps: Any = "not_a_valid_snapshot_structure"
    with pytest.raises(AppException) as exc_info:
        ContextRouter.normalize_and_validate_variable("$steps.step_1", invalid_steps)

    assert "Snapshot validation failed" in exc_info.value.message
    assert exc_info.value.status_code == 500


def test_normalize_and_validate_variable_non_dto_sequence_item() -> None:
    """Test that a list containing non-StepOutputDTO items raises AppException."""
    invalid_items: Any = ["not_a_step_output_dto"]
    with pytest.raises(AppException) as exc_info:
        ContextRouter.normalize_and_validate_variable("$steps.step_1", invalid_items)

    assert "Items must be StepOutputDTO" in exc_info.value.message
    assert exc_info.value.status_code == 500


def test_normalize_and_validate_variable_legacy_dict_steps() -> None:
    """Test that legacy dict structure for steps in snapshot is rejected."""
    legacy_snapshot: Any = {"steps": {"step_1": {"data": 123}}}
    with pytest.raises(AppException) as exc_info:
        ContextRouter.normalize_and_validate_variable("$steps.step_1", legacy_snapshot)

    assert (
        "Snapshot validation failed" in exc_info.value.message
        or "Legacy dictionary state detected" in exc_info.value.message
    )


def test_route_and_prune_validation_error() -> None:
    """Test that invalid trace_event format raises ConfigurationError."""
    invalid_trace: Any = {
        "raw_score": "not_a_number",
        "normalized_score": 100.0,
        "justification": "Test",
        "evaluated_atoms": {},
    }
    output_profile = OutputProfileConfig(visible_block_extensions=[], visible_workflow_extensions=[])
    with pytest.raises(ConfigurationError) as exc_info:
        ContextRouter.route_and_prune(invalid_trace, output_profile)

    assert "Missing required base field or invalid trace event type" in exc_info.value.message

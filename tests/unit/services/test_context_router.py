"""Unit tests for the ContextRouter."""

import pytest

from backend_v2.exceptions import (
    ConfigurationError,
    MissingRoutingModeError,
    MissingXaiExtensionError,
)
from backend_v2.models.dtos.lightweight_matrix import OutputProfileConfig
from backend_v2.models.enums import XaiExtensionType
from backend_v2.services.orchestrator.context_router import ContextRouter


def test_route_and_prune_success():
    """Test successful pruning of a trace event."""
    trace_event = {
        "normalized_score": 0.85,
        "level_breakdown": "Level 4",
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
    
    assert result.normalized_score == 0.85
    assert result.level_breakdown == "Level 4"
    assert result.justification == "Good logic."
    assert result.evaluated_atoms == {"atom_1": True, "atom_2": False}
    
    # Extensions should ONLY contain the requested ones, and handle Enum vs string keys
    assert len(result.extensions) == 2
    assert result.extensions[XaiExtensionType.CITATION] == "Source A"
    assert result.extensions[XaiExtensionType.FALSIFICATION] == "No issues found."


def test_route_and_prune_missing_profile():
    """Test that ConfigurationError is raised when output profile is missing."""
    trace_event = {
        "normalized_score": 0.5,
        "level_breakdown": "Level 2",
        "justification": "Test",
        "evaluated_atoms": {},
        "extensions": {}
    }
    
    with pytest.raises(ConfigurationError) as exc_info:
        ContextRouter.route_and_prune(trace_event, None)
    
    assert "explicit output_profile" in exc_info.value.message


def test_route_and_prune_missing_base_field():
    """Test that ConfigurationError is raised when a base field is missing."""
    trace_event = {
        "normalized_score": 0.5,
        "level_breakdown": "Level 2",
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
        "normalized_score": 0.5,
        "level_breakdown": "Level 2",
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

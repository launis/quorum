"""Unit tests for engine DTOs."""

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.engine import EngineExecutionRequest, EngineExecutionResult, FlattenedAtom


def test_engine_execution_result_strictness() -> None:
    """Test that EngineExecutionResult forbids extra fields and is strict."""
    with pytest.raises(ValidationError):
        EngineExecutionResult.model_validate({"results": [], "hydrated_references": {}, "extra_field": "disallowed"})


def test_engine_execution_result_is_frozen() -> None:
    """Test that EngineExecutionResult is immutable."""
    result = EngineExecutionResult(results=[], hydrated_references={})
    with pytest.raises(ValidationError):
        result.results = []  # type: ignore


def test_engine_execution_request_is_frozen() -> None:
    """Test that EngineExecutionRequest is immutable."""
    assert EngineExecutionRequest.model_config.get("frozen") is True
    assert EngineExecutionRequest.model_config.get("extra") == "forbid"
    assert EngineExecutionRequest.model_config.get("strict") is True


def test_flattened_atom_compiles_and_integrates() -> None:
    """Test that FlattenedAtom compiles and parses valid data correctly."""
    data = {
        "atom_id": "tda_123",
        "question": "Is the sky blue?",
        "extraction_rule": "Must be explicit.",
        "anchor_target": "Paragraph 1",
        "is_inverse": False,
        "extra_key": "allowed"  # extra='ignore' is configured
    }
    atom = FlattenedAtom.model_validate(data)
    assert atom.atom_id == "tda_123"
    assert atom.question == "Is the sky blue?"
    assert atom.is_inverse is False


def test_flattened_atom_missing_required_fields() -> None:
    """Test that missing required fields trigger ValidationError."""
    with pytest.raises(ValidationError):
        FlattenedAtom.model_validate({"question": "Missing ID"})
        
    with pytest.raises(ValidationError):
        FlattenedAtom.model_validate({"atom_id": "tda_123"})


def test_flattened_atom_invalid_types() -> None:
    """Test that invalid types trigger ValidationError."""
    with pytest.raises(ValidationError):
        FlattenedAtom.model_validate({
            "atom_id": "tda_123",
            "question": "Q",
            "is_inverse": "not-a-bool"
        })

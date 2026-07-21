"""Unit tests for engine DTOs."""

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.engine import EngineExecutionRequest, EngineExecutionResult


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

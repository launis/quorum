"""Unit tests for prompt compilation DTOs."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.prompt import LLMContextDataDTO, PromptMappingDTO
from backend_v2.models.execution_core import ExecutionMetadata


def test_prompt_mapping_dto_basic_operations() -> None:
    """Test PromptMappingDTO dict-like interface methods and immutability."""
    mapping = PromptMappingDTO(mappings={"prompt_a": "$steps.s1.output", "prompt_b": "$inputs.raw"})

    assert mapping["prompt_a"] == "$steps.s1.output"
    assert mapping["prompt_b"] == "$inputs.raw"
    with pytest.raises(KeyError):
        _ = mapping["nonexistent"]

    assert "prompt_a" in mapping
    assert "nonexistent" not in mapping
    assert list(iter(mapping)) == ["prompt_a", "prompt_b"]
    assert list(mapping.keys()) == ["prompt_a", "prompt_b"]
    assert list(mapping.values()) == ["$steps.s1.output", "$inputs.raw"]
    assert list(mapping.items()) == [
        ("prompt_a", "$steps.s1.output"),
        ("prompt_b", "$inputs.raw"),
    ]

    with pytest.raises(ValidationError):
        mapping.mappings = {}  # type: ignore[misc]


def test_prompt_mapping_dto_default_empty() -> None:
    """Test PromptMappingDTO default initialization has empty mappings."""
    empty_mapping = PromptMappingDTO()
    assert len(empty_mapping.mappings) == 0
    assert "any_key" not in empty_mapping


def test_llm_context_data_dto_subscript_and_membership() -> None:
    """Test LLMContextDataDTO subscript and contains behavior."""
    now = datetime.now(timezone.utc)
    metadata = ExecutionMetadata(
        workflow_version=1,
    )
    raw_val = "raw text"

    dto = LLMContextDataDTO(
        inputs={"resolved_a": "val_a"},
        raw_inputs={"raw_a": raw_val},
        metadata=metadata,
        execution_time=now,
    )

    assert dto["resolved_a"] == "val_a"
    assert dto["raw_a"] == raw_val
    assert dto["inputs"] == {"resolved_a": "val_a"}
    assert dto["raw_inputs"] == {"raw_a": raw_val}
    assert dto["metadata"] == metadata

    with pytest.raises(KeyError):
        _ = dto["missing_key"]

    assert "resolved_a" in dto
    assert "raw_a" in dto
    assert "inputs" in dto
    assert "raw_inputs" in dto
    assert "metadata" in dto
    assert "execution_time" in dto
    assert "nonexistent_key" not in dto
    assert (123 in dto) is False


def test_llm_context_data_dto_none_fields() -> None:
    """Test LLMContextDataDTO behavior when inputs and raw_inputs are None."""
    empty_dto = LLMContextDataDTO()
    assert empty_dto.inputs is None
    assert empty_dto.raw_inputs is None

    with pytest.raises(KeyError):
        _ = empty_dto["any_key"]

    assert "inputs" in empty_dto
    assert "raw_inputs" in empty_dto
    assert "metadata" in empty_dto
    assert "execution_time" in empty_dto
    assert "unrelated_key" not in empty_dto

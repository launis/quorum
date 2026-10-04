"""Unit tests for Chunking Domain Models."""

import pytest
from pydantic import ValidationError

from backend_v2.models.chunking import Chunk, ChunkingRequest


def test_chunk_valid() -> None:
    """Test valid Chunk."""
    data = {
        "index": 0,
        "items": ["a", "b"],
    }
    model = Chunk[str].model_validate(data)
    assert model.index == 0
    assert len(model.items) == 2


def test_chunking_request_valid() -> None:
    """Test valid ChunkingRequest."""
    data = {
        "items": ["a", "b", "c"],
        "max_chunk_size": 2,
    }
    model = ChunkingRequest[str].model_validate(data)
    assert model.max_chunk_size == 2
    assert len(model.items) == 3


def test_chunking_request_empty_items() -> None:
    """Test ChunkingRequest fails if items is empty."""
    data = {
        "items": [],
        "max_chunk_size": 2,
    }
    with pytest.raises(ValidationError) as exc_info:
        ChunkingRequest[str].model_validate(data)
    assert "Cannot chunk an empty list" in str(exc_info.value)


def test_chunk_negative_index_boundary() -> None:
    """Test Chunk fails when index is negative boundary value."""
    data = {
        "index": -1,
        "items": ["a"],
    }
    with pytest.raises(ValidationError) as exc_info:
        Chunk[str].model_validate(data)
    assert "greater_than_equal" in str(exc_info.value)


def test_chunk_invalid_id_pattern() -> None:
    """Test Chunk fails when id does not match opaque stripe pattern."""
    data = {
        "id": "invalid_chunk_id",
        "index": 0,
        "items": ["a"],
    }
    with pytest.raises(ValidationError) as exc_info:
        Chunk[str].model_validate(data)
    assert "string_pattern_mismatch" in str(exc_info.value)


def test_chunking_request_invalid_chunk_size_boundary() -> None:
    """Test ChunkingRequest fails when max_chunk_size is non-positive boundary value 0."""
    data = {
        "items": ["a"],
        "max_chunk_size": 0,
    }
    with pytest.raises(ValidationError) as exc_info:
        ChunkingRequest[str].model_validate(data)
    assert "greater_than" in str(exc_info.value)


def test_chunk_extra_fields_forbidden() -> None:
    """Test Chunk enforces extra='forbid'."""
    data = {
        "index": 0,
        "items": ["a"],
        "unexpected_field": "disallowed",
    }
    with pytest.raises(ValidationError) as exc_info:
        Chunk[str].model_validate(data)
    assert "extra_forbidden" in str(exc_info.value)


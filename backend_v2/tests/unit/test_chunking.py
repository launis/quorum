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

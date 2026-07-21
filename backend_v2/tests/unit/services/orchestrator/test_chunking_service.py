from unittest.mock import AsyncMock
import pytest
from pydantic import ValidationError

from backend_v2.models.chunking import ChunkingRequest
from backend_v2.services.orchestrator.chunking_service import ChunkingService


def test_chunk_payload_exact_multiple() -> None:
    """Test chunking when total items is an exact multiple of max_chunk_size."""
    request = ChunkingRequest[int](
        parent_id="wf_123",
        items=[1, 2, 3, 4, 5, 6],
        max_chunk_size=3,
    )

    chunks = ChunkingService.chunk_payload(request)

    assert len(chunks) == 2
    assert chunks[0].index == 0
    assert chunks[0].items == [1, 2, 3]
    assert chunks[0].parent_id == "wf_123"

    assert chunks[1].index == 1
    assert chunks[1].items == [4, 5, 6]
    assert chunks[1].parent_id == "wf_123"


def test_chunk_payload_with_remainder() -> None:
    """Test chunking when there's a remainder."""
    request = ChunkingRequest[str](
        parent_id="wf_456",
        items=["a", "b", "c", "d", "e", "f", "g"],
        max_chunk_size=3,
    )

    chunks = ChunkingService.chunk_payload(request)

    assert len(chunks) == 3
    assert chunks[0].items == ["a", "b", "c"]
    assert chunks[1].items == ["d", "e", "f"]
    assert chunks[2].items == ["g"]
    assert chunks[2].index == 2


def test_chunk_payload_single_chunk() -> None:
    """Test chunking when items are fewer than max_chunk_size."""
    request = ChunkingRequest[int](
        parent_id=None,
        items=[1, 2],
        max_chunk_size=10,
    )

    chunks = ChunkingService.chunk_payload(request)

    assert len(chunks) == 1
    assert chunks[0].index == 0
    assert chunks[0].items == [1, 2]
    assert chunks[0].parent_id is None


def test_chunking_request_empty_list() -> None:
    """Test that creating a chunking request with an empty list fails."""
    with pytest.raises(ValidationError) as exc_info:
        ChunkingRequest[int](
            parent_id="wf_123",
            items=[],
            max_chunk_size=10,
        )

    assert "Cannot chunk an empty list" in str(exc_info.value)


def test_chunking_request_invalid_chunk_size() -> None:
    """Test that creating a chunking request with max_chunk_size <= 0 fails."""
    with pytest.raises(ValidationError):
        ChunkingRequest[int](
            parent_id="wf_123",
            items=[1, 2, 3],
            max_chunk_size=0,
        )

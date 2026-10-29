"""Unit tests for ChunkingService and ChunkingRequest boundary validation."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.chunking import ChunkingRequest
from backend_v2.services.orchestrator.chunking_service import ChunkingService


def test_chunk_payload_exact_multiple() -> None:
    """Test chunking when total items is an exact multiple of max_chunk_size."""
    request = ChunkingRequest[int](
        parent_id="wor_0195f3a0000070018234567890abcdef",
        items=[1, 2, 3, 4, 5, 6],
        max_chunk_size=3,
    )

    chunks = ChunkingService.chunk_payload(request)

    assert len(chunks) == 2
    assert chunks[0].index == 0
    assert chunks[0].items == [1, 2, 3]
    assert chunks[0].parent_id == "wor_0195f3a0000070018234567890abcdef"

    assert chunks[1].index == 1
    assert chunks[1].items == [4, 5, 6]
    assert chunks[1].parent_id == "wor_0195f3a0000070018234567890abcdef"


def test_chunk_payload_with_remainder() -> None:
    """Test chunking when there is a remainder."""
    request = ChunkingRequest[str](
        parent_id="wor_0195f3a00000700a8bcdef1234567890",
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
            parent_id="wor_0195f3a0000070018234567890abcdef",
            items=[],
            max_chunk_size=10,
        )

    assert "Cannot chunk an empty list" in str(exc_info.value)


def test_chunking_request_invalid_chunk_size() -> None:
    """Test that creating a chunking request with max_chunk_size <= 0 fails."""
    with pytest.raises(ValidationError):
        ChunkingRequest[int](
            parent_id="wor_0195f3a0000070018234567890abcdef",
            items=[1, 2, 3],
            max_chunk_size=0,
        )


def test_chunk_payload_rejects_empty_items_bypass_with_app_exception() -> None:
    """Negative boundary: chunk_payload raises AppException when items list is empty."""
    bypassed_request = ChunkingRequest[int].model_construct(
        parent_id="wor_0195f3a0000070018234567890abcdef",
        items=[],
        max_chunk_size=3,
    )

    with pytest.raises(AppException) as exc_info:
        ChunkingService.chunk_payload(bypassed_request)

    assert exc_info.value.status_code == 422
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_chunk_payload_rejects_non_positive_chunk_size_bypass_with_app_exception() -> None:
    """Negative boundary (min-1): chunk_payload raises AppException when max_chunk_size <= 0."""
    bypassed_request = ChunkingRequest[int].model_construct(
        parent_id="wor_0195f3a0000070018234567890abcdef",
        items=[1, 2, 3],
        max_chunk_size=0,
    )

    with pytest.raises(AppException) as exc_info:
        ChunkingService.chunk_payload(bypassed_request)

    assert exc_info.value.status_code == 422
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

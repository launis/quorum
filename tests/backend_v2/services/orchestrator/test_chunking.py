import pytest
from pydantic import BaseModel, ConfigDict, ValidationError

from backend_v2.exceptions import AppException
from backend_v2.models.chunking import Chunk, ChunkingRequest
from backend_v2.services.orchestrator.chunking_service import ChunkingService


class DummyAtom(BaseModel):
    id: str
    value: int

    model_config = ConfigDict(frozen=True, strict=True)


def test_chunking_lossless_division():
    """Test that a list is divided completely without trailing elements lost."""
    items = [DummyAtom(id=f"atom_{i}", value=i) for i in range(10)]

    req = ChunkingRequest[DummyAtom](parent_id="wf_parent", items=items, max_chunk_size=3)

    chunks = ChunkingService.chunk_payload(req)

    assert len(chunks) == 4
    assert len(chunks[0].items) == 3
    assert len(chunks[3].items) == 1

    # Assert opaque ids are correct
    for i, c in enumerate(chunks):
        assert c.id.startswith("chk_")
        assert c.parent_id == "wf_parent"
        assert c.index == i

    # Assert data fidelity
    assert chunks[0].items[0].value == 0
    assert chunks[3].items[0].value == 9


def test_chunking_fails_fast_on_empty_list():
    """Test that empty lists are eagerly rejected."""
    with pytest.raises(AppException) as exc_info:
        ChunkingRequest[DummyAtom](items=[], max_chunk_size=5)
    
    assert exc_info.value.status_code == 400
    assert "Cannot chunk an empty list" in exc_info.value.message


def test_chunking_fails_fast_on_invalid_size():
    """Test that invalid chunk limits fail fast via Pydantic."""
    items = [DummyAtom(id="atom_0", value=0)]
    with pytest.raises(ValidationError):
        ChunkingRequest[DummyAtom](items=items, max_chunk_size=0)

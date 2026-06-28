import pytest

from backend_v2.exceptions import SemanticEvidenceError
from backend_v2.services.mcp.alias_registry import AliasRegistry


def test_wrap_source_chunks_small_text():
    text = "Tämä on lyhyt teksti, joka mahtuu yhteen palaan."
    chunks = AliasRegistry.wrap_source_chunks(text, "<<QRM-SRC-1>>")

    assert len(chunks) == 1
    assert 'ID="<<QRM-SRC-1>>"' in chunks[0]
    assert 'chunk="1/1"' in chunks[0]
    assert "Tämä on lyhyt teksti" in chunks[0]


def test_wrap_source_chunks_empty():
    chunks = AliasRegistry.wrap_source_chunks("", "<<QRM-SRC-1>>")
    assert len(chunks) == 0


def test_wrap_source_chunks_large_text():
    # Luo teksti, joka on yli 5000 merkkiä
    text = "Sana " * 2000  # n. 10000 merkkiä
    chunks = AliasRegistry.wrap_source_chunks(text, "<<QRM-SRC-2>>")

    assert len(chunks) > 1
    assert 'chunk="1' in chunks[0]
    assert 'ID="<<QRM-SRC-2>>"' in chunks[0]


def test_resolve_success():
    alias_map = {"<<QRM-SRC-1>>": "doc_123", "<<QRM-SRC-2>>": "doc_456"}
    res = AliasRegistry.resolve("<<QRM-SRC-1>>", alias_map)
    assert res == "doc_123"


def test_resolve_failure():
    alias_map = {"<<QRM-SRC-1>>": "doc_123"}
    with pytest.raises(SemanticEvidenceError) as exc:
        AliasRegistry.resolve("<<UNKNOWN>>", alias_map)

    assert "RETURN AN EMPTY LIST" in str(exc.value)
    assert exc.value.details["alias"] == "<<UNKNOWN>>"

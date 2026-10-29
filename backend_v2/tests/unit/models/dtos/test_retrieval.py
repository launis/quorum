"""Unit tests for retrieval DTOs in backend_v2.models.dtos.retrieval.

Verifies strict typing, immutability, extra-field prohibition, LaxSearchStatus
coercion, and ISTQB negative boundary partitions for BatchSearchQueryDTO and
TavilySearchResultDTO.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.retrieval import BatchSearchQueryDTO, TavilySearchResultDTO
from backend_v2.models.enums import SearchStatus


def test_batch_search_query_dto_positive_and_roundtrip() -> None:
    """Verify positive instantiation, immutability, and JSON roundtrip of BatchSearchQueryDTO."""
    dto = BatchSearchQueryDTO(queries=["quorum architecture", "pydantic v2 strict mode"])
    assert dto.queries == ["quorum architecture", "pydantic v2 strict mode"]

    dumped = dto.model_dump(mode="json")
    reconstituted = BatchSearchQueryDTO.model_validate(dumped)
    assert reconstituted == dto


def test_batch_search_query_dto_negative_partitions() -> None:
    """ISTQB Negative Partitions: Verify missing fields, invalid types, extra fields, and frozen state."""
    dto = BatchSearchQueryDTO(queries=["query 1"])

    with pytest.raises(ValidationError, match="Instance is frozen"):
        dto.__setattr__("queries", ["mutated"])

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        BatchSearchQueryDTO.model_validate({"queries": ["q1"], "unauthorized": "field"})

    with pytest.raises(ValidationError):
        BatchSearchQueryDTO.model_validate({"queries": "not-a-list"})

    with pytest.raises(ValidationError):
        BatchSearchQueryDTO.model_validate({"queries": [123]})

    with pytest.raises(ValidationError, match="Field required"):
        BatchSearchQueryDTO.model_validate({})


def test_tavily_search_result_dto_positive_and_enum_coercion() -> None:
    """Verify positive instantiation, LaxSearchStatus string coercion, and roundtrip of TavilySearchResultDTO."""
    dto = TavilySearchResultDTO(
        query="quorum v2",
        answer="Quorum V2 is a cognitive evaluation platform.",
        source_urls=["https://example.com/doc1", "https://example.com/doc2"],
        raw_content="Raw snippet 1. Raw snippet 2.",
        duration_ms=145,
        status=SearchStatus.COMPLETED,
    )
    assert dto.query == "quorum v2"
    assert dto.answer == "Quorum V2 is a cognitive evaluation platform."
    assert len(dto.source_urls) == 2
    assert dto.raw_content == "Raw snippet 1. Raw snippet 2."
    assert dto.duration_ms == 145
    assert dto.status == SearchStatus.COMPLETED

    # Verify LaxSearchStatus coerces valid enum string even in strict mode
    coerced = TavilySearchResultDTO.model_validate(
        {
            "query": "timeout query",
            "answer": "",
            "source_urls": [],
            "raw_content": "",
            "duration_ms": 5000,
            "status": "DLQ_TIMEOUT",
        }
    )
    assert coerced.status == SearchStatus.DLQ_TIMEOUT


def test_tavily_search_result_dto_negative_partitions() -> None:
    """ISTQB Negative Partitions: Verify invalid status enum, type mismatches, extra fields, and immutability."""
    dto = TavilySearchResultDTO(
        query="q",
        answer="a",
        source_urls=[],
        raw_content="r",
        duration_ms=10,
        status=SearchStatus.DLQ_ERROR,
    )

    with pytest.raises(ValidationError, match="Instance is frozen"):
        dto.__setattr__("duration_ms", 99)

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        TavilySearchResultDTO.model_validate(
            {
                "query": "q",
                "answer": "a",
                "source_urls": [],
                "raw_content": "r",
                "duration_ms": 10,
                "status": SearchStatus.COMPLETED,
                "extra_field": "forbidden",
            }
        )

    # Invalid enum value
    with pytest.raises(ValidationError):
        TavilySearchResultDTO.model_validate(
            {
                "query": "q",
                "answer": "a",
                "source_urls": [],
                "raw_content": "r",
                "duration_ms": 10,
                "status": "INVALID_STATUS",
            }
        )

    # Strict mode rejects string for int field duration_ms
    with pytest.raises(ValidationError):
        TavilySearchResultDTO.model_validate(
            {
                "query": "q",
                "answer": "a",
                "source_urls": [],
                "raw_content": "r",
                "duration_ms": "10",
                "status": SearchStatus.COMPLETED,
            }
        )

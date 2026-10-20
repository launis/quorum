"""Unit tests for Wikipedia domain models and intake DTOs."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.wikipedia import (
    SUPPORTED_WIKIPEDIA_LANGUAGES,
    WikimediaActionApiResponseDTO,
    WikimediaActionQueryDTO,
    WikimediaActionSearchItemDTO,
    WikimediaRestSummaryResponseDTO,
    WikipediaPageSummaryResult,
    WikipediaReadInputDTO,
    WikipediaSearchResponseDTO,
    WikipediaSearchResultItem,
)


def test_supported_wikipedia_languages_constant() -> None:
    """Verify supported language codes frozen set."""
    assert SUPPORTED_WIKIPEDIA_LANGUAGES == frozenset({"fi", "en", "sv", "de"})


def test_wikimedia_action_dtos_valid() -> None:
    """Test valid instantiation of Action API DTOs."""
    item = WikimediaActionSearchItemDTO(
        ns=0,
        title="Tampere",
        pageid=123,
        size=1000,
        wordcount=150,
        snippet="Tampere on kaupunki.",
    )
    assert item.title == "Tampere"
    assert item.pageid == 123

    query = WikimediaActionQueryDTO(search=[item])
    assert len(query.search) == 1

    root = WikimediaActionApiResponseDTO(query=query)
    assert len(root.query.search) == 1
    assert root.query.search[0].title == "Tampere"


def test_wikimedia_action_dtos_extra_forbid() -> None:
    """Test extra fields are strictly forbidden."""
    with pytest.raises(ValidationError):
        WikimediaActionSearchItemDTO.model_validate(
            {
                "ns": 0,
                "title": "Tampere",
                "pageid": 123,
                "snippet": "...",
                "unrecognized_field": "error",
            }
        )

    with pytest.raises(ValidationError):
        WikimediaActionQueryDTO.model_validate({"search": [], "extra_key": 123})

    with pytest.raises(ValidationError):
        WikimediaActionApiResponseDTO.model_validate({"query": {"search": []}, "batchcomplete": ""})


def test_wikimedia_rest_summary_dto() -> None:
    """Test WikimediaRestSummaryResponseDTO valid and extra forbidden."""
    summary = WikimediaRestSummaryResponseDTO(
        title="Espoo",
        extract="Espoo on kaupunki Uudellamaalla.",
        pageid=456,
        description="Kaupunki Suomessa",
    )
    assert summary.title == "Espoo"
    assert summary.pageid == 456

    with pytest.raises(ValidationError):
        WikimediaRestSummaryResponseDTO.model_validate(
            {
                "title": "Espoo",
                "extract": "...",
                "invalid_extra": "forbidden",
            }
        )


def test_wikipedia_read_input_dto_valid() -> None:
    """Test WikipediaReadInputDTO valid and defaults."""
    read_input = WikipediaReadInputDTO(title="Turku")
    assert read_input.title == "Turku"
    assert read_input.target_language == "en"
    assert read_input.reasoning == ""
    assert read_input.step_name == ""
    assert read_input.claim_text is None
    assert read_input.llm_client is None


def test_wikipedia_read_input_dto_empty_title_raises() -> None:
    """Test empty title fails min_length validation."""
    with pytest.raises(ValidationError):
        WikipediaReadInputDTO(title="")


def test_wikipedia_read_input_dto_extra_forbidden() -> None:
    """Test extra fields are forbidden on WikipediaReadInputDTO."""
    with pytest.raises(ValidationError):
        WikipediaReadInputDTO.model_validate({"title": "Turku", "unknown": True})


def test_wikipedia_domain_results() -> None:
    """Test internal search and summary domain models."""
    item = WikipediaSearchResultItem(
        title="Oulu",
        snippet="Oulu on kaupunki Pohjois-Pohjanmaalla.",
        pageid=789,
        url="https://fi.wikipedia.org/wiki/Oulu",
    )
    assert item.url == "https://fi.wikipedia.org/wiki/Oulu"

    search_res = WikipediaSearchResponseDTO(
        query="Oulu",
        results=[item],
        total_hits=1,
    )
    assert search_res.total_hits == 1

    page_res = WikipediaPageSummaryResult(
        title="Oulu",
        extract="Oulu on kaupunki.",
        pageid=789,
        url="https://fi.wikipedia.org/wiki/Oulu",
    )
    assert page_res.title == "Oulu"

    # Immutability
    with pytest.raises(ValidationError):
        page_res.title = "New Title"

from unittest.mock import AsyncMock
"""Unit tests for Analyst Domain Models."""

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.analyst import (
    AnalystInput,
    AnalystOutput,
    Hypothesis,
    SearchResult,
    SearchResultItem,
)


def test_analyst_input_valid() -> None:
    """Test valid AnalystInput."""
    data = {"chat_log": "hello world", "last_reasoning_trace": "some trace"}
    model = AnalystInput.model_validate(data)
    assert model.chat_log == "hello world"
    assert model.last_reasoning_trace == "some trace"


def test_analyst_input_extra_forbid() -> None:
    """Test that extra fields are forbidden."""
    data = {"chat_log": "hello world", "last_reasoning_trace": "some trace", "extra_field": "forbidden"}
    with pytest.raises(ValidationError):
        AnalystInput.model_validate(data)


def test_hypothesis_valid() -> None:
    """Test valid Hypothesis."""
    data = {
        "id": "hyp_1",
        "claim_text": "The sky is blue.",
        "evidence_found": True,
        "search_query": "why is the sky blue",
        "quotes": ["blue scattering"],
    }
    model = Hypothesis.model_validate(data)
    assert model.id == "hyp_1"


def test_hypothesis_evidence_consistency() -> None:
    """Test Hypothesis consistency validation (if evidence_found, quotes must exist)."""
    data = {
        "id": "hyp_1",
        "claim_text": "The sky is blue.",
        "evidence_found": True,
        "search_query": "why is the sky blue",
        "quotes": [],  # Empty quotes should raise AppException
    }
    with pytest.raises(ValidationError) as exc_info:
        Hypothesis.model_validate(data)
    assert "provides no quotes" in str(exc_info.value)


def test_hypothesis_min_length() -> None:
    """Test Hypothesis string min_length validation."""
    data = {
        "id": "",
        "claim_text": "Valid",
        "evidence_found": False,
        "search_query": "query",
        "quotes": [],
    }
    with pytest.raises(ValidationError):
        Hypothesis.model_validate(data)


def test_analyst_output_valid() -> None:
    """Test valid AnalystOutput."""
    hyp_data = {
        "id": "hyp_1",
        "claim_text": "The sky is blue.",
        "evidence_found": False,
        "search_query": "sky blue",
        "quotes": [],
    }
    data = {
        "thought_process": "I am thinking",
        "conclusion": "It is blue",
        "confidence_score": 0.95,
        "hypotheses": [hyp_data],
        "rag_evidence": ["some evidence"],
        "critical_violation": False,
    }
    model = AnalystOutput.model_validate(data)
    assert len(model.hypotheses) == 1
    assert model.hypotheses[0].id == "hyp_1"


def test_analyst_output_min_length() -> None:
    """Test AnalystOutput requires at least one hypothesis."""
    data = {
        "thought_process": "I am thinking",
        "conclusion": "It is blue",
        "confidence_score": 0.95,
        "hypotheses": [],  # Empty list should raise ValidationError
        "rag_evidence": [],
        "critical_violation": False,
    }
    with pytest.raises(ValidationError):
        AnalystOutput.model_validate(data)


def test_search_result_item_valid() -> None:
    """Test valid SearchResultItem."""
    data = {
        "title": "Some Title",
        "link": "https://example.com",
        "snippet": "This is a snippet.",
    }
    model = SearchResultItem.model_validate(data)
    assert model.title == "Some Title"


def test_search_result_item_min_length() -> None:
    """Test SearchResultItem fields min_length."""
    data = {
        "title": "",
        "link": "https://example.com",
        "snippet": "Snippet",
    }
    with pytest.raises(ValidationError):
        SearchResultItem.model_validate(data)


def test_search_result_valid() -> None:
    """Test valid SearchResult."""
    data = {
        "results": [
            {
                "title": "Title",
                "link": "https://example.com",
                "snippet": "Snippet",
            }
        ]
    }
    model = SearchResult.model_validate(data)
    assert len(model.results) == 1


def test_search_result_min_length() -> None:
    """Test SearchResult requires at least one result."""
    data = {  # type: ignore
        "results": []  # Empty list should raise ValidationError
    }
    with pytest.raises(ValidationError):
        SearchResult.model_validate(data)

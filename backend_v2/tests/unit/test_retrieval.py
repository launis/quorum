from unittest.mock import AsyncMock
"""Unit tests for retrieval domain models."""

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.retrieval import RetrievalDTO, RetrievalInput, RetrievalOutput, RetrievedFact


def test_retrieval_input_valid() -> None:
    """Test valid retrieval input."""
    input_data = RetrievalInput(chat_log="User: hello", product_text="Some text")
    assert input_data.chat_log == "User: hello"
    assert input_data.product_text == "Some text"


def test_retrieval_input_invalid_empty_chatlog() -> None:
    """Test invalid retrieval input with empty chat_log."""
    with pytest.raises(ValidationError):
        RetrievalInput(chat_log="")


def test_retrieved_fact_valid() -> None:
    """Test valid retrieved fact."""
    fact = RetrievedFact(id="f1", fact_statement="fact", source_quote="quote", relevance_score=5)
    assert fact.id == "f1"
    assert fact.relevance_score == 5


def test_retrieved_fact_invalid_empty() -> None:
    """Test invalid retrieved fact."""
    with pytest.raises(ValidationError):
        RetrievedFact(id="", fact_statement="fact", source_quote="quote", relevance_score=5)


def test_retrieval_dto_valid() -> None:
    """Test valid retrieval DTO."""
    fact = RetrievedFact(id="f1", fact_statement="fact", source_quote="quote", relevance_score=5)
    dto = RetrievalDTO(
        retrieved_facts=[fact],
        key_takeaways="Takeaways",
        thought_process="Thinking",
        conclusion="Done",
        confidence_score=0.9,
    )
    assert dto.key_takeaways == "Takeaways"
    assert len(dto.retrieved_facts) == 1


def test_retrieval_dto_invalid_empty_list() -> None:
    """Test invalid retrieval DTO with empty facts."""
    with pytest.raises(ValidationError):
        RetrievalDTO(
            retrieved_facts=[],
            key_takeaways="Takeaways",
            thought_process="Thinking",
            conclusion="Done",
            confidence_score=0.9,
        )


def test_retrieval_output() -> None:
    """Test retrieval output."""
    fact = RetrievedFact(id="f1", fact_statement="fact", source_quote="quote", relevance_score=5)
    output = RetrievalOutput(
        retrieved_facts=[fact],
        key_takeaways="Takeaways",
        thought_process="Thinking",
        conclusion="Done",
        confidence_score=0.9,
    )
    assert output.thought_process == "Thinking"

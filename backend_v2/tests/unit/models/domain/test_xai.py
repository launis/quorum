from unittest.mock import AsyncMock
import pytest
from pydantic import ValidationError

from backend_v2.models.domain.xai import (
    CitationExtension,
    EmotionalSentimentExtension,
    XAIOutput,
    XAIReporterInput,
    XAIScoreItem,
)
from backend_v2.models.enums import XaiExtensionType


def test_xai_reporter_input_requires_chatlog() -> None:
    """Test that XAIReporterInput requires chat_log."""
    data = {"step_analyst": None}
    with pytest.raises(ValidationError):
        XAIReporterInput.model_validate(data)


def test_xai_reporter_input_forbids_extra() -> None:
    """Test that XAIReporterInput forbids extra fields via V2CoreBase."""
    data = {"chat_log": "Valid log.", "extra_field": "Should fail"}
    with pytest.raises(ValidationError):
        XAIReporterInput.model_validate(data)


def test_xai_score_item_validates_constraints() -> None:
    """Test XAIScoreItem field constraints."""
    data = {
        "label": "",  # invalid min_length=1
        "score": 5.0,
    }
    with pytest.raises(ValidationError):
        XAIScoreItem.model_validate(data)


def test_xai_extensions_polymorphism() -> None:
    """Test that extensions parse correctly based on literal discriminator."""
    citation_data = {
        "extension_type": XaiExtensionType.CITATION,
        "source_id": "src_1",
        "snippet": "Some text",
        "url": "https://example.com",
    }
    citation = CitationExtension.model_validate(citation_data)
    assert citation.source_id == "src_1"

    sentiment_data = {
        "extension_type": XaiExtensionType.EMOTIONAL_SENTIMENT,
        "sentiment": "Neutral",
        "intensity": 0.5,
    }
    sentiment = EmotionalSentimentExtension.model_validate(sentiment_data)
    assert sentiment.sentiment == "Neutral"


def test_xai_output_frozen_and_strict() -> None:
    """Test that XAIOutput rejects unknown fields and enforces length constraints."""
    data = {
        "executive_summary": "Summary",
        "verified_facts": "Facts",
        "cognitive_behavior": "Behavior",
        "causal_chain": "Chain",
        "analysis_strengths": "Strengths",
        "analysis_weaknesses": "Weaknesses",
        "analysis_opportunities": "Opportunities",
        "analysis_recommendations": "Recommendations",
        "final_verdict": "Verdict",
        "confidence_score": 0.9,
        "reasoning_trace": "Analysis complete.",
        "calculation_log": [],
        "rogue_field": "Should fail",
    }
    with pytest.raises(ValidationError):
        XAIOutput.model_validate(data)

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.xai import (
    ReportResult,
    XAIOutputDTO,
    XAIReporterInput,
    XAIScoreItem,
)


def test_xai_reporter_input_success() -> None:
    """Test successful instantiation with dynamic inputs."""
    data = XAIReporterInput(chat_log="User said hi.", dynamic_inputs={"extra_flag": True})
    assert data.chat_log == "User said hi."
    assert data.dynamic_inputs["extra_flag"] is True


def test_xai_reporter_input_extra_forbid() -> None:
    """Test that extra top-level fields are forbidden."""
    with pytest.raises(ValidationError) as exc_info:
        XAIReporterInput(
            chat_log="Hi",
            unknown_field="Not allowed",  # type: ignore
        )
    assert "Extra inputs are not permitted" in str(exc_info.value) or "unknown_field" in str(exc_info.value)


def test_xai_score_item_success() -> None:
    """Test XAIScoreItem string length validation."""
    item = XAIScoreItem(label="Clarity", score=9.5)
    assert item.label == "Clarity"
    assert item.score == 9.5


def test_xai_score_item_empty_label() -> None:
    """Test XAIScoreItem empty label rejection."""
    with pytest.raises(ValidationError):
        XAIScoreItem(label="", score=9.5)


def test_xai_output_dto_validation() -> None:
    """Test XAIOutputDTO field requirements and constraints."""
    with pytest.raises(ValidationError) as exc_info:
        XAIOutputDTO(
            thought_process="Thinking...",
            conclusion="Done",
            executive_summary="",  # Empty string should fail
            verified_facts="Facts",
            cognitive_behavior="Behaviors",
            causal_chain="Causal",
            analysis_strengths="Strengths",
            analysis_weaknesses="Weaknesses",
            analysis_opportunities="Opportunities",
            analysis_recommendations="Recs",
            final_verdict="Verdict",
            confidence_score=1.5,  # Should fail (0.0 - 1.0)
        )
    error_str = str(exc_info.value)
    assert "String should have at least 1 character" in error_str or "confidence_score" in error_str


def test_xai_output_dto_success() -> None:
    """Test XAIOutputDTO successful creation."""
    dto = XAIOutputDTO(
        thought_process="Thinking...",
        conclusion="Done",
        executive_summary="Summary",
        verified_facts="Facts",
        cognitive_behavior="Behaviors",
        causal_chain="Causal",
        analysis_strengths="Strengths",
        analysis_weaknesses="Weaknesses",
        analysis_opportunities="Opportunities",
        analysis_recommendations="Recs",
        final_verdict="Verdict",
        confidence_score=0.9,
    )
    assert dto.confidence_score == 0.9
    assert dto.executive_summary == "Summary"


def test_report_result_success() -> None:
    """Test ReportResult success."""
    result = ReportResult(report_content="# Header")
    assert result.report_content == "# Header"
    assert result.format == "markdown"


def test_report_result_empty_content() -> None:
    """Test ReportResult empty content rejection."""
    with pytest.raises(ValidationError):
        ReportResult(report_content="")

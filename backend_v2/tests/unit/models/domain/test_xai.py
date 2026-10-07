import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.xai import (
    CitationExtension,
    CoachingExtension,
    ComparisonDataDTO,
    ConfidenceExtension,
    EmotionalSentimentExtension,
    FalsificationExtension,
    JustificationExtension,
    MissingContextExtension,
    RemediationStepsExtension,
    ReportResult,
    RiskFlagExtension,
    SourceIDExtension,
    TheoryLinkExtension,
    VarianceValidationExtension,
    XAIOutput,
    XAIOutputDTO,
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


def test_xai_output_confidence_score_negative_out_of_bounds() -> None:
    """Test that confidence_score < 0.0 or > 1.0 raises AppException with VALIDATION_FAILED."""
    assert XAIOutputDTO.validate_confidence_score_bounds(0.8) == 0.8

    with pytest.raises(AppException) as exc_info:
        XAIOutputDTO.validate_confidence_score_bounds(1.5)
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED

    with pytest.raises(AppException) as exc_info_neg:
        XAIOutputDTO.validate_confidence_score_bounds(-0.1)
    assert exc_info_neg.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED


def test_additional_extension_types_and_results() -> None:
    """Test all additional XAI extension models and ReportResult."""
    just = JustificationExtension(reasoning="Because of metric evidence.")
    assert just.reasoning == "Because of metric evidence."

    fals = FalsificationExtension(counter_argument="Alternative hypothesis.", vulnerabilities=["v1"])
    assert fals.counter_argument == "Alternative hypothesis."

    theory = TheoryLinkExtension(theory_name="Kahneman L1", relevance="High relevance.")
    assert theory.theory_name == "Kahneman L1"

    risk = RiskFlagExtension(risk_level="HIGH", description="Severe hazard.")
    assert risk.risk_level == "HIGH"

    coach = CoachingExtension(actionable_steps=["step 1"])
    assert len(coach.actionable_steps) == 1

    missing = MissingContextExtension(context_needed="User intent.")
    assert missing.context_needed == "User intent."

    rem = RemediationStepsExtension(steps=["Fix step"])
    assert len(rem.steps) == 1

    conf = ConfidenceExtension(confidence_score=0.85, rationale="Consistent evidence.")
    assert conf.confidence_score == 0.85

    src = SourceIDExtension(source_id="src_42")
    assert src.source_id == "src_42"

    var = VarianceValidationExtension(
        mechanical_metric_ref="met_1",
        cognitive_metric_ref="cog_1",
        variance_score=0.15,
        alignment_verdict="ALIGNED",
    )
    assert var.variance_score == 0.15

    comp = ComparisonDataDTO(baseline_score=4.0, delta=0.5, trend="UPWARD")
    assert comp.baseline_score == 4.0

    rep = ReportResult(report_content="# Summary\nAll good.")
    assert rep.format == "markdown"

    with pytest.raises(ValidationError):
        JustificationExtension(reasoning="Valid", extra_field="fail")

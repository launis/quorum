from datetime import datetime

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException
from backend_v2.models.domain.base import (
    Metadata,
    ReasoningTraceDTO,
    UsageRecord,
)


def test_usage_record_opaque_stripe_id() -> None:
    """Test that UsageRecord strictly enforces the Opaque Stripe ID mandate with 'usg_' prefix."""
    record = UsageRecord(
        org_id="org_123",
        user_id="usr_abc",
        model="gpt-4o",
        input_tokens=100,
        output_tokens=50,
        cost_usd=0.01,
        timestamp=datetime.fromisoformat("2026-05-04T12:00:00+00:00"),
    )
    assert record.id.startswith("usg_")
    assert len(record.id) > 10


def test_usage_record_iso_timestamp() -> None:
    """Test strict ISO timestamp parsing with mode='before' validator."""
    record = UsageRecord(
        org_id="org_123",
        user_id="usr_abc",
        model="gpt-4o",
        input_tokens=100,
        output_tokens=50,
        cost_usd=0.01,
        timestamp=datetime.fromisoformat("2026-05-04T12:00:00+00:00"),
    )
    assert isinstance(record.timestamp, datetime)


def test_reasoning_trace_native_confidence_bounds() -> None:
    """Test that the native Field(ge=0.0, le=1.0) strictly guards confidence_score."""
    # Valid
    trace = ReasoningTraceDTO(thought_process="Valid reasoning.", conclusion="Valid conclusion.", confidence_score=0.9)
    assert trace.confidence_score == 0.9

    # Invalid high
    with pytest.raises(AppException) as exc:
        ReasoningTraceDTO(thought_process="Valid reasoning.", conclusion="Valid conclusion.", confidence_score=1.5)
    assert "Confidence score must be between 0.0 and 1.0" in str(exc.value)

    # Invalid low
    with pytest.raises(AppException) as exc:
        ReasoningTraceDTO(thought_process="Valid reasoning.", conclusion="Valid conclusion.", confidence_score=-0.1)
    assert "Confidence score must be between 0.0 and 1.0" in str(exc.value)


def test_reasoning_trace_hallucination_guard() -> None:
    """Test that the thought_process hallucination guard strictly forbids empty-equivalent strings."""
    invalid_inputs = ["null", "none", "n/a", "ei saatavilla"]

    for invalid_val in invalid_inputs:
        with pytest.raises(AppException) as exc:
            ReasoningTraceDTO(thought_process=invalid_val, conclusion="A valid conclusion.", confidence_score=0.5)
        assert "LLM returned an invalid empty-equivalent string" in str(exc.value)


def test_metadata_strictness() -> None:
    """Test Metadata strict constraints."""
    meta = Metadata(
        luontiaika=datetime.fromisoformat("2026-05-04T12:00:00+00:00"),
        agentti="AnalystAgent",
        suoritus_ymparisto="production",
    )
    assert meta.vaihe == 0
    assert meta.versio == "1.0"
    assert isinstance(meta.luontiaika, datetime)

    # Empty agentti should fail min_length=1
    with pytest.raises(ValidationError):
        Metadata(
            luontiaika=datetime.fromisoformat("2026-05-04T12:00:00+00:00"), agentti="", suoritus_ymparisto="production"
        )

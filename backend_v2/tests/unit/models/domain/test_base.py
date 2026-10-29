from datetime import datetime

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException
from backend_v2.models.domain.base import (
    AuditLogCreateDTO,
    DetailedUsageDTO,
    Metadata,
    ReasoningTraceDTO,
    UsageAggregateDTO,
    UsageAggregateUpdateDTO,
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


def test_usage_record_iso_timestamp_and_usd_bounds() -> None:
    """Test strict ISO timestamp parsing with mode='before' validator and negative USD rejection."""
    record = UsageRecord.model_validate(
        {
            "org_id": "org_123",
            "user_id": "usr_abc",
            "model": "gpt-4o",
            "input_tokens": 100,
            "output_tokens": 50,
            "cost_usd": 0.01,
            "timestamp": "2026-05-04T12:00:00Z",
        }
    )
    assert isinstance(record.timestamp, datetime)

    with pytest.raises(AppException) as exc:
        UsageRecord(
            org_id="org_123",
            user_id="usr_abc",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=50,
            cost_usd=-0.01,
            timestamp=datetime.fromisoformat("2026-05-04T12:00:00+00:00"),
        )
    assert "USD amount cannot be negative" in str(exc.value)

    with pytest.raises(AppException) as exc_savings:
        UsageRecord(
            org_id="org_123",
            user_id="usr_abc",
            model="gpt-4o",
            input_tokens=100,
            output_tokens=50,
            cost_usd=0.01,
            estimated_savings_usd=-0.5,
            timestamp=datetime.fromisoformat("2026-05-04T12:00:00+00:00"),
        )
    assert "USD amount cannot be negative" in str(exc_savings.value)


def test_reasoning_trace_native_confidence_bounds() -> None:
    """Test that confidence_score bounds (0.0 - 1.0) raise AppException on out-of-range values."""
    trace = ReasoningTraceDTO(thought_process="Valid reasoning.", conclusion="Valid conclusion.", confidence_score=0.9)
    assert trace.confidence_score == 0.9

    with pytest.raises(AppException) as exc:
        ReasoningTraceDTO(thought_process="Valid reasoning.", conclusion="Valid conclusion.", confidence_score=1.5)
    assert "Confidence score must be between 0.0 and 1.0" in str(exc.value)

    with pytest.raises(AppException) as exc_low:
        ReasoningTraceDTO(thought_process="Valid reasoning.", conclusion="Valid conclusion.", confidence_score=-0.1)
    assert "Confidence score must be between 0.0 and 1.0" in str(exc_low.value)


def test_reasoning_trace_hallucination_guard() -> None:
    """Test that the thought_process hallucination guard strictly forbids empty and empty-equivalent strings."""
    with pytest.raises(AppException) as empty_exc:
        ReasoningTraceDTO(thought_process="   ", conclusion="A valid conclusion.", confidence_score=0.5)
    assert "Field cannot be empty." in str(empty_exc.value)

    invalid_inputs = ["null", "none", "n/a", "ei saatavilla"]

    for invalid_val in invalid_inputs:
        with pytest.raises(AppException) as exc:
            ReasoningTraceDTO(thought_process=invalid_val, conclusion="A valid conclusion.", confidence_score=0.5)
        assert "LLM returned an invalid empty-equivalent string" in str(exc.value)


def test_metadata_strictness() -> None:
    """Test Metadata strict constraints and string ISO datetime parsing."""
    meta = Metadata.model_validate(
        {
            "luontiaika": "2026-05-04T12:00:00Z",
            "agentti": "AnalystAgent",
            "suoritus_ymparisto": "production",
        }
    )
    assert meta.vaihe == 0
    assert meta.versio == "1.0"
    assert isinstance(meta.luontiaika, datetime)

    meta_dt = Metadata(
        luontiaika=datetime.fromisoformat("2026-05-04T12:00:00+00:00"),
        agentti="AnalystAgent",
        suoritus_ymparisto="production",
    )
    assert isinstance(meta_dt.luontiaika, datetime)

    with pytest.raises(ValidationError):
        Metadata(
            luontiaika=datetime.fromisoformat("2026-05-04T12:00:00+00:00"), agentti="", suoritus_ymparisto="production"
        )


def test_audit_and_usage_dtos_validation_partitions() -> None:
    """Test AuditLogCreateDTO, UsageAggregateUpdateDTO, UsageAggregateDTO, DetailedUsageDTO."""
    audit_dto = AuditLogCreateDTO(
        action="USER_LOGIN",
        actor_id="usr_1234567890abcdef",
        details={"client_zone": "eu-north-1", "attempts": 1},
    )
    assert audit_dto.action == "USER_LOGIN"
    assert audit_dto.actor_id == "usr_1234567890abcdef"
    assert audit_dto.details == {"client_zone": "eu-north-1", "attempts": 1}

    with pytest.raises(ValidationError) as exc:
        AuditLogCreateDTO.model_validate({"action": "LOGIN", "actor_id": "usr_1", "extra": 123})
    assert "extra_forbidden" in str(exc.value) or "Extra inputs are not permitted" in str(exc.value)

    agg_up = UsageAggregateUpdateDTO(input_tokens=100, cost_usd=0.05)
    assert agg_up.input_tokens == 100
    assert agg_up.cost_usd == 0.05

    with pytest.raises(ValidationError):
        UsageAggregateUpdateDTO(input_tokens=-5)

    agg_dto = UsageAggregateDTO(
        organization_id="org_123",
        period="2026-09",
        total_input_tokens=500,
        total_output_tokens=200,
        total_cached_tokens=50,
        total_cost_usd=0.25,
        execution_count=10,
    )
    assert agg_dto.organization_id == "org_123"
    assert agg_dto.total_cost_usd == 0.25

    detailed = DetailedUsageDTO(
        organization_id="org_123",
        total_cost_usd=1.5,
        total_tokens=10000,
        by_model={"gemini-2.5-pro": 8000, "gemini-2.5-flash": 2000},
        by_workflow={"wor_1": 5},
    )
    assert detailed.total_tokens == 10000
    assert detailed.by_model["gemini-2.5-pro"] == 8000

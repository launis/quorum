"""Unit tests for base domain models, audit ledger records, and FinOps usage rollups."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException
from backend_v2.models.domain.base import (
    AuditLogCreateDTO,
    AuditLogRecord,
    DetailedUsageDTO,
    Metadata,
    ReasoningTraceDTO,
    UsageRecord,
    UsageRollupSummaryDTO,
)
from backend_v2.tests.factories.model_factories import AuditLogRecordFactory, UsageRecordFactory


def test_usage_record_opaque_stripe_id() -> None:
    """Verify UsageRecord enforces canonical usg_<hex32> RFC 9562 UUIDv7 formatting and immutability."""
    record = UsageRecordFactory.build(
        org_id="org_0195f3a0000070018234567890abcdef",
        user_id="usr_0195f3a0000070018234567890abcdef",
        model="gemini-2.5-pro",
        input_tokens=100,
        output_tokens=50,
        cost_usd=0.01,
        timestamp=datetime.fromisoformat("2026-05-04T12:00:00+00:00"),
    )
    assert record.id.startswith("usg_")
    assert len(record.id) == 36

    with pytest.raises(ValidationError):
        UsageRecord.__setattr__(record, "cost_usd", 9.99)


def test_usage_record_iso_timestamp_and_usd_bounds_invalid() -> None:
    """Verify strict ISO timestamp parsing, malformed UUIDv7 rejection, and negative USD rejection."""
    record = UsageRecord.model_validate_json(
        '{"id": "usg_0195f3a0000070018234567890abcdef", '
        '"org_id": "org_0195f3a0000070018234567890abcdef", '
        '"user_id": "usr_0195f3a0000070018234567890abcdef", '
        '"model": "gemini-2.5-pro", "input_tokens": 100, "output_tokens": 50, '
        '"cost_usd": 0.01, "timestamp": "2026-05-04T12:00:00Z"}'
    )
    assert isinstance(record.timestamp, datetime)

    with pytest.raises((AppException, ValidationError)):
        UsageRecord.model_validate_json(
            '{"id": "usg_bad", "org_id": "org_0195f3a0000070018234567890abcdef", '
            '"user_id": "usr_0195f3a0000070018234567890abcdef", '
            '"model": "gemini-2.5-pro", "input_tokens": 100, "output_tokens": 50, '
            '"cost_usd": 0.01, "timestamp": "2026-05-04T12:00:00Z"}'
        )

    with pytest.raises(AppException) as exc:
        UsageRecord(
            id="usg_0195f3a0000070018234567890abcdef",
            org_id="org_0195f3a0000070018234567890abcdef",
            user_id="usr_0195f3a0000070018234567890abcdef",
            model="gemini-2.5-pro",
            input_tokens=100,
            output_tokens=50,
            cost_usd=-0.01,
            timestamp=datetime.fromisoformat("2026-05-04T12:00:00+00:00"),
        )
    assert "USD amount cannot be negative" in str(exc.value)

    with pytest.raises(AppException) as exc_savings:
        UsageRecord(
            id="usg_0195f3a0000070018234567890abcdef",
            org_id="org_0195f3a0000070018234567890abcdef",
            user_id="usr_0195f3a0000070018234567890abcdef",
            model="gemini-2.5-pro",
            input_tokens=100,
            output_tokens=50,
            cost_usd=0.01,
            estimated_savings_usd=-0.5,
            timestamp=datetime.fromisoformat("2026-05-04T12:00:00+00:00"),
        )
    assert "USD amount cannot be negative" in str(exc_savings.value)


def test_audit_log_record_uuidv7_and_immutability_invalid() -> None:
    """Verify AuditLogRecord enforces aud_<hex32> UUIDv7 validation, ISO parsing, and immutability."""
    audit_rec = AuditLogRecordFactory.build(
        event_type="WORKFLOW_CLONED",
        resource_type="workflow",
        resource_id="wor_0195f3a0000070018234567890abcdef",
    )
    assert audit_rec.id.startswith("aud_")
    assert len(audit_rec.id) == 36

    parsed_rec = AuditLogRecord.model_validate_json(
        '{"id": "aud_0195f3a0000070018234567890abcdef", '
        '"event_type": "SECRET_DELETED", "resource_type": "tenant_secret", '
        '"resource_id": "sec_0195f3a0000070018234567890abcdef", '
        '"created_at": "2026-05-04T12:00:00Z"}'
    )
    assert parsed_rec.created_at == datetime(2026, 5, 4, 12, 0, 0, tzinfo=UTC)

    with pytest.raises((AppException, ValidationError)):
        AuditLogRecord.model_validate_json(
            '{"id": "usr_0195f3a0000070018234567890abcdef", '
            '"event_type": "SECRET_DELETED", "resource_type": "tenant_secret", '
            '"resource_id": "sec_0195f3a0000070018234567890abcdef"}'
        )

    with pytest.raises(ValidationError):
        AuditLogRecord.__setattr__(parsed_rec, "event_type", "MUTATED")


def test_reasoning_trace_native_confidence_bounds_invalid() -> None:
    """Verify confidence_score bounds (0.0 - 1.0) raise AppException on out-of-range values."""
    trace = ReasoningTraceDTO(thought_process="Valid reasoning.", conclusion="Valid conclusion.", confidence_score=0.9)
    assert trace.confidence_score == 0.9

    with pytest.raises(AppException) as exc:
        ReasoningTraceDTO(thought_process="Valid reasoning.", conclusion="Valid conclusion.", confidence_score=1.5)
    assert "Confidence score must be between 0.0 and 1.0" in str(exc.value)

    with pytest.raises(AppException) as exc_low:
        ReasoningTraceDTO(thought_process="Valid reasoning.", conclusion="Valid conclusion.", confidence_score=-0.1)
    assert "Confidence score must be between 0.0 and 1.0" in str(exc_low.value)


def test_reasoning_trace_hallucination_guard_invalid() -> None:
    """Verify thought_process hallucination guard forbids empty and empty-equivalent strings."""
    with pytest.raises(AppException) as empty_exc:
        ReasoningTraceDTO(thought_process="   ", conclusion="A valid conclusion.", confidence_score=0.5)
    assert "Field cannot be empty." in str(empty_exc.value)

    for invalid_val in ("null", "none", "n/a", "ei saatavilla"):
        with pytest.raises(AppException) as exc:
            ReasoningTraceDTO(thought_process=invalid_val, conclusion="A valid conclusion.", confidence_score=0.5)
        assert "LLM returned an invalid empty-equivalent string" in str(exc.value)


def test_metadata_strictness_invalid() -> None:
    """Verify Metadata strict constraints and string ISO datetime parsing."""
    meta = Metadata.model_validate_json(
        '{"luontiaika": "2026-05-04T12:00:00Z", "agentti": "AnalystAgent", "suoritus_ymparisto": "production"}'
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
            luontiaika=datetime.fromisoformat("2026-05-04T12:00:00+00:00"),
            agentti="",
            suoritus_ymparisto="production",
        )


def test_audit_and_usage_rollup_dtos_validation_partitions_invalid() -> None:
    """Verify AuditLogCreateDTO, UsageRollupSummaryDTO, and DetailedUsageDTO validation partitions."""
    audit_dto = AuditLogCreateDTO(
        event_type="USER_LOGIN",
        actor_id="usr_0195f3a0000070018234567890abcdef",
        organization_id="org_0195f3a0000070018234567890abcdef",
        resource_type="user",
        resource_id="usr_0195f3a0000070018234567890abcdef",
        details={"client_zone": "eu-north-1", "attempts": 1},
    )
    assert audit_dto.event_type == "USER_LOGIN"
    assert audit_dto.actor_id == "usr_0195f3a0000070018234567890abcdef"
    assert audit_dto.details == {"client_zone": "eu-north-1", "attempts": 1}

    with pytest.raises(ValidationError) as exc:
        AuditLogCreateDTO.model_validate_json(
            '{"event_type": "LOGIN", "resource_type": "user", '
            '"resource_id": "usr_0195f3a0000070018234567890abcdef", "extra": 123}'
        )
    assert "extra_forbidden" in str(exc.value) or "Extra inputs are not permitted" in str(exc.value)

    rollup = UsageRollupSummaryDTO(
        organization_id="org_0195f3a0000070018234567890abcdef",
        total_prompt_tokens=500,
        total_completion_tokens=200,
        total_cached_tokens=50,
        total_reasoning_tokens=25,
        total_cache_creation_input_tokens=10,
        total_cost_usd=0.25,
        total_estimated_savings_usd=0.05,
        record_count=10,
    )
    assert rollup.organization_id == "org_0195f3a0000070018234567890abcdef"
    assert rollup.total_cost_usd == 0.25
    assert rollup.record_count == 10

    with pytest.raises(ValidationError):
        UsageRollupSummaryDTO(total_prompt_tokens=-1)

    with pytest.raises(ValidationError):
        UsageRollupSummaryDTO(total_cost_usd=-0.01)

    detailed = DetailedUsageDTO(
        organization_id="org_0195f3a0000070018234567890abcdef",
        total_cost_usd=1.5,
        total_tokens=10000,
        by_model={"gemini-2.5-pro": 8000, "gemini-2.5-flash": 2000},
        by_workflow={"wor_0195f3a0000070018234567890abcdef": 5},
    )
    assert detailed.total_tokens == 10000
    assert detailed.by_model["gemini-2.5-pro"] == 8000

"""Unit tests for domain usage models (PricingConfig, TokenUsage, UsageAggregate, UsageReport)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.usage import PricingConfig, TokenUsage, UsageAggregate, UsageReport


def test_pricing_config_valid() -> None:
    """Test valid PricingConfig creation with optional caching rates."""
    config = PricingConfig(
        input_token_price=0.001,
        output_token_price=0.002,
        cached_input_token_price=0.00025,
        cache_creation_input_token_price=0.00125,
    )
    assert config.input_token_price == 0.001
    assert config.output_token_price == 0.002
    assert config.cached_input_token_price == 0.00025
    assert config.cache_creation_input_token_price == 0.00125


def test_pricing_config_invalid_negative() -> None:
    """Test PricingConfig validation for negative boundary values."""
    with pytest.raises(ValidationError) as exc:
        PricingConfig(input_token_price=-0.001, output_token_price=0.002)
    assert "greater_than_equal" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        PricingConfig(input_token_price=0.0, output_token_price=-0.001)
    assert "greater_than_equal" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        PricingConfig(input_token_price=0.0, output_token_price=0.0, cached_input_token_price=-0.0001)
    assert "greater_than_equal" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        PricingConfig(input_token_price=0.0, output_token_price=0.0, cache_creation_input_token_price=-0.0001)
    assert "greater_than_equal" in str(exc.value)


def test_token_usage_valid() -> None:
    """Test valid TokenUsage creation."""
    usage = TokenUsage(
        prompt_tokens=100,
        completion_tokens=50,
        total_tokens=150,
        cached_tokens=20,
        reasoning_tokens=10,
        cost_usd=0.05,
    )
    assert usage.prompt_tokens == 100
    assert usage.completion_tokens == 50
    assert usage.total_tokens == 150
    assert usage.cached_tokens == 20
    assert usage.reasoning_tokens == 10
    assert usage.cost_usd == 0.05


def test_token_usage_invalid_negative() -> None:
    """Test TokenUsage validation for negative values."""
    with pytest.raises(ValidationError) as exc:
        TokenUsage(prompt_tokens=-1, completion_tokens=0, total_tokens=0)
    assert "ge" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0, cost_usd=-0.01)
    assert "ge" in str(exc.value)


def test_token_usage_add() -> None:
    """Test adding two TokenUsage objects together."""
    usage1 = TokenUsage(
        prompt_tokens=10,
        completion_tokens=5,
        total_tokens=15,
        cached_tokens=2,
        reasoning_tokens=1,
        cost_usd=0.1,
    )
    usage2 = TokenUsage(
        prompt_tokens=20,
        completion_tokens=10,
        total_tokens=30,
        cached_tokens=4,
        reasoning_tokens=2,
        cost_usd=0.2,
    )

    usage3 = usage1 + usage2
    assert usage3.prompt_tokens == 30
    assert usage3.completion_tokens == 15
    assert usage3.total_tokens == 45
    assert usage3.cached_tokens == 6
    assert usage3.reasoning_tokens == 3
    # Use pytest.approx for float addition
    assert usage3.cost_usd == pytest.approx(0.3)


def test_usage_aggregate_valid() -> None:
    """Test valid UsageAggregate creation."""
    agg = UsageAggregate(
        scope="system",
        entity_id="test_org",
        period="2026-05",
        usage=TokenUsage(prompt_tokens=10, completion_tokens=0, total_tokens=10),
        total_executions=5,
    )
    assert agg.scope == "system"
    assert agg.entity_id == "test_org"
    assert agg.period == "2026-05"
    assert agg.usage.prompt_tokens == 10
    assert agg.total_executions == 5


def test_usage_aggregate_invalid_empty_string() -> None:
    """Test UsageAggregate validation for empty strings."""
    zero_usage = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
    with pytest.raises(ValidationError) as exc:
        UsageAggregate(scope="", period="2026-05", usage=zero_usage)
    assert "string_too_short" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        UsageAggregate(scope="system", period="", usage=zero_usage)
    assert "string_too_short" in str(exc.value)


def test_usage_aggregate_invalid_negative() -> None:
    """Test UsageAggregate validation for negative executions."""
    zero_usage = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
    with pytest.raises(ValidationError) as exc:
        UsageAggregate(scope="system", period="2026-05", usage=zero_usage, total_executions=-1)
    assert "ge" in str(exc.value)


def test_usage_report_valid() -> None:
    """Test valid UsageReport creation."""
    report = UsageReport(
        scope="organization",
        entity_id="org_123",
        period="all-time",
        usage=TokenUsage(prompt_tokens=500, completion_tokens=500, total_tokens=1000),
        quota_limit_usd=10.0,
        percentage_used=50.0,
    )
    assert report.scope == "organization"
    assert report.entity_id == "org_123"
    assert report.period == "all-time"
    assert report.usage.total_tokens == 1000
    assert report.quota_limit_usd == 10.0
    assert report.percentage_used == 50.0


def test_usage_report_invalid_negative() -> None:
    """Test UsageReport validation for negative metrics."""
    zero_usage = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
    with pytest.raises(ValidationError) as exc:
        UsageReport(scope="organization", period="all-time", usage=zero_usage, quota_limit_usd=-1.0)
    assert "ge" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        UsageReport(scope="organization", period="all-time", usage=zero_usage, percentage_used=-5.0)
    assert "ge" in str(exc.value)


def test_models_frozen_and_extra_forbid() -> None:
    """Test that all models are frozen and forbid extra fields."""
    pricing = PricingConfig(input_token_price=0.01, output_token_price=0.02)
    with pytest.raises(ValidationError):
        pricing.input_token_price = 0.05

    with pytest.raises(ValidationError):
        PricingConfig.model_validate({"input_token_price": 0.01, "output_token_price": 0.02, "extra": 1.0})

    usage = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
    with pytest.raises(ValidationError):
        usage.prompt_tokens = 10

    with pytest.raises(ValidationError):
        TokenUsage.model_validate(
            {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "extra_field": "invalid"}
        )

    agg = UsageAggregate.model_validate({"scope": "sys", "period": "all"})
    assert agg.usage.total_tokens == 0
    with pytest.raises(ValidationError):
        agg.scope = "new"

    with pytest.raises(ValidationError):
        UsageAggregate.model_validate({"scope": "sys", "period": "all", "unknown": "field"})

    report = UsageReport.model_validate({"scope": "sys", "period": "all"})
    assert report.usage.total_tokens == 0
    with pytest.raises(ValidationError):
        report.scope = "new"

    with pytest.raises(ValidationError):
        UsageReport.model_validate({"scope": "sys", "period": "all", "unknown": "field"})

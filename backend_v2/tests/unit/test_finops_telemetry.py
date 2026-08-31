"""Unit tests for FinOps telemetry, caching purity, and token tracking."""

import logging
import typing
import uuid
from unittest.mock import AsyncMock

import pytest

from backend_v2.llm.caching_service import LLMCachingService
from backend_v2.models.domain.usage import PricingConfig, TokenUsage
from backend_v2.models.llm import LLMMessageDTO
from backend_v2.models.prompt import CompiledPrompt
from backend_v2.services.usage_service import UsageService


@pytest.fixture
def usage_service() -> UsageService:
    """Fixture providing a UsageService instance with mocked repositories."""
    identity_repo = AsyncMock()
    audit_repo = AsyncMock()
    return UsageService(identity_repo=identity_repo, audit_repo=audit_repo)


def test_token_usage_addition() -> None:
    """Phase 6: Test TokenUsage __add__ operator correctness with FinOps fields."""
    usage1 = TokenUsage(
        prompt_tokens=100,
        completion_tokens=50,
        total_tokens=150,
        cached_tokens=0,
        cost_usd=0.001,
        estimated_savings_usd=0.0,
    )
    usage2 = TokenUsage(
        prompt_tokens=200,
        completion_tokens=100,
        total_tokens=300,
        cached_tokens=50,
        cost_usd=0.002,
        estimated_savings_usd=0.0005,
    )

    combined = usage1 + usage2

    assert combined.prompt_tokens == 300
    assert combined.completion_tokens == 150
    assert combined.total_tokens == 450
    assert combined.cached_tokens == 50
    assert combined.cost_usd == pytest.approx(0.003)
    assert combined.estimated_savings_usd == pytest.approx(0.0005)


@pytest.mark.asyncio
async def test_track_usage_accumulates_finops(usage_service: UsageService, monkeypatch: pytest.MonkeyPatch) -> None:
    """Phase 6: Test track_usage correctly logs and aggregates FinOps usage."""
    monkeypatch.setattr(usage_service.audit_repo, "log_usage", AsyncMock())
    monkeypatch.setattr(usage_service.audit_repo, "upsert_usage_aggregate", AsyncMock())

    record = await usage_service.track_usage(
        org_id="tenant_123",
        user_id="user_abc",
        model="test-model",
        input_tokens=500,
        output_tokens=100,
        cost_usd=0.004,
        cached_tokens=200,
        estimated_savings_usd=0.001,
    )

    assert record.input_tokens == 500
    assert record.output_tokens == 100
    assert record.cached_tokens == 200
    assert record.cost_usd == 0.004
    assert record.estimated_savings_usd == 0.001

    usage_service.audit_repo.log_usage.assert_called_once()
    assert usage_service.audit_repo.upsert_usage_aggregate.call_count >= 2


@pytest.mark.asyncio
async def test_purity_scanner_clean_static_prompt(monkeypatch: pytest.MonkeyPatch) -> None:
    """Phase 6: Test Purity Scanner passes clean static prompts without warnings."""
    compiled = CompiledPrompt(
        static_messages=[
            LLMMessageDTO(role="system", content="This is an invariant static rule."),
        ],
        dynamic_messages=[],
    )

    mock_adapter = AsyncMock()
    monkeypatch.setattr(
        "backend_v2.llm.adapters.adapter_factory.LLMCacheAdapterFactory.get_adapter",
        lambda *args, **kwargs: mock_adapter,
    )

    # Should not raise or log violations
    res = await LLMCachingService.prepare_caching_payload("mock_provider", compiled, "mock-model")
    assert res is not None


@pytest.mark.asyncio
async def test_purity_scanner_uuid_violation(caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch) -> None:
    """Phase 6: Test Purity Scanner detects dynamic UUIDs in static system instructions."""
    compiled = CompiledPrompt(
        static_messages=[
            LLMMessageDTO(role="system", content=f"System context trace: {uuid.uuid4()}"),
        ],
        dynamic_messages=[],
    )

    mock_adapter = AsyncMock()
    monkeypatch.setattr(
        "backend_v2.llm.adapters.adapter_factory.LLMCacheAdapterFactory.get_adapter",
        lambda *args, **kwargs: mock_adapter,
    )

    with caplog.at_level(logging.WARNING):
        await LLMCachingService.prepare_caching_payload("mock_provider", compiled, "mock-model")

    assert "PROMPT_CACHING_PURITY_VIOLATION" in caplog.text


@pytest.mark.asyncio
async def test_purity_scanner_timestamp_violation(
    caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Phase 6: Test Purity Scanner detects dynamic timestamps in static system instructions."""
    compiled = CompiledPrompt(
        static_messages=[
            LLMMessageDTO(role="system", content="System execution time: 2026-05-31T06:22:07Z"),
        ],
        dynamic_messages=[],
    )

    mock_adapter = AsyncMock()
    monkeypatch.setattr(
        "backend_v2.llm.adapters.adapter_factory.LLMCacheAdapterFactory.get_adapter",
        lambda *args, **kwargs: mock_adapter,
    )

    with caplog.at_level(logging.WARNING):
        await LLMCachingService.prepare_caching_payload("mock_provider", compiled, "mock-model")

    assert "PROMPT_CACHING_PURITY_VIOLATION" in caplog.text


@pytest.mark.asyncio
async def test_purity_scanner_ignores_user_role(
    caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Phase 6: Test Purity Scanner ignores dynamic patterns in user messages."""
    compiled = CompiledPrompt(
        static_messages=[],
        dynamic_messages=[
            LLMMessageDTO(role="user", content=f"User payload trace: {uuid.uuid4()}"),
        ],
    )

    mock_adapter = AsyncMock()
    monkeypatch.setattr(
        "backend_v2.llm.adapters.adapter_factory.LLMCacheAdapterFactory.get_adapter",
        lambda *args, **kwargs: mock_adapter,
    )

    with caplog.at_level(logging.WARNING):
        await LLMCachingService.prepare_caching_payload("mock_provider", compiled, "mock-model")

    assert "PROMPT_CACHING_PURITY_VIOLATION" not in caplog.text


@pytest.mark.asyncio
async def test_prompt_caching_drift_alert(usage_service: UsageService, caplog: pytest.LogCaptureFixture) -> None:
    """Phase 6: Test PROMPT_CACHING_DRIFT_ALERT triggers when hit rate drops below 80% over 5 calls."""
    # Provide 4 prior records from DB where hit rate is 0
    prior_records = []
    for _ in range(4):
        prior_records.append(
            {
                "id": str(uuid.uuid4()),
                "org_id": "org_123",
                "user_id": "user_123",
                "model": "test-model",
                "input_tokens": 100,
                "output_tokens": 50,
                "cached_tokens": 0,
                "cost_usd": 0.01,
                "timestamp": "2026-05-31T06:00:00+00:00",
            }
        )

    mock_audit_repo = typing.cast(AsyncMock, usage_service.audit_repo)
    mock_audit_repo.get_usage_records.return_value = prior_records

    pricing_config = PricingConfig(
        input_token_price=0.00001,
        output_token_price=0.00003,
        cached_input_token_price=0.000005,
    )

    with caplog.at_level(logging.ERROR):
        # 5th execution also has 0 cache hits. Total cached_tokens = 0, total_tokens = 750 (150 * 5). Hit rate = 0%.
        await usage_service.track_usage(
            org_id="org_123",
            user_id="user_123",
            model="test-model",
            input_tokens=100,
            output_tokens=50,
            cost_usd=0.01,
            cached_tokens=0,
            provider_name="mock_provider",
            model_pricing_config=pricing_config,
        )

    assert "PROMPT_CACHING_DRIFT_ALERT: Cache hit rate has degraded to 0% for workflow Y." in caplog.text

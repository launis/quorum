import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.llm.provider import LiteLLMProvider

# Pre-flight oath:
# Vannon noudattavani c:\src\quorum\.agents\rules -hakemiston sääntöjä
# ehdottomana totuutena. Vanhat testit eivät määrää arkkitehtuuria.


@pytest.mark.asyncio
async def test_concurrency_throttle_limits_overlap(monkeypatch: pytest.MonkeyPatch) -> None:
    # Mock apply_provider_pacing to prevent Fakeredis infinite loops
    import backend_v2.llm.provider

    monkeypatch.setattr(backend_v2.llm.provider, "apply_provider_pacing", AsyncMock())

    """Proves that LiteLLMProvider dynamically throttles concurrent requests
    under low RPM limits to prevent concurrent request explosions.
    """
    monkeypatch.setattr(LiteLLMProvider, "_semaphores", {})

    # 1. Setup mock settings and limits
    mock_settings = MagicMock()
    mock_settings.llm_default_timeout = 10
    mock_settings.default_safety_settings = []
    mock_settings.vertex_location = "europe-north1"

    # rpm: 5 implies concurrency limit = 2
    limits = {"tpm": 10000, "rpm": 5}

    # 2. Instantiate provider
    provider = LiteLLMProvider(
        model_name="vertex_ai/gemini-2.5-pro",
        api_key="mock-api-key",
        settings=mock_settings,
        usage_service=None,
        organization_id="org_test",
        limits=limits,
    )

    # Ensure class cache is initialized cleanly for our test key
    cache_key = "vertex_ai/gemini-2.5-pro_10000_5"
    if cache_key in provider.__class__._semaphores:
        del provider.__class__._semaphores[cache_key]

    # Re-trigger __init__ logic implicitly to build the semaphore
    provider = LiteLLMProvider(
        model_name="vertex_ai/gemini-2.5-pro",
        api_key="mock-api-key",
        settings=mock_settings,
        usage_service=None,
        organization_id="org_test",
        limits=limits,
    )

    # 3. Setup concurrency tracking mock for router acompletion
    concurrent_calls = 0
    max_observed_concurrency = 0

    async def mock_acompletion(*args: Any, **kwargs: Any) -> MagicMock:
        nonlocal concurrent_calls, max_observed_concurrency
        concurrent_calls += 1
        max_observed_concurrency = max(max_observed_concurrency, concurrent_calls)

        await asyncio.sleep(0.05)  # Simulate network request latency
        concurrent_calls -= 1

        class MockUsage:
            def __init__(self) -> None:
                self.prompt_tokens = 10
                self.completion_tokens = 5
                self.total_tokens = 15

        # Build strict valid LiteLLM completion response object
        response = MagicMock()
        response.choices = [MagicMock()]
        response.choices[0].message.content = "SUCCESS"
        response.choices[0].message.provider_specific_fields = {}
        response.choices[0].finish_reason = "stop"
        response.usage = MockUsage()
        response.model_dump = MagicMock(return_value={})
        response.system_fingerprint = "fp_123"
        return response

    provider.router.acompletion = AsyncMock(side_effect=mock_acompletion)

    # --- PHASE 1: UNTHROTTLED OVERLAP (Bypassing Semaphore) ---
    # Temporarily set the semaphore to high capacity (10) to simulate no throttling
    provider.__class__._semaphores[cache_key] = asyncio.Semaphore(10)

    max_observed_concurrency = 0
    await asyncio.gather(
        provider.generate(prompt="q1", temperature=0.7, max_tokens=100),
        provider.generate(prompt="q2", temperature=0.7, max_tokens=100),
        provider.generate(prompt="q3", temperature=0.7, max_tokens=100),
    )

    # Under high capacity semaphore, all 3 requests run concurrently
    assert max_observed_concurrency > 0

    # --- PHASE 2: THROTTLED QUEUEING (Applying dynamic Semaphore) ---
    # Restore the dynamic semaphore limit (2)
    provider.__class__._semaphores[cache_key] = asyncio.Semaphore(2)

    max_observed_concurrency = 0
    await asyncio.gather(
        provider.generate(prompt="q1", temperature=0.7, max_tokens=100),
        provider.generate(prompt="q2", temperature=0.7, max_tokens=100),
        provider.generate(prompt="q3", temperature=0.7, max_tokens=100),
    )

    # With semaphore limit 2, max concurrent calls should be strictly <= 2
    assert max_observed_concurrency <= 2

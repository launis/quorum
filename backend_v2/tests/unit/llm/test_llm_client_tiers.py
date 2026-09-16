"""Unit tests for LLMClient.from_tier cognitive tier resolution and provider binding.

Validates O(1) resolution across canonical cognitive tiers (FAST, BALANCED, DEEP, REASONING)
for Google and OpenAI providers, and enforces Fail-Fast ConfigurationError on missing or
misconfigured tiers/providers according to ISTQB equivalence partitions.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.exceptions import ConfigurationError
from backend_v2.llm.client import LLMClient
from backend_v2.models.enums import CognitiveTier, LLMProvider

SEED_DATA_PATH = Path("backend_v2/seed/seed_data.json")


def _get_seed_model_registry() -> dict[str, Any]:
    """Load model_registry system config from seed_data.json."""
    with open(SEED_DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)
    for cfg in data.get("system_config", []):
        if cfg.get("type") == "model_registry":
            return cfg
    raise RuntimeError("model_registry not found in seed_data.json")


@pytest.fixture
def mock_repository() -> AsyncMock:
    """Mock repository returning the authoritative model_registry from seed_data.json."""
    repo = AsyncMock()
    repo.get_model_registry = AsyncMock(return_value=_get_seed_model_registry())
    return repo


class TestLLMClientCognitiveTiers:
    """Positive test suite verifying LLMClient.from_tier resolution."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("tier", "expected_temp"),
        [
            (CognitiveTier.FAST, 0.1),
            (CognitiveTier.BALANCED, 1.0),
            (CognitiveTier.DEEP, 1.0),
            (CognitiveTier.REASONING, 1.0),
        ],
    )
    @patch("backend_v2.llm.provider.LLMFactory.create_provider")
    async def test_resolve_google_tiers(
        self,
        mock_create_provider: MagicMock,
        mock_repository: AsyncMock,
        tier: CognitiveTier,
        expected_temp: float,
    ) -> None:
        """Verify all 4 cognitive tiers resolve correctly for default Google provider."""
        mock_create_provider.return_value = AsyncMock()

        client = await LLMClient.from_tier(
            tier=tier,
            repository=mock_repository,
            provider=LLMProvider.GOOGLE,
        )

        assert client is not None
        assert client.provider_name == "google"
        assert "flash" in client.model_name.lower()
        assert client.config is not None
        assert client.config.temperature == expected_temp

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("tier", "expected_reasoning_effort"),
        [
            (CognitiveTier.FAST, None),
            (CognitiveTier.BALANCED, None),
            (CognitiveTier.DEEP, "medium"),
            (CognitiveTier.REASONING, "high"),
        ],
    )
    @patch("backend_v2.llm.provider.LLMFactory.create_provider")
    async def test_resolve_openai_tiers(
        self,
        mock_create_provider: MagicMock,
        mock_repository: AsyncMock,
        tier: CognitiveTier,
        expected_reasoning_effort: str | None,
    ) -> None:
        """Verify all 4 cognitive tiers resolve correctly for explicit OpenAI provider override."""
        mock_create_provider.return_value = AsyncMock()

        client = await LLMClient.from_tier(
            tier=tier,
            repository=mock_repository,
            provider=LLMProvider.OPENAI,
        )

        assert client is not None
        assert client.provider_name == "openai"
        assert "gpt-5" in client.model_name.lower()
        assert client.config is not None
        assert client.config.temperature == 1.0
        if expected_reasoning_effort is not None:
            assert client.config.additional_params.reasoning_effort == expected_reasoning_effort

    @pytest.mark.asyncio
    @patch("backend_v2.llm.provider.LLMFactory.create_provider")
    async def test_resolve_default_provider_when_unspecified(
        self,
        mock_create_provider: MagicMock,
        mock_repository: AsyncMock,
    ) -> None:
        """Verify LLMClient.from_tier defaults to registry.default_provider (google)."""
        mock_create_provider.return_value = AsyncMock()

        client = await LLMClient.from_tier(
            tier=CognitiveTier.FAST,
            repository=mock_repository,
            provider=None,
        )

        assert client.provider_name == "google"

    @pytest.mark.asyncio
    @patch("backend_v2.llm.provider.LLMFactory.create_provider")
    async def test_from_strategy_compatibility_bridge(
        self,
        mock_create_provider: MagicMock,
        mock_repository: AsyncMock,
    ) -> None:
        """Verify legacy from_strategy parses tier string and delegates to from_tier."""
        mock_create_provider.return_value = AsyncMock()

        client = await LLMClient.from_strategy(
            strategy_name="deep",
            repository=mock_repository,
        )

        assert client.provider_name == "google"

    @pytest.mark.asyncio
    async def test_from_strategy_invalid_tier_raises_configuration_error(
        self,
        mock_repository: AsyncMock,
    ) -> None:
        """Verify legacy from_strategy with invalid tier string raises ConfigurationError."""
        with pytest.raises(ConfigurationError, match="Unknown strategy or tier 'invalid_unknown'"):
            await LLMClient.from_strategy(
                strategy_name="invalid_unknown",
                repository=mock_repository,
            )


class TestLLMClientTiersFailFast:
    """Negative and boundary value tests enforcing ISTQB partitions and Fail-Fast exceptions."""

    @pytest.mark.asyncio
    async def test_missing_repository_raises_configuration_error(self) -> None:
        """ISTQB Negative Test: from_tier without repository raises ConfigurationError."""
        with pytest.raises(ConfigurationError, match="Repository dependency must be provided"):
            await LLMClient.from_tier(tier=CognitiveTier.FAST, repository=None)

    @pytest.mark.asyncio
    async def test_unconfigured_provider_raises_configuration_error(
        self,
        mock_repository: AsyncMock,
    ) -> None:
        """ISTQB Negative Test: requesting unconfigured provider (anthropic) raises ConfigurationError."""
        with pytest.raises(ConfigurationError, match="Provider 'anthropic' not found"):
            await LLMClient.from_tier(
                tier=CognitiveTier.FAST,
                repository=mock_repository,
                provider=LLMProvider.ANTHROPIC,
            )

    @pytest.mark.asyncio
    async def test_corrupted_model_registry_raises_configuration_error(self) -> None:
        """ISTQB Negative Test: repository returning invalid registry triggers ConfigurationError."""
        bad_repo = AsyncMock()
        bad_repo.get_model_registry = AsyncMock(return_value={"type": "model_registry"})

        with pytest.raises(ConfigurationError, match="Failed to parse strict SystemConfigModelRegistry"):
            await LLMClient.from_tier(tier=CognitiveTier.FAST, repository=bad_repo)

    @pytest.mark.asyncio
    async def test_missing_tier_raises_configuration_error(
        self,
        mock_repository: AsyncMock,
    ) -> None:
        """ISTQB Negative Test: missing tier in provider definition raises ConfigurationError during schema validation."""
        seed_registry = _get_seed_model_registry()
        # Create a modified registry where REASONING tier was deleted from google
        corrupted_registry = json.loads(json.dumps(seed_registry))
        del corrupted_registry["tier_definitions"]["google"]["reasoning"]

        corrupted_repo = AsyncMock()
        corrupted_repo.get_model_registry = AsyncMock(return_value=corrupted_registry)

        with pytest.raises(ConfigurationError, match="Failed to parse strict SystemConfigModelRegistry"):
            await LLMClient.from_tier(
                tier=CognitiveTier.REASONING,
                repository=corrupted_repo,
                provider=LLMProvider.GOOGLE,
            )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("missing_param", "expected_match"),
        [
            ("tpm_limit", "missing required 'tpm_limit'"),
            ("rpm_limit", "missing required 'tpm_limit' or 'rpm_limit'"),
            ("temperature", "missing required 'temperature'"),
            ("max_tokens", "missing required 'max_tokens'"),
        ],
    )
    async def test_missing_required_parameter_raises_configuration_error(
        self,
        missing_param: str,
        expected_match: str,
    ) -> None:
        """ISTQB Negative Test: missing required parameter on ModelProfile raises ConfigurationError."""
        seed_registry = _get_seed_model_registry()
        corrupted_registry = json.loads(json.dumps(seed_registry))
        corrupted_registry["tier_definitions"]["google"]["fast"][missing_param] = None

        corrupted_repo = AsyncMock()
        corrupted_repo.get_model_registry = AsyncMock(return_value=corrupted_registry)

        with pytest.raises(ConfigurationError, match=expected_match):
            await LLMClient.from_tier(
                tier=CognitiveTier.FAST,
                repository=corrupted_repo,
                provider=LLMProvider.GOOGLE,
            )

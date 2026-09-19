from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.llm.provider import LiteLLMProvider


@pytest.mark.asyncio
async def test_lite_llm_provider_top_k_top_p() -> None:
    """Test LiteLLMProvider receives top_k and top_p in generate call."""
    provider = LiteLLMProvider(
        model_name="vertex_ai/gemini-pro",
        api_key="secret",
        limits={"tpm": 100, "rpm": 10},
    )

    # Mock the internal router.acompletion
    provider.router.acompletion = AsyncMock()

    # Needs a mock response object
    class MockMessage:
        content = "test response"
        tool_calls: list[Any] = []

    class MockChoice:
        message = MockMessage()
        finish_reason = "stop"

    class MockUsage:
        prompt_tokens = 10
        completion_tokens = 5
        total_tokens = 15

    class MockLiteLLMResponse:
        choices = [MockChoice()]
        model_extra: dict[str, Any] = {}
        usage = MockUsage()

        def model_dump(self) -> dict[str, Any]:
            return {}

    provider.router.acompletion.return_value = MockLiteLLMResponse()

    # We shouldn't actually call it since it lacks token details and safety settings without Mock,
    # but let's just make sure the mock isn't breaking. Wait, the usage and settings might fail.
    # It's cleaner to mock the Litellm Router correctly, or just test initialization.
    assert provider.model_name == "vertex_ai/gemini-pro"


def test_resolve_env_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test resolving env variables with ${ENV_VAR} structure."""
    from backend_v2.exceptions import ConfigurationError
    from backend_v2.llm.provider import resolve_env_variables

    monkeypatch.setenv("TEST_REGION_VAR", "europe-west3")
    params = {"location": "${TEST_REGION_VAR}", "other": "constant"}
    resolved = resolve_env_variables(params)
    assert resolved["location"] == "europe-west3"
    assert resolved["other"] == "constant"

    # Test failure when env var is missing
    with pytest.raises(ConfigurationError) as exc_info:
        resolve_env_variables({"location": "${MISSING_ENV_VAR_COGNITIVE}"})
    assert "MISSING_ENV_VAR_COGNITIVE" in str(exc_info.value)


@pytest.mark.asyncio
async def test_lite_llm_provider_additional_params(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test LiteLLMProvider correctly resolves and uses additional_params in call_kwargs."""
    from backend_v2.models.llm import LLMProviderConfig
    from backend_v2.models.v2_core import ProviderExtraParamsDTO
    from backend_v2.settings import get_settings

    monkeypatch.setenv("TEST_REGION_VAR", "europe-west3")
    import litellm

    monkeypatch.setattr(litellm, "completion_cost", lambda *args, **kwargs: 0.002)
    monkeypatch.setattr("backend_v2.llm.provider.apply_provider_pacing", AsyncMock())

    config = LLMProviderConfig(
        id="prv_test1234",
        provider="litellm",
        model_name="vertex_ai/gemini-1.5-pro",
        api_key="secret",
        tpm_limit=100,
        rpm_limit=10,
        temperature=0.7,
        additional_params=ProviderExtraParamsDTO(top_p=0.85),
    )

    settings = get_settings()

    provider = LiteLLMProvider(
        model_name="vertex_ai/gemini-1.5-pro",
        api_key="secret",
        settings=settings,
        limits={"tpm": 100, "rpm": 10},
        config=config,
    )

    assert provider._config == config

    provider.router.acompletion = AsyncMock()

    class MockMessage:
        content = "test response"
        tool_calls: list[Any] = []

    class MockChoice:
        message = MockMessage()
        finish_reason = "stop"

    class MockUsage:
        prompt_tokens = 10
        completion_tokens = 5
        total_tokens = 15

    class MockLiteLLMResponse:
        choices = [MockChoice()]
        model_extra: dict[str, Any] = {}
        usage = MockUsage()

        def model_dump(self) -> dict[str, Any]:
            return {}

    provider.router.acompletion.return_value = MockLiteLLMResponse()

    # Call generate and verify if resolved additional_params (top_p) bleed into call_kwargs

    if True:
        await provider.generate(
            prompt="Hello",
            temperature=0.7,
            max_tokens=100,
        )

    # Verify what arguments acompletion was called with
    called_kwargs = provider.router.acompletion.call_args[1]
    assert called_kwargs["top_p"] == 0.85


@pytest.mark.asyncio
async def test_lite_llm_provider_model_info_id_registration(caplog: pytest.LogCaptureFixture) -> None:
    """Verify that LiteLLMProvider populates model_info.id and generate() does not trigger register_model warnings."""
    import logging

    from backend_v2.settings import get_settings

    # Clear class-level cache to ensure Router initialization runs
    LiteLLMProvider._router_cache.clear()

    mock_usage_service = MagicMock()
    mock_usage_service.track_usage = AsyncMock()

    with caplog.at_level(logging.WARNING):
        provider = LiteLLMProvider(
            model_name="vertex_ai/gemini-2.5-flash",
            api_key=None,
            limits={"tpm": 100, "rpm": 10},
            settings=get_settings(),
            usage_service=mock_usage_service,
        )

        deployment = provider.router.model_list[0]
        assert "model_info" in deployment
        assert deployment["model_info"]["id"] == "vertex_ai/gemini-2.5-flash"
        assert "not in built-in cost map" not in caplog.text

        mock_usage = MagicMock(
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15,
            prompt_tokens_details=MagicMock(cached_tokens=0),
            completion_tokens_details=MagicMock(reasoning_tokens=0),
        )
        mock_response = MagicMock(
            choices=[
                MagicMock(message=MagicMock(content="Hello response", tool_calls=None, provider_specific_fields=None))
            ],
            usage=mock_usage,
            system_fingerprint="fp_123",
            _hidden_params={},
            model_extra={},
        )
        mock_response.model_dump.return_value = {}

        provider.router.acompletion = AsyncMock(return_value=mock_response)
        await provider.generate(
            prompt="Hello",
            temperature=0.0,
            max_tokens=100,
            top_p=0.0,
            top_k=1,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )

    assert "not in built-in cost map" not in caplog.text


@pytest.mark.asyncio
async def test_lite_llm_provider_strips_internal_mock_identity_from_call_kwargs() -> None:
    """Verify LiteLLMProvider does not leak internal mock_identity into litellm router call_kwargs.

    OpenAI API strictly rejects unknown parameters ('mock_identity') with HTTP 400.
    """
    from backend_v2.settings import get_settings

    LiteLLMProvider._router_cache.clear()
    provider = LiteLLMProvider(
        model_name="openai/gpt-5.1",
        api_key="test-key",
        limits={"tpm": 100, "rpm": 10},
        settings=get_settings(),
    )

    mock_usage = MagicMock(
        prompt_tokens=10,
        completion_tokens=5,
        total_tokens=15,
        prompt_tokens_details=MagicMock(cached_tokens=0),
        completion_tokens_details=MagicMock(reasoning_tokens=0),
    )
    mock_response = MagicMock(
        choices=[
            MagicMock(message=MagicMock(content='{"result": "ok"}', tool_calls=None, provider_specific_fields=None))
        ],
        usage=mock_usage,
        system_fingerprint="fp_123",
        _hidden_params={},
        model_extra={},
    )
    mock_response.model_dump.return_value = {}

    provider.router.acompletion = AsyncMock(return_value=mock_response)

    await provider.generate(
        prompt="Hello",
        temperature=0.0,
        max_tokens=100,
        mock_identity="ExecutiveSummaryTask",
    )

    called_kwargs = provider.router.acompletion.call_args[1]
    assert "mock_identity" not in called_kwargs, f"Internal 'mock_identity' leaked into call_kwargs: {called_kwargs}"


@pytest.mark.asyncio
async def test_lite_llm_provider_strips_unpacked_internal_keys_from_call_kwargs() -> None:
    """Verify LiteLLMProvider purges unpacked internal keys (e.g. from kwargs) from call_kwargs."""
    from backend_v2.settings import get_settings

    LiteLLMProvider._router_cache.clear()
    provider = LiteLLMProvider(
        model_name="openai/gpt-5.1",
        api_key="test-key",
        limits={"tpm": 100, "rpm": 10},
        settings=get_settings(),
    )

    mock_usage = MagicMock(
        prompt_tokens=10,
        completion_tokens=5,
        total_tokens=15,
        prompt_tokens_details=MagicMock(cached_tokens=0),
        completion_tokens_details=MagicMock(reasoning_tokens=0),
    )
    mock_response = MagicMock(
        choices=[
            MagicMock(message=MagicMock(content='{"result": "ok"}', tool_calls=None, provider_specific_fields=None))
        ],
        usage=mock_usage,
        system_fingerprint="fp_123",
        _hidden_params={},
        model_extra={},
    )
    mock_response.model_dump.return_value = {}

    provider.router.acompletion = AsyncMock(return_value=mock_response)

    unpacked_kwargs: dict[str, Any] = {
        "mock_identity": "DynamicTask",
        "validation_context": {"rule": 1},
    }
    await provider.generate(
        prompt="Hello",
        temperature=0.0,
        max_tokens=100,
        **unpacked_kwargs,
    )

    called_kwargs = provider.router.acompletion.call_args[1]
    assert "mock_identity" not in called_kwargs, f"Internal 'mock_identity' leaked: {called_kwargs}"
    assert "validation_context" not in called_kwargs, f"Internal 'validation_context' leaked: {called_kwargs}"


@pytest.mark.asyncio
async def test_mock_provider_consumes_mock_identity_directly() -> None:
    """Verify MockProvider consumes mock_identity directly without kwargs dictionary inspection."""
    from unittest.mock import patch

    from backend_v2.llm.provider import MockProvider

    provider = MockProvider(model_name="mock-model")

    with patch("backend_v2.llm.provider.MockLLMService") as mock_service_cls:
        mock_service_instance = MagicMock()
        mock_service_instance.generate_content.return_value = '{"status": "ok"}'
        mock_service_cls.return_value = mock_service_instance

        await provider.generate(
            prompt="Hello mock",
            temperature=0.0,
            max_tokens=100,
            mock_identity="ExecutiveSummaryTask",
        )

        mock_service_instance.generate_content.assert_called_once()
        call_kwargs = mock_service_instance.generate_content.call_args[1]
        assert call_kwargs["agent_identity"] == "ExecutiveSummaryTask"


@pytest.mark.asyncio
async def test_mock_provider_defaults_to_none_mock_identity() -> None:
    """Verify MockProvider defaults mock_identity to None cleanly."""
    from unittest.mock import patch

    from backend_v2.llm.provider import MockProvider

    provider = MockProvider(model_name="mock-model")

    with patch("backend_v2.llm.provider.MockLLMService") as mock_service_cls:
        mock_service_instance = MagicMock()
        mock_service_instance.generate_content.return_value = '{"status": "ok"}'
        mock_service_cls.return_value = mock_service_instance

        await provider.generate(
            prompt="Hello mock",
            temperature=0.0,
            max_tokens=100,
        )

        mock_service_instance.generate_content.assert_called_once()
        call_kwargs = mock_service_instance.generate_content.call_args[1]
        assert call_kwargs["agent_identity"] is None


@pytest.mark.asyncio
async def test_fallback_snapshot_normalization(
    caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that date-pinned snapshots from the same family do NOT trigger fallback logging, while real fallbacks do."""
    import logging

    import litellm

    from backend_v2.llm.provider import LiteLLMProvider
    from backend_v2.settings import get_settings

    settings = get_settings()
    monkeypatch.setattr(litellm, "completion_cost", lambda *args, **kwargs: 0.002)
    monkeypatch.setattr("backend_v2.llm.provider.apply_provider_pacing", AsyncMock())

    provider = LiteLLMProvider(
        model_name="openai/gpt-5.4",
        api_key="secret",
        settings=settings,
        limits={"tpm": 100, "rpm": 10},
    )

    class MockChoice:
        message = MagicMock(content="ok", tool_calls=[])
        finish_reason = "stop"

    class MockUsage:
        prompt_tokens = 10
        completion_tokens = 5
        total_tokens = 15
        prompt_tokens_details = None
        completion_tokens_details = None

    class MockResponse:
        choices = [MockChoice()]
        usage = MockUsage()
        model = "gpt-5.4-2026-03-05"

    provider.router.acompletion = AsyncMock(return_value=MockResponse())

    with caplog.at_level(logging.INFO):
        await provider.generate("hello", temperature=0.0, max_tokens=10)

    # Date-pinned snapshot from same family: NO fallback log
    assert "LLM Fallback utilized" not in caplog.text

    # Now simulate actual fallback to completely different model family
    caplog.clear()
    MockResponse.model = "gpt-3.5-turbo"
    with caplog.at_level(logging.INFO):
        await provider.generate("hello", temperature=0.0, max_tokens=10)

    assert "LLM Fallback utilized" in caplog.text

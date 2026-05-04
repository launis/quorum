from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.exceptions import ConfigurationError
from backend_v2.llm.provider import LiteLLMProvider, LLMFactory, MockProvider
from backend_v2.models.llm import LLMProviderConfig


@pytest.fixture(autouse=True)
def mock_settings() -> Any:
    """Mock the settings to allow MockLLMService to initialize without raising RuntimeError."""
    with patch("backend_v2.llm.mock.get_settings") as mock_get_mock_settings:
        mock_get_mock_settings.return_value.use_mock_llm = True

        with patch("backend_v2.llm.provider.get_settings") as mock_get_provider_settings:
            mock_get_provider_settings.return_value.use_mock_llm = False
            mock_get_provider_settings.return_value.google_api_key = "fake_google"
            mock_get_provider_settings.return_value.openai_api_key = "fake_openai"
            yield


@pytest.mark.asyncio
async def test_mock_provider_missing_config() -> None:
    """Test that MockProvider fails fast if temperature or max_tokens is missing."""
    provider = MockProvider(model_name="mock")

    with pytest.raises(ConfigurationError) as exc:
        await provider.generate(prompt="Hello", mock_identity="test_agent")

    assert "must be explicitly provided" in str(exc.value)


def test_llm_factory_create_mock() -> None:
    """Test that LLMFactory correctly instantiates a MockProvider."""
    provider = LLMFactory.create_provider(provider_type="mock", model_name="mock", limits={"tpm": 100, "rpm": 100})
    assert isinstance(provider, MockProvider)


def test_litellm_provider_init_missing_limits() -> None:
    """Test that LiteLLMProvider fails fast without explicit limits."""
    with pytest.raises(ConfigurationError) as exc:
        LiteLLMProvider(model_name="gemini/gemini-1.5-pro")
    assert "No hardcoded defaults allowed" in str(exc.value)


def test_litellm_provider_init_missing_tpm() -> None:
    """Test that LiteLLMProvider fails fast without explicit tpm limits."""
    with pytest.raises(ConfigurationError) as exc:
        LiteLLMProvider(model_name="gemini/gemini-1.5-pro", limits={"rpm": 100})
    assert "Both TPM and RPM must be defined" in str(exc.value)


def test_litellm_provider_init_success() -> None:
    """Test successful initialization of LiteLLMProvider."""
    provider = LiteLLMProvider(model_name="gemini/gemini-1.5-pro", limits={"tpm": 100, "rpm": 100})
    assert provider.model_name == "gemini/gemini-1.5-pro"
    assert provider.router is not None


@pytest.mark.asyncio
async def test_litellm_generate_missing_config() -> None:
    """Test that LiteLLMProvider.generate enforces temperature and max_tokens parameters."""
    provider = LiteLLMProvider(model_name="gemini/gemini-1.5-pro", limits={"tpm": 100, "rpm": 100})
    with pytest.raises(ConfigurationError) as exc:
        await provider.generate(prompt="Hello")
    assert "temperature" in str(exc.value).lower()


@pytest.mark.asyncio
@patch("backend_v2.llm.provider.os.getenv")
async def test_litellm_generate_success(mock_getenv: MagicMock) -> None:
    """Test LiteLLMProvider successfully generates content via router acompletion."""
    mock_getenv.return_value = "us-central1"
    mock_settings = MagicMock()
    mock_settings.llm_default_timeout = 30
    mock_settings.default_safety_settings = None

    provider = LiteLLMProvider(
        model_name="gemini/gemini-1.5-pro", limits={"tpm": 100, "rpm": 100}, settings=mock_settings
    )

    # Mocking LiteLLM router acompletion
    provider.router.acompletion = AsyncMock()

    mock_choice = MagicMock()
    mock_choice.message.content = "Simulated response"
    mock_choice.message.provider_specific_fields = None
    mock_choice.message.tool_calls = None
    mock_choice.finish_reason = "stop"

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_response.system_fingerprint = None
    mock_response.model_extra = {}
    mock_response.model_dump.return_value = {}
    
    mock_response.usage = {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}

    provider.router.acompletion.return_value = mock_response

    with patch("backend_v2.llm.provider.litellm.completion_cost", return_value=0.01):
        resp = await provider.generate(prompt="Hello", max_tokens=100, temperature=0.0)

    assert resp.content == "Simulated response"


def test_llm_factory_create_litellm() -> None:
    """Test LLMFactory explicitly creating LiteLLMProvider."""
    provider = LLMFactory.create_provider(
        provider_type="litellm", model_name="gpt-4o", limits={"tpm": 100, "rpm": 100}, api_key="fake_key"
    )
    assert isinstance(provider, LiteLLMProvider)
    assert provider.api_key == "fake_key"


def test_llm_factory_missing_model_name() -> None:
    """Test LLMFactory fails if model name is missing for non-mock providers."""
    with pytest.raises(ConfigurationError):
        LLMFactory.create_provider(provider_type="litellm", model_name="", limits={"tpm": 100, "rpm": 100})


def test_llm_factory_with_config() -> None:
    """Test LLMFactory reading values from LLMProviderConfig properly."""
    config = LLMProviderConfig(
        id="prov_config123456",
        provider="litellm",
        model_name="gpt-4o",
        is_active=True,
        tpm_limit=500,
        rpm_limit=500,
        api_key="config_key",
    )
    provider = LLMFactory.create_provider(provider_type="ignore", model_name="ignore", config=config)
    assert isinstance(provider, LiteLLMProvider)
    assert provider.api_key == "config_key"


def test_llm_factory_grounding_unsupported() -> None:
    """Test LLMFactory explicitly blocking grounding feature if not supported."""
    config = LLMProviderConfig(
        id="prov_config123456",
        provider="litellm",
        model_name="gpt-4o",
        is_active=True,
        tpm_limit=500,
        rpm_limit=500,
        api_key="config_key",
        supports_grounding=False,
    )
    with pytest.raises(ConfigurationError) as exc:
        LLMFactory.create_provider(provider_type="ignore", model_name="ignore", config=config, enable_grounding=True)
    assert "supports_grounding' is False" in str(exc.value)

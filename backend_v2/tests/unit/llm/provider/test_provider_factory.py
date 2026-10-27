"""Unit tests for LLMFactory provider resolution, credential validation, and Fail-Fast errors."""

from __future__ import annotations

import logging
import sys

import pytest

import backend_v2.llm.provider.provider_factory as factory_mod
from backend_v2.exceptions import ConfigurationError, ErrorCodes, ServiceUnavailableError
from backend_v2.llm.provider import LiteLLMProvider
from backend_v2.llm.provider.base_and_mock_provider import MockProvider
from backend_v2.llm.provider.provider_factory import LLMFactory
from backend_v2.models.llm import LLMProviderConfig
from backend_v2.settings import Settings


def test_llm_factory_create_provider_missing_api_key_raises_configuration_error(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verifies that LLMFactory.create_provider logs an RFC 7807 error and raises ConfigurationError when required provider API keys are missing."""
    empty_key_settings = Settings(
        use_mock_llm=False,
        google_api_key=None,
        openai_api_key=None,
        anthropic_api_key=None,
        vertex_location="europe-north1",
        discovery_location="us-central1",
        storage_backend="LOCAL",
    )
    monkeypatch.setattr(factory_mod, "get_settings", lambda: empty_key_settings)

    for provider_name, model_name, expected_key_name in (
        ("ai_studio", "gemini/gemini-2.5-flash", "GEMINI_API_KEY"),
        ("openai", "openai/gpt-5.1", "OPENAI_API_KEY"),
        ("anthropic", "anthropic/claude-3-7-sonnet", "ANTHROPIC_API_KEY"),
    ):
        caplog.clear()
        with caplog.at_level(logging.ERROR), pytest.raises(ConfigurationError) as exc_info:
            LLMFactory.create_provider(
                provider_name,
                model_name,
                limits={"tpm": 1000, "rpm": 10},
            )
        assert expected_key_name in str(exc_info.value)
        assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value
        assert expected_key_name in caplog.text


def test_llm_factory_create_provider_config_authority_and_capabilities(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify LLMFactory.create_provider enforces config authority, grounding checks, and mock overrides."""
    configured_settings = Settings(
        use_mock_llm=False,
        google_api_key="g-key",
        openai_api_key="o-key",
        anthropic_api_key="a-key",
        vertex_location="europe-north1",
        discovery_location="us-central1",
        storage_backend="LOCAL",
    )
    monkeypatch.setattr(factory_mod, "get_settings", lambda: configured_settings)

    # 1. Disabled config raises ServiceUnavailableError
    disabled_cfg = LLMProviderConfig(
        id="prv_disabled01",
        provider="openai",
        model_name="openai/gpt-5.1",
        is_active=False,
        tpm_limit=1000,
        rpm_limit=10,
    )
    with pytest.raises(ServiceUnavailableError) as disabled_exc:
        LLMFactory.create_provider("openai", "openai/gpt-5.1", config=disabled_cfg)
    assert disabled_exc.value.details["error_code"] == ErrorCodes.SERVICE_DISABLED.value

    # 2. Grounding requested via enable_grounding or google_search tool when supports_grounding=False
    ungrounded_cfg = LLMProviderConfig(
        id="prv_noground01",
        provider="openai",
        model_name="openai/gpt-5.1",
        supports_grounding=False,
        tpm_limit=1000,
        rpm_limit=10,
    )
    with pytest.raises(ConfigurationError) as ground_exc:
        LLMFactory.create_provider(
            "openai",
            "openai/gpt-5.1",
            config=ungrounded_cfg,
            tools=[{"google_search": {}}],
        )
    assert ground_exc.value.details["error_code"] == ErrorCodes.CAPABILITY_NOT_SUPPORTED.value

    # 3. Active config populates limits and explicit api_key
    active_cfg = LLMProviderConfig(
        id="prv_active0001",
        provider="openai",
        model_name="openai/gpt-5.1",
        api_key="cfg-override-key",
        tpm_limit=50000,
        rpm_limit=50,
    )
    created_from_cfg = LLMFactory.create_provider("openai", "ignored", config=active_cfg)
    assert isinstance(created_from_cfg, LiteLLMProvider)
    assert created_from_cfg.api_key == "cfg-override-key"
    assert created_from_cfg.model_name == "openai/gpt-5.1"

    # 4. Vertex AI clears resolved_api_key (uses ADC)
    vertex_prov = LLMFactory.create_provider(
        "vertex_ai",
        "vertex_ai/gemini-2.5-flash",
        api_key="should-be-cleared",
        limits={"tpm": 10000, "rpm": 20},
    )
    assert isinstance(vertex_prov, LiteLLMProvider)
    assert vertex_prov.api_key is None

    # 5. AI Studio, Anthropic, LiteLLM, and fallback provider branches
    for prov_type, model_id, expected_key in (
        ("ai_studio", "gemini/gemini-2.5-flash", "g-key"),
        ("anthropic", "anthropic/claude-3-7-sonnet", "a-key"),
        ("litellm", "ollama/llama3", None),
        ("deepseek", "deepseek/deepseek-chat", "custom-ds-key"),
    ):
        inst = LLMFactory.create_provider(
            prov_type,
            model_id,
            api_key="custom-ds-key" if prov_type == "deepseek" else None,
            limits={"tpm": 10000, "rpm": 20},
        )
        assert isinstance(inst, LiteLLMProvider)
        assert inst.api_key == expected_key

    # 6. Empty model_name raises ConfigurationError
    with pytest.raises(ConfigurationError):
        LLMFactory.create_provider("openai", "")

    # 7. Explicit mock provider_type and global use_mock_llm=True
    explicit_mock = LLMFactory.create_provider("mock", "mock-custom")
    assert isinstance(explicit_mock, MockProvider)

    mock_mode_settings = configured_settings.model_copy(update={"use_mock_llm": True})
    monkeypatch.setattr(factory_mod, "get_settings", lambda: mock_mode_settings)
    forced_mock = LLMFactory.create_provider("vertex_ai", "")
    assert isinstance(forced_mock, MockProvider)
    assert forced_mock.model_name == "mock"

    # 8. Missing LiteLLMProvider registration raises ConfigurationError
    monkeypatch.setattr(factory_mod, "get_settings", lambda: configured_settings)
    provider_mod = sys.modules["backend_v2.llm.provider"]
    monkeypatch.delattr(provider_mod, "LiteLLMProvider")
    with pytest.raises(ConfigurationError) as missing_cls_exc:
        LLMFactory.create_provider("openai", "openai/gpt-5.1", limits={"tpm": 1000, "rpm": 10})
    assert "LiteLLMProvider class is not registered" in str(missing_cls_exc.value)


# Phase 4, Step 1: Migrate test_llm_factory_create_provider_edge_cases from test_provider.py
def test_llm_factory_create_provider_edge_cases(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test LLMFactory.create_provider branches and validations via facade patch targets."""
    settings = Settings(
        use_mock_llm=False,
        google_api_key="fake-google-key",
        openai_api_key="fake-openai-key",
        anthropic_api_key="fake-anthropic-key",
        vertex_location="europe-north1",
        discovery_location="us-central1",
        storage_backend="LOCAL",
    )
    monkeypatch.setattr("backend_v2.llm.provider.get_settings", lambda: settings)

    inactive_config = LLMProviderConfig(
        id="prv_inactive",
        provider="openai",
        model_name="gpt-4o",
        is_active=False,
        tpm_limit=1000,
        rpm_limit=100,
    )
    with pytest.raises(ServiceUnavailableError):
        LLMFactory.create_provider("openai", "gpt-4o", config=inactive_config)

    no_ground_config = LLMProviderConfig(
        id="prv_noground",
        provider="openai",
        model_name="gpt-4o",
        supports_grounding=False,
        tpm_limit=1000,
        rpm_limit=100,
    )
    with pytest.raises(ConfigurationError):
        LLMFactory.create_provider("openai", "gpt-4o", config=no_ground_config, enable_grounding=True)

    with_key_config = LLMProviderConfig(
        id="prv_withkey0001",
        provider="openai",
        model_name="gpt-4o",
        api_key="explicit_key",
        tpm_limit=5000,
        rpm_limit=500,
    )
    prov_key = LLMFactory.create_provider("openai", "gpt-4o", config=with_key_config)
    assert isinstance(prov_key, LiteLLMProvider)
    assert prov_key.api_key == "explicit_key"

    mock_settings = Settings(
        use_mock_llm=True,
        vertex_location="europe-north1",
        discovery_location="us-central1",
        storage_backend="LOCAL",
    )
    monkeypatch.setattr("backend_v2.llm.provider.get_settings", lambda: mock_settings)
    prov = LLMFactory.create_provider("openai", "gpt-4o")
    assert isinstance(prov, MockProvider)

    monkeypatch.setattr("backend_v2.llm.provider.get_settings", lambda: settings)
    prov_mock = LLMFactory.create_provider("mock", "custom-mock")
    assert isinstance(prov_mock, MockProvider)

    with pytest.raises(ConfigurationError):
        LLMFactory.create_provider("openai", model_name="")

    prov_vertex = LLMFactory.create_provider("vertex_ai", "vertex_ai/gemini-1.5-pro", limits={"tpm": 1000, "rpm": 100})
    assert isinstance(prov_vertex, LiteLLMProvider)
    assert prov_vertex.api_key is None

    for key_field, prov_type, model_id in (
        ("google_api_key", "ai_studio", "gemini-1.5-pro"),
        ("openai_api_key", "openai", "gpt-4o"),
        ("anthropic_api_key", "anthropic", "claude-3-5-sonnet"),
    ):
        missing_key_settings = settings.model_copy(update={key_field: None})
        monkeypatch.setattr("backend_v2.llm.provider.get_settings", lambda s=missing_key_settings: s)
        with pytest.raises(ConfigurationError):
            LLMFactory.create_provider(prov_type, model_id)

    monkeypatch.setattr("backend_v2.llm.provider.get_settings", lambda: settings)
    prov_openai = LLMFactory.create_provider("openai", "gpt-4o", limits={"tpm": 1000, "rpm": 100})
    assert isinstance(prov_openai, LiteLLMProvider)
    assert prov_openai.api_key == "fake-openai-key"

    prov_anthropic = LLMFactory.create_provider(
        "anthropic", "anthropic/claude-3-5-sonnet", limits={"tpm": 1000, "rpm": 100}
    )
    assert isinstance(prov_anthropic, LiteLLMProvider)
    assert prov_anthropic.api_key == "fake-anthropic-key"

    prov_ai_studio = LLMFactory.create_provider("ai_studio", "gemini/gemini-1.5-pro", limits={"tpm": 1000, "rpm": 100})
    assert isinstance(prov_ai_studio, LiteLLMProvider)
    assert prov_ai_studio.api_key == "fake-google-key"

    prov_litellm = LLMFactory.create_provider("litellm", "ollama/llama3", limits={"tpm": 1000, "rpm": 100})
    assert isinstance(prov_litellm, LiteLLMProvider)
    assert prov_litellm.model_name == "ollama/llama3"

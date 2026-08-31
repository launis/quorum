"""Unit tests for the seed registry."""

import pytest
from pydantic import ValidationError

from backend_v2.models.v2_core import (
    AllowedMCPTool,
    I18nText,
    LexiconConfigPayload,
    ModelProfile,
    SystemConfigMCPGateways,
    SystemConfigModelRegistry,
    SystemConfigPerformativeLexicons,
)
from backend_v2.seed.seed_registry import STANDARD_REGISTRY


def test_system_config_discriminator_mcp_gateways() -> None:
    """Tests the discriminator correctly resolves SystemConfigMCPGateways."""
    adapter = STANDARD_REGISTRY["system_config"]["model"]
    tool = AllowedMCPTool(
        tool_id="mcp_tavily_search",
        name=I18nText(translations={"en": "Tavily Search", "fi": "Tavily Haku"}),
        description="Search tool",
        input_schema={},
    )
    data = {
        "id": "cfg_0123456789abcdef",
        "type": "mcp_gateways",
        "tools": [tool.model_dump(mode="json")],
    }
    result = adapter.validate_python(data)
    assert isinstance(result, SystemConfigMCPGateways)
    assert result.type == "mcp_gateways"
    assert len(result.tools) == 1


def test_system_config_discriminator_model_registry() -> None:
    """Tests the discriminator correctly resolves SystemConfigModelRegistry."""
    adapter = STANDARD_REGISTRY["system_config"]["model"]
    profile = ModelProfile(
        model_name="gpt-4o",
        provider="openai",
    )
    data = {
        "id": "cfg_0123456789abcdef",
        "type": "model_registry",
        "models": {"primary": profile.model_dump(mode="json")},
    }
    result = adapter.validate_python(data)
    assert isinstance(result, SystemConfigModelRegistry)
    assert result.type == "model_registry"
    assert "primary" in result.models


def test_system_config_discriminator_performative_lexicons() -> None:
    """Tests the discriminator correctly resolves SystemConfigPerformativeLexicons."""
    adapter = STANDARD_REGISTRY["system_config"]["model"]
    lex_payload = LexiconConfigPayload(
        language_code="en",
        language_name="English",
        words=["test"],
    )
    data = {
        "id": "cfg_0123456789abcdef",
        "type": "performative_lexicons",
        "lexicon_configs": {"en": lex_payload.model_dump(mode="json")},
    }
    result = adapter.validate_python(data)
    assert isinstance(result, SystemConfigPerformativeLexicons)
    assert result.type == "performative_lexicons"
    assert "en" in result.lexicon_configs


def test_system_config_discriminator_missing_type_fails() -> None:
    """Tests that missing type discriminator tag triggers ValidationError."""
    adapter = STANDARD_REGISTRY["system_config"]["model"]
    data = {"id": "cfg_0123456789abcdef", "other": "value"}
    with pytest.raises(ValidationError):
        adapter.validate_python(data)


def test_system_config_discriminator_unknown_type_fails() -> None:
    """Tests that unknown type discriminator tag triggers ValidationError."""
    adapter = STANDARD_REGISTRY["system_config"]["model"]
    data = {"id": "cfg_0123456789abcdef", "type": "unknown_config_type"}
    with pytest.raises(ValidationError):
        adapter.validate_python(data)

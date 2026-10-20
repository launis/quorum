"""Tests for system_config domain models and DTOs."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.system_config import (
    AllowedMCPTool,
    ModelProfile,
    SystemConfigModelRegistry,
    SystemConfigOptionDTO,
    SystemValidationRulesDTO,
)
from backend_v2.models.enums import CognitiveTier, LaxCognitiveTier, ToolCapability


def test_system_validation_rules_dto_rejects_unknown_attribute() -> None:
    """Verify extra attributes are rejected by SystemValidationRulesDTO."""
    with pytest.raises(ValidationError):
        SystemValidationRulesDTO.model_validate({"unknown_rule": "bad"})


def test_system_validation_rules_dto_valid() -> None:
    """Verify valid SystemValidationRulesDTO instantiation."""
    rules = SystemValidationRulesDTO(min=1.0, max=10.0, required=True, pattern=r"^\d+$")
    assert rules.min == 1.0
    assert rules.max == 10.0
    assert rules.required is True
    assert rules.pattern == r"^\d+$"


def test_system_config_option_dto_valid() -> None:
    """Verify valid SystemConfigOptionDTO instantiation."""
    opt = SystemConfigOptionDTO(label="Opt1", value="val1")
    assert opt.label == "Opt1"
    assert opt.value == "val1"


def test_system_config_option_dto_rejects_unknown_attribute() -> None:
    """Verify extra attributes are rejected by SystemConfigOptionDTO."""
    with pytest.raises(ValidationError):
        SystemConfigOptionDTO.model_validate({"label": "Opt1", "value": "val1", "extra": "bad"})


def test_allowed_mcp_tool_valid_and_defaults() -> None:
    """Verify AllowedMCPTool defaults capability to SEARCH and accepts DOCUMENT_READER."""
    tool_default = AllowedMCPTool(
        tool_id="mcp_test_search",
        name=I18nText(translations={"fi": "Haku", "en": "Search"}),
        description="Search tool description.",
    )
    assert tool_default.capability == ToolCapability.SEARCH
    assert tool_default.tool_id == "mcp_test_search"

    tool_reader = AllowedMCPTool(
        tool_id="mcp_test_reader",
        capability=ToolCapability.DOCUMENT_READER,
        name=I18nText(translations={"fi": "Lukija", "en": "Reader"}),
        description="Reader tool description.",
    )
    assert tool_reader.capability == ToolCapability.DOCUMENT_READER


def test_allowed_mcp_tool_rejects_unknown_attribute() -> None:
    """Verify AllowedMCPTool enforces extra='forbid'."""
    with pytest.raises(ValidationError):
        AllowedMCPTool.model_validate(
            {
                "tool_id": "mcp_test",
                "name": {"translations": {"fi": "Testi", "en": "Test"}},
                "description": "Test tool",
                "extra_key": "forbidden",
            }
        )



def test_system_config_model_registry_missing_tier_raises_value_error() -> None:
    """Verify SystemConfigModelRegistry raises ValueError when cognitive tiers are incomplete."""
    incomplete_tiers: dict[LaxCognitiveTier, ModelProfile] = {
        CognitiveTier.FAST: ModelProfile(provider="google", model_name="gemini-2.5-flash"),
    }
    with pytest.raises(ValidationError) as exc_info:
        SystemConfigModelRegistry(
            id="sys_1234567890abcdef",
            name="Incomplete Registry",
            tier_definitions=incomplete_tiers,
        )
    assert "missing required cognitive tiers" in str(exc_info.value)



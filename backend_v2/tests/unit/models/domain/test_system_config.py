"""Tests for system_config domain models and DTOs."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.system_config import (
    SystemConfigOptionDTO,
    SystemValidationRulesDTO,
)


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

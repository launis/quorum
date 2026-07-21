from unittest.mock import AsyncMock
"""Unit tests for the seed registry."""

import pytest
from pydantic import BaseModel

from backend_v2.seed.seed_registry import _system_config_discriminator


def test_system_config_discriminator_dict() -> None:
    """Tests the discriminator function with a dictionary."""
    data = {"type": "mcp_gateways"}
    result = _system_config_discriminator(data)
    assert result == "mcp_gateways"


def test_system_config_discriminator_object() -> None:
    """Tests the discriminator function with an object."""

    class MockConfig(BaseModel):
        type: str

    obj = MockConfig(type="model_registry")
    result = _system_config_discriminator(obj)
    assert result == "model_registry"


def test_system_config_discriminator_missing_type_dict() -> None:
    """Tests the discriminator function with a dict missing the type key.
    Should fail-fast with KeyError.
    """
    data = {"other": "value"}
    with pytest.raises(KeyError):
        _system_config_discriminator(data)


def test_system_config_discriminator_missing_type_object() -> None:
    """Tests the discriminator function with an object missing the type attribute.
    Should fail-fast with AttributeError.
    """

    class MockConfig(BaseModel):
        other: str

    obj = MockConfig(other="value")
    with pytest.raises(AttributeError):
        _system_config_discriminator(obj)

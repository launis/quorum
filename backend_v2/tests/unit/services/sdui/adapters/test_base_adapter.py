"""Unit tests for the SDUI base adapter protocol and context."""

import pytest
from pydantic import ValidationError
from polyfactory.factories.pydantic_factory import ModelFactory

from backend_v2.models.v2_core import OutputProfile, I18nText
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext


@pytest.fixture
def valid_output_profile_fixture() -> OutputProfile:
    """Fixture for a valid output profile to use in tests."""
    return OutputProfile(
        id="prf_0123456789abcdef",
        slug="test-profile",
        workflow_id="wfw_test",
        name=I18nText(default_locale="en", translations={"en": "Test Profile"}),
        layouts=[],
    )


def test_adapter_context_valid_construction(valid_output_profile_fixture: OutputProfile) -> None:
    """Positive: Successfully creates a frozen AdapterContext instance."""
    context = AdapterContext(
        execution=None,
        locale="fi",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        accumulated_extensions={},
        profile=valid_output_profile_fixture,
        profile_cache=None,
    )
    assert context.locale == "fi"
    assert context.penalties_applied == []


def test_adapter_context_frozen_rejects_mutation(valid_output_profile_fixture: OutputProfile) -> None:
    """Negative: frozen model cannot be mutated."""
    context = AdapterContext(
        execution=None,
        locale="fi",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        accumulated_extensions={},
        profile=valid_output_profile_fixture,
        profile_cache=None,
    )
    with pytest.raises(ValidationError):
        context.locale = "en"  # type: ignore[misc]


def test_adapter_context_forbids_extra_fields(valid_output_profile_fixture: OutputProfile) -> None:
    """Negative: extra fields forbidden."""
    with pytest.raises(ValidationError) as exc_info:
        AdapterContext(
            execution=None,
            locale="fi",
            penalties_applied=[],
            mcp_audit_map=None,
            global_score=None,
            accumulated_extensions={},
            profile=valid_output_profile_fixture,
            profile_cache=None,
            unknown_field="hax",  # type: ignore[call-arg]
        )
    assert "Extra inputs are not permitted" in str(exc_info.value)


def test_adapter_context_missing_required_field_raises() -> None:
    """Error path: missing required fields."""
    with pytest.raises(ValidationError) as exc_info:
        AdapterContext(
            locale="fi",  # type: ignore[call-arg]
        )
    assert "Field required" in str(exc_info.value)


def test_adapter_context_strict_type_enforcement(valid_output_profile_fixture: OutputProfile) -> None:
    """Boundary: strict=True enforces type."""
    with pytest.raises(ValidationError) as exc_info:
        AdapterContext(
            execution=None,
            locale=123,  # type: ignore[arg-type]
            penalties_applied=[],
            mcp_audit_map=None,
            global_score=None,
            accumulated_extensions={},
            profile=valid_output_profile_fixture,
            profile_cache=None,
        )
    assert "Input should be a valid string" in str(exc_info.value)

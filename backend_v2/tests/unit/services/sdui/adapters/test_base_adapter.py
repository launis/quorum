"""Unit tests for the SDUI base adapter protocol and context."""

import pytest
from pydantic import ValidationError

from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.synthesis import RenderedSynthesisCache
from backend_v2.models.dtos.base import DataStarvationEvent
from backend_v2.models.view.sdui import AnySduiBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext, SduiAdapterProtocol


@pytest.fixture
def valid_output_profile_fixture() -> OutputProfile:
    """Fixture for a valid output profile to use in tests."""
    return OutputProfile(
        id="prf_0195f3a0000070008123456789abcdef",
        slug="test-profile",
        workflow_id="wfw_test",
        name=I18nText(translations={"en": "Test Profile"}),
        target_block_order=[],
    )


def test_adapter_context_valid_construction(valid_output_profile_fixture: OutputProfile) -> None:
    """Positive: Successfully creates a frozen AdapterContext instance."""
    context = AdapterContext(
        execution=None,
        locale="fi",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=valid_output_profile_fixture,
        profile_cache=None,
        user_name=None,
        org_name=None,
    )
    assert context.locale == "fi"
    assert context.penalties_applied == []
    assert context.parsed_matrices == {}
    assert context.mcp_tools_map == {}
    assert context.is_data_starved is False


def test_adapter_context_frozen_rejects_mutation(valid_output_profile_fixture: OutputProfile) -> None:
    """Negative: frozen model cannot be mutated."""
    context = AdapterContext(
        execution=None,
        locale="fi",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=valid_output_profile_fixture,
        profile_cache=None,
        user_name=None,
        org_name=None,
    )
    with pytest.raises(ValidationError):
        context.locale = "en"


def test_adapter_context_forbids_extra_fields(valid_output_profile_fixture: OutputProfile) -> None:
    """Negative: extra fields forbidden."""
    with pytest.raises(ValidationError) as exc_info:
        AdapterContext.model_validate(
            {
                "execution": None,
                "locale": "fi",
                "penalties_applied": [],
                "mcp_audit_map": None,
                "global_score": None,
                "profile": valid_output_profile_fixture,
                "profile_cache": None,
                "user_name": None,
                "org_name": None,
                "unknown_field": "hax",
            }
        )
    assert "Extra inputs are not permitted" in str(exc_info.value)


def test_adapter_context_missing_required_field_raises() -> None:
    """Error path: missing required fields."""
    with pytest.raises(ValidationError) as exc_info:
        AdapterContext.model_validate(
            {
                "locale": "fi",
            }
        )
    assert "Field required" in str(exc_info.value)


def test_adapter_context_strict_type_enforcement(valid_output_profile_fixture: OutputProfile) -> None:
    """Boundary: strict=True enforces type."""
    with pytest.raises(ValidationError) as exc_info:
        AdapterContext.model_validate(
            {
                "execution": None,
                "locale": 123,
                "penalties_applied": [],
                "mcp_audit_map": None,
                "global_score": None,
                "profile": valid_output_profile_fixture,
                "profile_cache": None,
                "user_name": None,
                "org_name": None,
            }
        )
    assert "Input should be a valid string" in str(exc_info.value)


def test_adapter_context_is_data_starved_predicate(valid_output_profile_fixture: OutputProfile) -> None:
    """Verifies is_data_starved predicate under starved and non-starved scenarios."""
    starved_cache = RenderedSynthesisCache(
        data_starvation=DataStarvationEvent(
            total_atoms=0,
            reason="Data starvation: insufficient atoms",
        )
    )
    starved_context = AdapterContext(
        execution=None,
        locale="fi",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=valid_output_profile_fixture,
        profile_cache=starved_cache,
        user_name=None,
        org_name=None,
    )
    assert starved_context.is_data_starved is True

    normal_cache = RenderedSynthesisCache(data_starvation=None)
    normal_context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=valid_output_profile_fixture,
        profile_cache=normal_cache,
        user_name=None,
        org_name=None,
    )
    assert normal_context.is_data_starved is False


def test_sdui_adapter_protocol_conformance(valid_output_profile_fixture: OutputProfile) -> None:
    """Verifies that concrete classes satisfy SduiAdapterProtocol static build contract."""

    class MockAdapter:
        @staticmethod
        def build(context: AdapterContext) -> list[AnySduiBlock]:
            return []

    assert issubclass(MockAdapter, SduiAdapterProtocol)
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=valid_output_profile_fixture,
        profile_cache=None,
        user_name=None,
        org_name=None,
    )
    assert MockAdapter.build(context) == []

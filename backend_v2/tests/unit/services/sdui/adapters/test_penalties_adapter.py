"""Unit tests for the Penalties SDUI adapter."""

import pytest

from backend_v2.models.enums import VisualIntent
from backend_v2.models.v2_core import I18nText, OutputProfile
from backend_v2.models.view.sdui import AlertBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.penalties_adapter import PenaltiesAdapter


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


def test_build_tampered_rules_dictionary_raises_keyerror(
    valid_output_profile_fixture: OutputProfile, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Negative: Fail-Fast dictionary access raises KeyError if unmapped."""
    monkeypatch.setattr("backend_v2.services.sdui.adapters.penalties_adapter.PENALTIES_RULES", {})
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=["Test Penalty"],
        mcp_audit_map=None,
        global_score=None,
        accumulated_extensions={},
        profile=valid_output_profile_fixture,
        profile_cache=None,
    )
    with pytest.raises(KeyError):
        PenaltiesAdapter.build(context)


def test_build_empty_list_returns_empty(valid_output_profile_fixture: OutputProfile) -> None:
    """Boundary: empty penalties_applied returns empty list."""
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        accumulated_extensions={},
        profile=valid_output_profile_fixture,
        profile_cache=None,
    )
    blocks = PenaltiesAdapter.build(context)
    assert blocks == []


def test_build_valid_penalties_returns_alert_blocks(valid_output_profile_fixture: OutputProfile) -> None:
    """Positive: valid penalties_applied returns AlertBlocks."""
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=["Test Penalty 1", "Test Penalty 2"],
        mcp_audit_map=None,
        global_score=None,
        accumulated_extensions={},
        profile=valid_output_profile_fixture,
        profile_cache=None,
    )
    blocks = PenaltiesAdapter.build(context)
    assert len(blocks) == 2
    assert isinstance(blocks[0], AlertBlock)
    assert blocks[0].severity == VisualIntent.CRITICAL_OVERRIDE
    assert blocks[0].text == "Penalty applied: Test Penalty 1"
    assert blocks[1].text == "Penalty applied: Test Penalty 2"

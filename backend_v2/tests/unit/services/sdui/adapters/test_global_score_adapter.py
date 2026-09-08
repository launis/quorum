"""Unit tests for the GlobalScoreAdapter SDUI adapter."""

import pytest

from backend_v2.models.v2_core import DataStarvationEvent, I18nText, OutputProfile, RenderedSynthesisCache
from backend_v2.models.view.sdui import SduiScoreCardBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.global_score_adapter import GlobalScoreAdapter


@pytest.fixture
def sample_profile() -> OutputProfile:
    """Fixture providing a valid OutputProfile for testing."""
    return OutputProfile(
        id="prf_0123456789abcdef",
        slug="test-profile",
        workflow_id="wfw_test",
        name=I18nText(translations={"en": "Test Profile"}),
        target_block_order=[],
    )


def test_build_returns_score_card_block_when_global_score_present(sample_profile: OutputProfile) -> None:
    """Positive: returns SduiScoreCardBlock with correct global score."""
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=88.5,
        profile=sample_profile,
        profile_cache=None,
        user_name=None,
        org_name=None,
    )
    blocks = GlobalScoreAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], SduiScoreCardBlock)
    assert blocks[0].global_score == 88.5


def test_build_returns_empty_when_global_score_is_none(sample_profile: OutputProfile) -> None:
    """Negative: returns empty list when global_score is None."""
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=sample_profile,
        profile_cache=None,
        user_name=None,
        org_name=None,
    )
    blocks = GlobalScoreAdapter.build(context)
    assert blocks == []


def test_build_returns_empty_when_data_starved(sample_profile: OutputProfile) -> None:
    """Negative: returns empty list when context is data starved even with global_score."""
    starved_cache = RenderedSynthesisCache(
        data_starvation=DataStarvationEvent(total_atoms=0, reason="insufficient_tokens")
    )
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=92.0,
        profile=sample_profile,
        profile_cache=starved_cache,
        user_name=None,
        org_name=None,
    )
    assert context.is_data_starved is True
    blocks = GlobalScoreAdapter.build(context)
    assert blocks == []


def test_build_boundary_scores(sample_profile: OutputProfile) -> None:
    """Boundary: correctly builds blocks for extrema scores 0.0 and 100.0."""
    for score in (0.0, 100.0):
        context = AdapterContext(
            execution=None,
            locale="fi",
            penalties_applied=[],
            mcp_audit_map=None,
            global_score=score,
            profile=sample_profile,
            profile_cache=None,
            user_name=None,
            org_name=None,
        )
        assert context.is_data_starved is False
        blocks = GlobalScoreAdapter.build(context)
        assert len(blocks) == 1
        assert isinstance(blocks[0], SduiScoreCardBlock)
        assert blocks[0].global_score == score

"""Unit tests for the McpAuditAdapter SDUI adapter."""

import pytest

from backend_v2.models.v2_core import (
    DataStarvationEvent,
    I18nText,
    MCPAuditTrace,
    OutputProfile,
    RenderedSynthesisCache,
)
from backend_v2.models.view.sdui import SduiAuditTrailBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.mcp_audit_adapter import McpAuditAdapter


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


@pytest.fixture
def sample_trace() -> MCPAuditTrace:
    """Fixture providing a valid MCPAuditTrace for testing."""
    return MCPAuditTrace(
        tool_id="search_tool",
        step_name="step_fact_check",
        query="quorum consensus protocol",
    )


def test_build_returns_audit_trail_block_when_mcp_audit_map_populated(
    sample_profile: OutputProfile, sample_trace: MCPAuditTrace
) -> None:
    """Positive: returns SduiAuditTrailBlock when mcp_audit_map is non-empty."""
    cache = RenderedSynthesisCache()
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map={"gateway_1": sample_trace},
        global_score=None,
        profile=sample_profile,
        profile_cache=cache,
        user_name=None,
        org_name=None,
    )
    assert context.is_data_starved is False
    blocks = McpAuditAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], SduiAuditTrailBlock)


def test_build_returns_empty_when_mcp_audit_map_is_empty(sample_profile: OutputProfile) -> None:
    """Negative: returns empty list when mcp_audit_map is empty dict."""
    cache = RenderedSynthesisCache()
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map={},
        global_score=None,
        profile=sample_profile,
        profile_cache=cache,
        user_name=None,
        org_name=None,
    )
    blocks = McpAuditAdapter.build(context)
    assert blocks == []


def test_build_returns_empty_when_mcp_audit_map_is_none(sample_profile: OutputProfile) -> None:
    """Negative: returns empty list when mcp_audit_map is None."""
    cache = RenderedSynthesisCache()
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=sample_profile,
        profile_cache=cache,
        user_name=None,
        org_name=None,
    )
    blocks = McpAuditAdapter.build(context)
    assert blocks == []


def test_build_returns_empty_when_data_starved(sample_profile: OutputProfile, sample_trace: MCPAuditTrace) -> None:
    """Negative: returns empty list when context is data starved."""
    starved_cache = RenderedSynthesisCache(
        data_starvation=DataStarvationEvent(total_atoms=0, reason="insufficient_tokens")
    )
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map={"gateway_1": sample_trace},
        global_score=None,
        profile=sample_profile,
        profile_cache=starved_cache,
        user_name=None,
        org_name=None,
    )
    assert context.is_data_starved is True
    blocks = McpAuditAdapter.build(context)
    assert blocks == []

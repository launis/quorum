"""Live integration tests for Tavily AI Search and Source Verification Hook.

Verifies end-to-end integration with live external Tavily search endpoints
and full pipeline execution across TavilyClient, MCP Tool Loop, and SourceVerificationHook.
"""

import _socket
import socket
from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.core.hook_registry import ExecutionInputsDTO, HookDependencies, HookState
from backend_v2.database.factory import get_driver
from backend_v2.database.repositories.system import SystemRepositoryImpl
from backend_v2.exceptions import ConfigurationError
from backend_v2.models.domain.mcp import TavilySearchResult
from backend_v2.models.v2_core import MCPAuditTrace
from backend_v2.services.mcp.mcp_tool_loop import DISPATCHER
from backend_v2.services.mcp.tavily_search_client import tavily_search
from backend_v2.services.mcp.tools.tavily import TAVILY_TOOL_ID
from backend_v2.settings import get_settings


@pytest.fixture(autouse=True)
def allow_live_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Restores unblocked C-level socket getaddrinfo for live integration tests.

    Args:
        monkeypatch: Pytest monkeypatch fixture.
    """
    monkeypatch.setattr(socket, "getaddrinfo", _socket.getaddrinfo)


@pytest.mark.asyncio
async def test_live_tavily_search_client() -> None:
    """Executes a live search via Tavily AI client and verifies returned payload structure."""
    settings = get_settings()
    if not settings.tavily_api_key:
        pytest.skip("TAVILY_API_KEY is not configured in environment.")

    query = "What is the capital of Finland?"
    result: TavilySearchResult = await tavily_search(query)

    assert isinstance(result, TavilySearchResult)
    assert result.query == query
    assert result.answer is not None and len(result.answer.strip()) > 0
    assert "Helsinki" in result.answer or "Helsinki" in result.raw_content
    assert len(result.source_urls) >= 1
    assert all(url.startswith("http") for url in result.source_urls)
    assert result.duration_ms > 0


@pytest.mark.asyncio
async def test_live_tavily_mcp_tool_dispatcher() -> None:
    """Executes a live search via DISPATCHER and verifies MCPAuditTrace structure."""
    settings = get_settings()
    if not settings.tavily_api_key:
        pytest.skip("TAVILY_API_KEY is not configured in environment.")

    query = "Albert Einstein Nobel Prize in Physics year 1921"
    claim = "Albert Einstein received the Nobel Prize in Physics in 1921."

    audit_trace: MCPAuditTrace = await DISPATCHER.execute_tool(
        tool_id=TAVILY_TOOL_ID,
        query=query,
        step_name="test_live_step",
        target_language="en",
        claim_text=claim,
    )

    assert isinstance(audit_trace, MCPAuditTrace)
    assert audit_trace.tool_id == TAVILY_TOOL_ID
    assert audit_trace.step_name == "test_live_step"
    assert audit_trace.claim_text == claim
    assert audit_trace.query == query
    assert len(audit_trace.source_urls) >= 1
    assert all(url.startswith("http") for url in audit_trace.source_urls)
    assert audit_trace.response_summary is not None and len(audit_trace.response_summary) > 0
    assert audit_trace.duration_ms > 0


@pytest.mark.asyncio
async def test_live_source_verification_hook_pipeline() -> None:
    """Executes the full source_verification_hook pipeline with real LLM and live Tavily search."""
    settings = get_settings()
    if not settings.tavily_api_key:
        pytest.skip("TAVILY_API_KEY is not configured in environment.")

    from backend_v2.hooks.source_verification_hook import source_verification_hook

    driver = await get_driver(settings)
    system_repo = SystemRepositoryImpl(driver)

    document_text = (
        "According to the World Health Organization (WHO), regular physical activity "
        "reduces the risk of cardiovascular diseases and adults should do at least 150 minutes "
        "of moderate-intensity aerobic physical activity throughout the week."
    )

    state = HookState(
        execution_id="exe_live_test_0001",
        workflow_id="wor_live_test_0001",
        step_id="sp_76eedbc020274f66",
        metadata={"target_locale": "fi"},
        global_context_vars={},
        inputs=ExecutionInputsDTO(dynamic_inputs={"document_text": document_text}),
    )
    deps = HookDependencies(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=system_repo,
    )

    result = await source_verification_hook(state=state, deps=deps)

    assert result.success is True
    assert result.state_delta is not None
    assert result.state_delta.metadata_updates is not None

    metadata_dict = result.state_delta.metadata_updates
    assert isinstance(metadata_dict, dict)
    assert "mcp_audit_traces" in metadata_dict

    traces = metadata_dict["mcp_audit_traces"]
    assert isinstance(traces, list)
    assert len(traces) >= 1

    first_trace = traces[0]
    assert isinstance(first_trace, dict)
    assert first_trace["tool_id"] == "mcp_tavily_search"
    assert isinstance(first_trace["source_urls"], list)
    assert len(first_trace["source_urls"]) >= 1

    assert "external_evidence" in result.state_delta.delta
    evidence_xml = result.state_delta.delta["external_evidence"]
    assert isinstance(evidence_xml, str)
    assert "<external_evidence>" in evidence_xml
    assert "</external_evidence>" in evidence_xml
    assert "<claim status=" in evidence_xml


@pytest.mark.asyncio
async def test_live_tavily_search_missing_key_fail_fast() -> None:
    """Ensures ConfigurationError is raised when API key is missing."""
    with patch("backend_v2.services.mcp.tavily_search_client.get_settings") as mock_get:
        mock_get.return_value.tavily_api_key = None
        with pytest.raises(ConfigurationError) as exc_info:
            await tavily_search("Test query without key")
        assert "Tavily API key is not configured" in str(exc_info.value)

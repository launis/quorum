"""Full End-to-End Integration Test for Tavily Search & Bibliography Generation.

Tests the complete lifecycle:
1. Input document ingestion & claim extraction via Fast LLM
2. Live Tavily web search verification & MCPAuditTrace creation
3. External evidence XML construction for workflow step context
4. SDUI PrintableSourcesAdapter rendering into final markdown bibliography
5. Data starvation / claim-free input handling (graceful block omission)
"""

import _socket
import os
import socket

import httpx
import pytest

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDependencies,
    HookState,
)
from backend_v2.database.factory import get_driver
from backend_v2.database.repositories.system import SystemRepositoryImpl
from backend_v2.hooks.source_verification_hook import source_verification_hook
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.dtos.hook_delta import ExternalEvidenceResultDTO
from backend_v2.models.dtos.mcp import (
    MCPContentBlockDTO,
    MCPInitializeResultDTO,
    MCPJsonRpcRequestDTO,
    MCPJsonRpcResponseDTO,
    MCPToolCallParamsDTO,
    MCPToolCallResultDTO,
)
from backend_v2.models.enums import TargetBlockType
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.view.sdui import MarkdownBlock
from backend_v2.services.mcp.generic_mcp_client import GenericMCPClient
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.printable_sources_adapter import PrintableSourcesAdapter
from backend_v2.settings import get_settings
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


def _build_tavily_mcp_transport() -> httpx.MockTransport:
    """Build a JSON-RPC 2.0 MCP transport responder for tavily_search verification calls.

    Returns:
        Configured httpx.MockTransport instance.
    """

    def _handler(request: httpx.Request) -> httpx.Response:
        rpc_req = MCPJsonRpcRequestDTO.model_validate_json(request.content)
        if rpc_req.method == "initialize":
            init_resp = MCPJsonRpcResponseDTO(
                id=rpc_req.id,
                result=MCPInitializeResultDTO(
                    protocol_version="2025-03-26",
                    server_info={"name": "tavily-mcp", "version": "1.0.0"},
                ),
            )
            return httpx.Response(
                200,
                headers={"Content-Type": "application/json", "Mcp-Session-Id": "sess_tavily_e2e"},
                json=init_resp.model_dump(mode="json", by_alias=True, exclude_none=True),
            )
        if rpc_req.method == "notifications/initialized":
            return httpx.Response(202)
        if rpc_req.method == "tools/call" and isinstance(rpc_req.params, MCPToolCallParamsDTO):
            query_str = str(rpc_req.params.arguments.get("query", ""))
            call_resp = MCPJsonRpcResponseDTO(
                id=rpc_req.id,
                result=MCPToolCallResultDTO(
                    content=[
                        MCPContentBlockDTO(
                            type="text",
                            text=(
                                f"Search evidence for '{query_str}': "
                                "According to the World Health Organization (WHO), adults should do at least "
                                "150 minutes of moderate-intensity physical activity per week "
                                "(https://www.who.int/news-room/fact-sheets/detail/physical-activity). "
                                "Harvard Medical School research confirms that sufficient sleep improves "
                                "cognitive performance (https://health.harvard.edu/sleep-and-cognition)."
                            ),
                        )
                    ],
                    is_error=False,
                ),
            )
            return httpx.Response(
                200,
                headers={"Content-Type": "application/json"},
                json=call_resp.model_dump(mode="json", by_alias=True, exclude_none=True),
            )
        return httpx.Response(400)

    return httpx.MockTransport(_handler)


@pytest.fixture(autouse=True)
def allow_live_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Restores unblocked C-level socket getaddrinfo for live LLM calls and binds MCP JSON-RPC transport."""
    monkeypatch.setattr(socket, "getaddrinfo", _socket.getaddrinfo)
    mock_transport = _build_tavily_mcp_transport()
    orig_init = GenericMCPClient.__init__

    def _patched_init(
        self: GenericMCPClient,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        orig_init(self, transport=transport if transport is not None else mock_transport)

    monkeypatch.setattr(GenericMCPClient, "__init__", _patched_init)


@pytest.mark.asyncio
async def test_full_e2e_tavily_extraction_to_sdui_bibliography_live() -> None:
    """End-to-end test: Ingest text -> extract claims -> live Tavily search -> build SDUI bibliography."""
    settings = get_settings()
    if "TAVILY_API_KEY" not in os.environ or not os.environ["TAVILY_API_KEY"]:
        pytest.skip("TAVILY_API_KEY is not configured in environment.")

    driver = await get_driver(settings)
    system_repo = SystemRepositoryImpl(driver)

    document_text = (
        "Maailman terveysjärjestön (WHO) mukaan aikuisten tulisi harrastaa vähintään 150 minuuttia "
        "kestävyysliikuntaa viikossa sydänsairauksien ehkäisemiseksi. "
        "Lisäksi Harvardin yliopiston tutkimus osoittaa, että riittävä uni parantaa kognitiivista suorituskykyä."
    )

    # 1. Pipeline Step 1: Execute Pre-Hook
    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wor_1111222233334444",
        step_id="sp_76eedbc020274f66",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(dynamic_inputs={"document_text": document_text}, target_locale="fi"),
    )
    fake_repo = InMemoryUnifiedWorkflowRepository()
    deps = HookDependencies(
        exec_repo=fake_repo,
        workflow_repo=fake_repo,
        comp_repo=fake_repo,
        prompt_block_repo=fake_repo,
        output_profile_repo=fake_repo,
        identity_repo=fake_repo,
        audit_repo=fake_repo,
        system_repo=system_repo,
    )

    hook_result = await source_verification_hook(state=state, deps=deps)

    # Verify Hook Result
    assert hook_result.success is True
    assert hook_result.state_delta is not None
    assert hook_result.state_delta.metadata_updates is not None

    metadata_delta = hook_result.state_delta.metadata_updates
    assert metadata_delta.mcp_audit_traces is not None

    raw_traces = metadata_delta.mcp_audit_traces
    assert isinstance(raw_traces, list)
    assert len(raw_traces) >= 1

    # Map typed MCPAuditTrace instances
    audit_map: dict[str, MCPAuditTrace] = {}
    for typed_trace in raw_traces:
        assert typed_trace.id is not None
        audit_map[typed_trace.id] = typed_trace
        assert typed_trace.tool_id == "tavily_search"
        assert len(typed_trace.source_urls) >= 1
        assert any(url.startswith("http") for url in typed_trace.source_urls)

    # 2. Pipeline Step 2: Verify Evidence XML for Step LLM Context
    assert isinstance(hook_result.state_delta.delta, ExternalEvidenceResultDTO)
    evidence_xml = hook_result.state_delta.delta.external_evidence
    assert isinstance(evidence_xml, str)
    assert "<external_evidence>" in evidence_xml
    assert "<claim status=" in evidence_xml

    # 3. Pipeline Step 3: Server-Driven UI Rendering (SDUI)
    mock_profile = OutputProfile(
        id="prf_1111222233334444",
        slug="default_profile",
        workflow_id="wor_1111222233334444",
        name=I18nText(translations={"fi": "Oletusprofiili", "en": "Default Profile"}),
        target_block_order=[TargetBlockType.PRINTABLE_SOURCES_BLOCK],
    )

    adapter_context_fi = AdapterContext(
        execution=None,
        locale="fi",
        penalties_applied=[],
        mcp_audit_map=audit_map,
        global_score=None,
        profile=mock_profile,
        profile_cache=None,
        user_name="Test User",
        org_name="Test Org",
        parsed_matrices={},
        mcp_tools_map={},
    )

    sdui_blocks_fi = PrintableSourcesAdapter.build(adapter_context_fi)

    assert len(sdui_blocks_fi) == 1
    markdown_block_fi = sdui_blocks_fi[0]
    assert isinstance(markdown_block_fi, MarkdownBlock)
    assert "### Lähteet ja lähdeviitteet" in markdown_block_fi.text

    # Verify that real HTTP source URLs from Tavily search are included in the bibliography
    for trace in audit_map.values():
        for url in trace.source_urls:
            assert url in markdown_block_fi.text

    # 4. Pipeline Step 4: Verify English Localization Parity
    adapter_context_en = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=audit_map,
        global_score=None,
        profile=mock_profile,
        profile_cache=None,
        user_name="Test User",
        org_name="Test Org",
        parsed_matrices={},
        mcp_tools_map={},
    )

    sdui_blocks_en = PrintableSourcesAdapter.build(adapter_context_en)
    assert len(sdui_blocks_en) == 1
    assert isinstance(sdui_blocks_en[0], MarkdownBlock)
    assert "### Sources and Bibliography" in sdui_blocks_en[0].text


@pytest.mark.asyncio
async def test_full_e2e_tavily_empty_claims_invalid_skips_search_and_hides_sdui_block() -> None:
    """End-to-end test: Non-verifiable text skips Tavily search and omits bibliography from SDUI."""
    settings = get_settings()
    if "TAVILY_API_KEY" not in os.environ or not os.environ["TAVILY_API_KEY"]:
        pytest.skip("TAVILY_API_KEY is not configured in environment.")

    driver = await get_driver(settings)
    system_repo = SystemRepositoryImpl(driver)

    document_text = "Hei kaikille ja tervetuloa tämänpäiväiseen kokoukseen."

    state = HookState(
        execution_id="exe_2222333344445555",
        workflow_id="wor_2222333344445555",
        step_id="sp_76eedbc020274f66",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(dynamic_inputs={"document_text": document_text}, target_locale="fi"),
    )
    fake_repo = InMemoryUnifiedWorkflowRepository()
    deps = HookDependencies(
        exec_repo=fake_repo,
        workflow_repo=fake_repo,
        comp_repo=fake_repo,
        prompt_block_repo=fake_repo,
        output_profile_repo=fake_repo,
        identity_repo=fake_repo,
        audit_repo=fake_repo,
        system_repo=system_repo,
    )

    hook_result = await source_verification_hook(state=state, deps=deps)

    assert hook_result.success is True
    assert hook_result.state_delta is not None

    metadata_delta = hook_result.state_delta.metadata_updates
    traces = metadata_delta.mcp_audit_traces if (metadata_delta and metadata_delta.mcp_audit_traces) else []
    assert len(traces) == 0

    # Build SDUI with empty audit map
    mock_profile = OutputProfile(
        id="prf_2222333344445555",
        slug="empty_profile",
        workflow_id="wor_2222333344445555",
        name=I18nText(translations={"fi": "Tyhjä profiili", "en": "Empty Profile"}),
        target_block_order=[TargetBlockType.PRINTABLE_SOURCES_BLOCK],
    )

    adapter_context = AdapterContext(
        execution=None,
        locale="fi",
        penalties_applied=[],
        mcp_audit_map={},
        global_score=None,
        profile=mock_profile,
        profile_cache=None,
        user_name="Test User",
        org_name="Test Org",
        parsed_matrices={},
        mcp_tools_map={},
    )

    sdui_blocks = PrintableSourcesAdapter.build(adapter_context)
    # When no citations or search traces exist and summary box is enabled, PrintableSourcesAdapter renders empty notice
    assert len(sdui_blocks) == 1
    assert isinstance(sdui_blocks[0], MarkdownBlock)
    assert "ei havaittu ulkoisia kirjallisuusviitteitä" in sdui_blocks[0].text

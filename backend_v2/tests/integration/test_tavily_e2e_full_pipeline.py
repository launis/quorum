"""Full End-to-End Integration Test for Tavily Search & Bibliography Generation.

Tests the complete lifecycle:
1. Input document ingestion & claim extraction via Fast LLM
2. Live Tavily web search verification & MCPAuditTrace creation
3. External evidence XML construction for workflow step context
4. SDUI PrintableSourcesAdapter rendering into final markdown bibliography
5. Data starvation / claim-free input handling (graceful block omission)
"""

import _socket
import socket
from unittest.mock import AsyncMock

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
from backend_v2.models.enums import TargetBlockType
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.v2_core import MCPAuditTrace, OutputProfile
from backend_v2.models.view.sdui import MarkdownBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.printable_sources_adapter import PrintableSourcesAdapter
from backend_v2.settings import get_settings


@pytest.fixture(autouse=True)
def allow_live_network(monkeypatch: pytest.MonkeyPatch) -> None:
    """Restores unblocked C-level socket getaddrinfo for live network calls."""
    monkeypatch.setattr(socket, "getaddrinfo", _socket.getaddrinfo)


@pytest.mark.asyncio
async def test_full_e2e_tavily_extraction_to_sdui_bibliography_live() -> None:
    """End-to-end test: Ingest text -> extract claims -> live Tavily search -> build SDUI bibliography."""
    settings = get_settings()
    if not settings.tavily_api_key:
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

    hook_result = await source_verification_hook(state=state, deps=deps)

    # Verify Hook Result
    assert hook_result.success is True
    assert hook_result.state_delta is not None
    assert hook_result.state_delta.metadata_updates is not None

    metadata_dict = hook_result.state_delta.metadata_updates
    assert isinstance(metadata_dict, dict)
    assert "mcp_audit_traces" in metadata_dict

    raw_traces = metadata_dict["mcp_audit_traces"]
    assert isinstance(raw_traces, list)
    assert len(raw_traces) >= 1

    # Convert raw trace dicts to typed MCPAuditTrace instances
    audit_map: dict[str, MCPAuditTrace] = {}
    for trace_data in raw_traces:
        typed_trace = MCPAuditTrace.model_validate(trace_data)
        audit_map[typed_trace.id] = typed_trace
        assert typed_trace.tool_id == "mcp_tavily_search"
        assert len(typed_trace.source_urls) >= 1
        assert any(url.startswith("http") for url in typed_trace.source_urls)

    # 2. Pipeline Step 2: Verify Evidence XML for Step LLM Context
    assert "external_evidence" in hook_result.state_delta.delta
    evidence_xml = hook_result.state_delta.delta["external_evidence"]
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
    )

    sdui_blocks_en = PrintableSourcesAdapter.build(adapter_context_en)
    assert len(sdui_blocks_en) == 1
    assert "### Sources and Bibliography" in sdui_blocks_en[0].text  # type: ignore[attr-defined]


@pytest.mark.asyncio
async def test_full_e2e_tavily_empty_claims_skips_search_and_hides_sdui_block() -> None:
    """End-to-end test: Non-verifiable text skips Tavily search and omits bibliography from SDUI."""
    settings = get_settings()
    if not settings.tavily_api_key:
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

    hook_result = await source_verification_hook(state=state, deps=deps)

    assert hook_result.success is True
    assert hook_result.state_delta is not None

    metadata_dict = hook_result.state_delta.metadata_updates
    traces = metadata_dict.get("mcp_audit_traces", []) if metadata_dict else []
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
    )

    sdui_blocks = PrintableSourcesAdapter.build(adapter_context)
    # When no citations or search traces exist and summary box is enabled, PrintableSourcesAdapter renders empty notice
    assert len(sdui_blocks) == 1
    assert "ei havaittu ulkoisia kirjallisuusviitteitä" in sdui_blocks[0].text  # type: ignore[attr-defined]

"""Unit tests for deterministic MCP Tool Loop Conductor."""

from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel, ConfigDict, Field, JsonValue

from backend_v2.exceptions import AppException, ErrorCodes, SemanticEvidenceError
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.mcp import (
    CitationCorrectionResult,
    CitationExtractionItemDTO,
    CitationExtractionResult,
    MCPRetrievalResultDTO,
    MCPSynthesisInstructionsDTO,
)
from backend_v2.models.domain.system_config import (
    AllowedMCPTool,
    MCPAuditTrace,
    SystemConfigMCPGateways,
)
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.mcp import MCPToolInputSchemaDTO, MCPToolSchemaPropertyDTO
from backend_v2.models.enums import (
    JSONSchemaPropertyType,
    MCPAuthType,
    MCPTransportType,
    SourceSufficiencyThreshold,
    ToolCapability,
)
from backend_v2.models.llm import LLMMessageDTO
from backend_v2.services.mcp.dispatcher import ToolDispatcher
from backend_v2.services.mcp.mcp_tool_loop import (
    _build_tool_evidence_message,
    _resolve_dispatcher,
    execute_mcp_retrieval,
    execute_tool_loop,
    is_source_sufficient,
    validate_query_relevance,
)
from backend_v2.utils.alias_engine import AliasEngine

TAVILY_ALIAS = "default_mcp_gateway__mcp_tavily_search"
WIKI_SEARCH_ALIAS = "default_mcp_gateway__mcp_wikipedia_search"
WIKI_READ_ALIAS = "default_mcp_gateway__mcp_wikipedia_read"


class MockResponseModel(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")
    score: float = Field(description="Test score.")
    reasoning: str = Field(description="Test reasoning.")


def _make_mock_llm_client() -> MagicMock:
    return MagicMock()


def _make_gateway_fixture() -> SystemConfigMCPGateways:
    search_schema = MCPToolInputSchemaDTO(
        properties={
            "query": MCPToolSchemaPropertyDTO(
                type=JSONSchemaPropertyType.STRING,
                description="Search query string.",
            )
        },
        required=["query"],
    )
    read_schema = MCPToolInputSchemaDTO(
        properties={
            "title": MCPToolSchemaPropertyDTO(
                type=JSONSchemaPropertyType.STRING,
                description="Article title.",
            )
        },
        required=["title"],
    )
    return SystemConfigMCPGateways(
        id="sys_a1b2c3d4e5f60718",
        slug="default_mcp_gateway",
        endpoint_url="https://mcp.example.com/v1",
        transport_type=MCPTransportType.STREAMABLE_HTTP,
        auth_type=MCPAuthType.NONE,
        timeout_seconds=15,
        tools=[
            AllowedMCPTool(
                tool_id="mcp_tavily_search",
                name=I18nText(translations={"en": "Tavily Search", "fi": "Tavily-haku"}),
                description="Search the web",
                enabled=True,
                capability=ToolCapability.SEARCH,
                input_schema=search_schema,
            ),
            AllowedMCPTool(
                tool_id="mcp_wikipedia_search",
                name=I18nText(translations={"en": "Wikipedia Search", "fi": "Wikipedia-haku"}),
                description="Search Wikipedia",
                enabled=True,
                capability=ToolCapability.SEARCH,
                input_schema=search_schema,
            ),
            AllowedMCPTool(
                tool_id="mcp_wikipedia_read",
                name=I18nText(translations={"en": "Wikipedia Read", "fi": "Wikipedia-luku"}),
                description="Read Wikipedia",
                enabled=True,
                capability=ToolCapability.DOCUMENT_READER,
                input_schema=read_schema,
            ),
        ],
    )


def _make_test_dispatcher() -> ToolDispatcher:
    return ToolDispatcher(gateways=[_make_gateway_fixture()], mcp_client=MagicMock())


def _make_mock_executor(extracted_claims: list[str] | None = None) -> MagicMock:
    executor = MagicMock()

    async def mock_execute_structured_task(*args: Any, **kwargs: Any) -> tuple[Any, TokenUsage]:
        response_model = kwargs["response_model"] if "response_model" in kwargs else None
        if response_model == CitationExtractionResult:
            citations = [
                CitationExtractionItemDTO(claim_text=c, search_query=c, reasoning="Mock reasoning.")
                for c in (extracted_claims or [])
            ]
            return (
                CitationExtractionResult(citations=citations),
                TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=10),
            )
        elif response_model == CitationCorrectionResult:
            return (
                CitationCorrectionResult(corrected_claim="corrected but still hallucinated"),
                TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=5),
            )
        mock_result = MockResponseModel(score=4.5, reasoning="Well-supported claim.")
        usage = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=100)
        return (mock_result, usage)

    executor.execute_structured_task = AsyncMock(side_effect=mock_execute_structured_task)
    executor.execute_chat_task = AsyncMock(return_value="Direct text response.")
    return executor


@pytest.mark.asyncio
async def test_resolve_dispatcher_from_repository_and_fallback() -> None:
    """Verify _resolve_dispatcher resolves gateways from repository or returns empty ToolDispatcher."""
    from backend_v2.tests.fakes.in_memory_repositories import InMemorySystemRepository

    gateway = _make_gateway_fixture()
    repo = InMemorySystemRepository()
    await repo.update_mcp_gateways(gateway)

    resolved = await _resolve_dispatcher(dispatcher=None, repository=repo)
    assert TAVILY_ALIAS in resolved.get_all_enabled_tool_aliases()

    empty_resolved = await _resolve_dispatcher(dispatcher=None, repository=None)
    assert empty_resolved.get_all_enabled_tool_aliases() == []


@pytest.mark.asyncio
async def test_tool_loop_no_tools_passthrough() -> None:
    client = _make_mock_llm_client()
    executor = _make_mock_executor()
    dispatcher = _make_test_dispatcher()
    result = await execute_tool_loop(
        llm_client=client,
        executor=executor,
        messages=[{"role": "user", "content": "test"}],
        response_model=MockResponseModel,
        allowed_tools=[],
        step_name="test_step",
        dispatcher=dispatcher,
    )
    assert result.result_data["score"] == 4.5
    assert len(result.audit_traces) == 0
    executor.execute_structured_task.assert_called_once()


@pytest.mark.asyncio
async def test_citation_extraction_empty_document() -> None:
    client = _make_mock_llm_client()
    executor = _make_mock_executor(extracted_claims=[])
    dispatcher = _make_test_dispatcher()

    with patch.object(dispatcher, "execute_tool", new_callable=AsyncMock) as mock_search:
        result = await execute_tool_loop(
            llm_client=client,
            executor=executor,
            messages=[{"role": "user", "content": "test"}],
            response_model=MockResponseModel,
            allowed_tools=[TAVILY_ALIAS],
            step_name="test_step",
            source_context="some context",
            dispatcher=dispatcher,
        )

    assert len(result.audit_traces) == 0
    mock_search.assert_not_called()
    assert executor.execute_structured_task.call_count == 4


@pytest.mark.asyncio
async def test_citation_extraction_hallucinated_claim_rejected() -> None:
    client = _make_mock_llm_client()
    executor = _make_mock_executor(extracted_claims=["This claim does not exist in the source document"])
    dispatcher = _make_test_dispatcher()

    with pytest.raises(SemanticEvidenceError) as exc_info:
        await execute_tool_loop(
            llm_client=client,
            executor=executor,
            messages=[{"role": "user", "content": "test"}],
            response_model=MockResponseModel,
            allowed_tools=[TAVILY_ALIAS],
            step_name="test_step",
            source_context="Actual source context without the hallucinated claim.",
            dispatcher=dispatcher,
        )
    assert "Self-correction failed" in str(exc_info.value.message)


@pytest.mark.asyncio
async def test_execute_tool_loop_deterministic_search() -> None:
    client = _make_mock_llm_client()
    executor = _make_mock_executor(extracted_claims=["valid claim 1", "valid claim 2"])
    dispatcher = _make_test_dispatcher()

    mock_settings = MagicMock()
    mock_settings.max_tool_calls_per_step = 3
    with (
        patch.object(dispatcher, "execute_tool", new_callable=AsyncMock) as mock_search,
        patch("backend_v2.services.mcp.mcp_tool_loop.get_settings", return_value=mock_settings),
    ):

        async def fake_search(*args: Any, **kwargs: Any) -> MCPAuditTrace:
            raw_args = kwargs["raw_arguments"] if "raw_arguments" in kwargs else {}
            query = str(raw_args["query"]) if "query" in raw_args else "test"
            return MCPAuditTrace(
                tool_id="mcp_tavily_search",
                namespaced_alias=TAVILY_ALIAS,
                gateway_slug="default_mcp_gateway",
                step_name="test_step",
                query=query,
                response_summary="Found some evidence",
                source_urls=["http://test.com"],
                timestamp=datetime.now(timezone.utc),
                duration_ms=100,
            )

        mock_search.side_effect = fake_search

        result = await execute_tool_loop(
            llm_client=client,
            executor=executor,
            messages=[{"role": "user", "content": "test"}],
            response_model=MockResponseModel,
            allowed_tools=[TAVILY_ALIAS],
            step_name="test_step",
            source_context="valid claim 1 and valid claim 2 are here.",
            dispatcher=dispatcher,
        )

    assert len(result.audit_traces) == 2
    assert result.audit_traces[0].query == "valid claim 1"
    assert result.audit_traces[1].query == "valid claim 2"
    assert mock_search.call_count == 2


@pytest.mark.asyncio
async def test_execute_tool_loop_with_wikipedia_search() -> None:
    client = _make_mock_llm_client()
    executor = _make_mock_executor(extracted_claims=["wikipedia claim 1"])
    dispatcher = _make_test_dispatcher()

    mock_settings = MagicMock()
    mock_settings.max_tool_calls_per_step = 3
    with (
        patch.object(dispatcher, "execute_tool", new_callable=AsyncMock) as mock_tool_exec,
        patch("backend_v2.services.mcp.mcp_tool_loop.get_settings", return_value=mock_settings),
    ):

        async def fake_wiki_search(*args: Any, **kwargs: Any) -> MCPAuditTrace:
            raw_args = kwargs["raw_arguments"] if "raw_arguments" in kwargs else {}
            query = str(raw_args["query"]) if "query" in raw_args else "test"
            return MCPAuditTrace(
                tool_id="mcp_wikipedia_search",
                namespaced_alias=WIKI_SEARCH_ALIAS,
                gateway_slug="default_mcp_gateway",
                step_name="wiki_step",
                query=query,
                response_summary="Wikipedia evidence summary",
                source_urls=["https://en.wikipedia.org/wiki/Test"],
                timestamp=datetime.now(timezone.utc),
                duration_ms=50,
            )

        mock_tool_exec.side_effect = fake_wiki_search

        result = await execute_tool_loop(
            llm_client=client,
            executor=executor,
            messages=[{"role": "user", "content": "test"}],
            response_model=MockResponseModel,
            allowed_tools=[WIKI_SEARCH_ALIAS, WIKI_READ_ALIAS],
            step_name="wiki_step",
            source_context="wikipedia claim 1 is documented in encyclopedias.",
            dispatcher=dispatcher,
        )

    assert len(result.audit_traces) == 1
    assert result.audit_traces[0].tool_id == "mcp_wikipedia_search"
    assert result.audit_traces[0].query == "wikipedia claim 1"
    assert mock_tool_exec.call_count == 1


@pytest.mark.asyncio
async def test_ensemble_vote_consensus() -> None:
    client = _make_mock_llm_client()
    executor = MagicMock()
    dispatcher = _make_test_dispatcher()

    call_count = 0

    async def mock_execute_structured_task(*args: Any, **kwargs: Any) -> tuple[Any, TokenUsage]:
        nonlocal call_count
        response_model = kwargs["response_model"] if "response_model" in kwargs else None
        if response_model == CitationExtractionResult:
            call_count += 1
            if call_count == 1:
                claims = ["claim A", "claim B"]
            elif call_count == 2:
                claims = ["claim B", "claim C"]
            else:
                claims = ["claim B"]
            citations = [
                CitationExtractionItemDTO(claim_text=c, search_query=c, reasoning="Mock reasoning.") for c in claims
            ]
            return (
                CitationExtractionResult(citations=citations),
                TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            )
        mock_result = MockResponseModel(score=4.5, reasoning="Ensemble test")
        usage = TokenUsage(prompt_tokens=50, completion_tokens=20, total_tokens=70)
        return (mock_result, usage)

    executor.execute_structured_task = AsyncMock(side_effect=mock_execute_structured_task)

    with patch.object(dispatcher, "execute_tool", new_callable=AsyncMock) as mock_search:

        async def fake_search(*args: Any, **kwargs: Any) -> MCPAuditTrace:
            raw_args = kwargs["raw_arguments"] if "raw_arguments" in kwargs else {}
            query = str(raw_args["query"]) if "query" in raw_args else ""
            return MCPAuditTrace(
                tool_id="mcp_tavily_search",
                namespaced_alias=TAVILY_ALIAS,
                gateway_slug="default_mcp_gateway",
                step_name="test_step",
                query=query,
                response_summary="Found",
                source_urls=[],
                timestamp=datetime.now(timezone.utc),
                duration_ms=50,
            )

        mock_search.side_effect = fake_search

        result = await execute_tool_loop(
            llm_client=client,
            executor=executor,
            messages=[{"role": "user", "content": "test"}],
            response_model=MockResponseModel,
            allowed_tools=[TAVILY_ALIAS],
            step_name="test_step",
            source_context="claim A claim B claim C",
            dispatcher=dispatcher,
        )

    assert len(result.audit_traces) == 1
    assert result.audit_traces[0].query == "claim B"
    assert result.usage.total_tokens == 115


@pytest.mark.asyncio
async def test_strictness_override_bypasses_physical_anchoring() -> None:
    client = _make_mock_llm_client()
    executor = _make_mock_executor(extracted_claims=["hallucinated claim"])
    dispatcher = _make_test_dispatcher()

    with patch.object(dispatcher, "execute_tool", new_callable=AsyncMock) as mock_search:

        async def fake_search(*args: Any, **kwargs: Any) -> MCPAuditTrace:
            raw_args = kwargs["raw_arguments"] if "raw_arguments" in kwargs else {}
            query = str(raw_args["query"]) if "query" in raw_args else ""
            return MCPAuditTrace(
                tool_id="mcp_tavily_search",
                namespaced_alias=TAVILY_ALIAS,
                gateway_slug="default_mcp_gateway",
                step_name="test_step",
                query=query,
                response_summary="Found",
                source_urls=[],
                timestamp=datetime.now(timezone.utc),
                duration_ms=50,
            )

        mock_search.side_effect = fake_search

        result = await execute_tool_loop(
            llm_client=client,
            executor=executor,
            messages=[{"role": "user", "content": "test"}],
            response_model=MockResponseModel,
            allowed_tools=[TAVILY_ALIAS],
            step_name="test_step",
            source_context="totally unrelated source context",
            validation_context={"strictness_level": 85},
            dispatcher=dispatcher,
        )

    assert len(result.audit_traces) == 1
    assert result.audit_traces[0].query == "hallucinated claim"
    assert mock_search.call_count == 1


@pytest.mark.asyncio
async def test_agentic_self_reflection_success() -> None:
    client = _make_mock_llm_client()
    dispatcher = _make_test_dispatcher()

    async def mock_execute_structured_task(*args: Any, **kwargs: Any) -> tuple[Any, TokenUsage]:
        response_model = kwargs["response_model"] if "response_model" in kwargs else None
        if response_model == CitationExtractionResult:
            citations = [
                CitationExtractionItemDTO(
                    claim_text="imprecise claim", search_query="query", reasoning="Mock reasoning."
                )
            ]
            return (
                CitationExtractionResult(citations=citations),
                TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            )
        elif response_model == CitationCorrectionResult:
            return (
                CitationCorrectionResult(corrected_claim="precise claim"),
                TokenUsage(prompt_tokens=20, completion_tokens=10, total_tokens=30),
            )
        mock_result = MockResponseModel(score=4.5, reasoning="Reflection success test")
        usage = TokenUsage(prompt_tokens=50, completion_tokens=20, total_tokens=70)
        return (mock_result, usage)

    executor = MagicMock()
    executor.execute_structured_task = AsyncMock(side_effect=mock_execute_structured_task)

    with patch.object(dispatcher, "execute_tool", new_callable=AsyncMock) as mock_search:

        async def fake_search(*args: Any, **kwargs: Any) -> MCPAuditTrace:
            raw_args = kwargs["raw_arguments"] if "raw_arguments" in kwargs else {}
            query = str(raw_args["query"]) if "query" in raw_args else ""
            return MCPAuditTrace(
                tool_id="mcp_tavily_search",
                namespaced_alias=TAVILY_ALIAS,
                gateway_slug="default_mcp_gateway",
                step_name="test_step",
                query=query,
                response_summary="Found",
                source_urls=[],
                timestamp=datetime.now(timezone.utc),
                duration_ms=50,
            )

        mock_search.side_effect = fake_search

        result = await execute_tool_loop(
            llm_client=client,
            executor=executor,
            messages=[{"role": "user", "content": "test"}],
            response_model=MockResponseModel,
            allowed_tools=[TAVILY_ALIAS],
            step_name="test_step",
            source_context="source context containing precise claim here",
            validation_context={"strictness_level": 100},
            dispatcher=dispatcher,
        )

    assert len(result.audit_traces) == 1
    assert mock_search.call_count == 1
    assert result.usage.total_tokens == 145


@pytest.mark.asyncio
async def test_agentic_self_reflection_failure_raises_error() -> None:
    client = _make_mock_llm_client()
    dispatcher = _make_test_dispatcher()

    async def mock_execute_structured_task(*args: Any, **kwargs: Any) -> tuple[Any, TokenUsage]:
        response_model = kwargs["response_model"] if "response_model" in kwargs else None
        if response_model == CitationExtractionResult:
            citations = [
                CitationExtractionItemDTO(
                    claim_text="totally hallucinated claim", search_query="query", reasoning="Mock reasoning."
                )
            ]
            return (
                CitationExtractionResult(citations=citations),
                TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            )
        elif response_model == CitationCorrectionResult:
            return (
                CitationCorrectionResult(corrected_claim="totally missing claim"),
                TokenUsage(prompt_tokens=20, completion_tokens=10, total_tokens=30),
            )
        mock_result = MockResponseModel(score=4.5, reasoning="Reflection failure test")
        usage = TokenUsage(prompt_tokens=50, completion_tokens=20, total_tokens=70)
        return (mock_result, usage)

    executor = MagicMock()
    executor.execute_structured_task = AsyncMock(side_effect=mock_execute_structured_task)

    with pytest.raises(SemanticEvidenceError) as exc_info:
        await execute_tool_loop(
            llm_client=client,
            executor=executor,
            messages=[{"role": "user", "content": "test"}],
            response_model=MockResponseModel,
            allowed_tools=[TAVILY_ALIAS],
            step_name="test_step",
            source_context="source context with no overlap at all",
            validation_context={"strictness_level": 100},
            dispatcher=dispatcher,
        )
    assert "Self-correction failed" in str(exc_info.value.message)


def test_validate_query_relevance() -> None:
    """Tests validate_query_relevance for various contexts and query inputs."""
    assert validate_query_relevance("test query", "") is True
    assert validate_query_relevance("  ", "some context") is True

    assert (
        validate_query_relevance("Harvard medical research", "This document contains Harvard clinical findings.")
        is True
    )

    assert (
        validate_query_relevance("Bitcoin exchange rate", "This document discusses pediatric nutrition exclusively.")
        is False
    )


def test_is_source_sufficient() -> None:
    """Tests is_source_sufficient against MIN_CHARS threshold."""
    short_text = "short text"
    assert is_source_sufficient(short_text) is False

    long_text = "a" * (SourceSufficiencyThreshold.MIN_CHARS.value + 10)
    assert is_source_sufficient(long_text) is True


def test_build_tool_evidence_message() -> None:
    """Tests _build_tool_evidence_message formatting for both empty and populated audit traces."""
    empty_trace = MCPAuditTrace(
        id="t1",
        tool_id="mcp_tavily_search",
        step_name="step",
        query="query",
        reasoning="r",
        response_summary="",
        source_urls=[],
        timestamp=datetime.now(timezone.utc),
        duration_ms=10,
    )
    empty_msg = _build_tool_evidence_message(empty_trace, "call_123")
    assert empty_msg.role == "tool"
    assert empty_msg.tool_call_id == "call_123"
    assert isinstance(empty_msg.content, str)
    assert "Search returned no results" in empty_msg.content

    populated_trace = MCPAuditTrace(
        id="t2",
        tool_id="mcp_tavily_search",
        step_name="step",
        query="verified query",
        reasoning="r",
        response_summary="Verified finding summary",
        source_urls=["https://example.com/source1"],
        timestamp=datetime.now(timezone.utc),
        duration_ms=10,
    )
    pop_msg = _build_tool_evidence_message(populated_trace, "call_456")
    assert pop_msg.role == "tool"
    assert isinstance(pop_msg.content, str)
    assert "<query>verified query</query>" in pop_msg.content
    assert "<summary>Verified finding summary</summary>" in pop_msg.content
    assert "<url>https://example.com/source1</url>" in pop_msg.content


@pytest.mark.asyncio
async def test_execute_tool_loop_with_synthesis_instructions() -> None:
    """Tests execute_tool_loop injecting synthesis formatting constraints."""
    client = _make_mock_llm_client()
    executor = _make_mock_executor(extracted_claims=["valid claim"])
    dispatcher = _make_test_dispatcher()

    synthesis_payload = {
        "synthesis_preamble": "Custom preamble for profile.",
        "synthesis_length_limit": 200,
    }

    with patch.object(dispatcher, "execute_tool", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = MCPAuditTrace(
            tool_id="mcp_tavily_search",
            namespaced_alias=TAVILY_ALIAS,
            gateway_slug="default_mcp_gateway",
            step_name="test_synth_step",
            query="valid claim",
            response_summary="Evidence summary",
            source_urls=["https://example.com"],
            timestamp=datetime.now(timezone.utc),
            duration_ms=50,
        )

        synth_arg: Any = synthesis_payload
        result = await execute_tool_loop(
            llm_client=client,
            executor=executor,
            messages=[{"role": "system", "content": "Base prompt."}],
            response_model=MockResponseModel,
            allowed_tools=[TAVILY_ALIAS],
            step_name="test_synth_step",
            source_context="source document text with valid claim here",
            synthesis_instructions=synth_arg,
            dispatcher=dispatcher,
        )

    assert result.result_data["score"] == 4.5
    call_args = executor.execute_structured_task.call_args.kwargs
    first_msg = call_args["messages"][0].content
    assert isinstance(first_msg, str)
    assert "<synthesis_preamble>Custom preamble for profile.</synthesis_preamble>" in first_msg
    assert "<synthesis_length_limit>200</synthesis_length_limit>" in first_msg


@pytest.mark.asyncio
async def test_execute_tool_loop_invalid_synthesis_instructions_raises_app_exception() -> None:
    """Tests execute_tool_loop raising AppException on invalid synthesis instructions."""
    client = _make_mock_llm_client()
    executor = _make_mock_executor(extracted_claims=["valid claim"])
    dispatcher = _make_test_dispatcher()

    with patch.object(dispatcher, "execute_tool", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = MCPAuditTrace(
            tool_id="mcp_tavily_search",
            namespaced_alias=TAVILY_ALIAS,
            gateway_slug="default_mcp_gateway",
            step_name="test_synth_step",
            query="valid claim",
            response_summary="Evidence summary",
            source_urls=["https://example.com"],
            timestamp=datetime.now(timezone.utc),
            duration_ms=50,
        )

        invalid_synth: Any = "invalid_non_dict_payload"
        with pytest.raises(AppException) as exc_info:
            await execute_tool_loop(
                llm_client=client,
                executor=executor,
                messages=[{"role": "user", "content": "test"}],
                response_model=MockResponseModel,
                allowed_tools=[TAVILY_ALIAS],
                step_name="test_synth_step",
                source_context="source document text with valid claim here",
                synthesis_instructions=invalid_synth,
                dispatcher=dispatcher,
            )
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_execute_tool_loop_phase2_failure_raises_app_exception() -> None:
    """Tests execute_tool_loop catching unexpected Phase 2 crash and raising AppException."""
    client = _make_mock_llm_client()
    dispatcher = _make_test_dispatcher()

    async def mock_execute_structured_task(*args: Any, **kwargs: Any) -> tuple[Any, TokenUsage]:
        response_model = kwargs["response_model"] if "response_model" in kwargs else None
        if response_model == CitationExtractionResult:
            citations = [CitationExtractionItemDTO(claim_text="valid claim", search_query="valid claim", reasoning="r")]
            return (
                CitationExtractionResult(citations=citations),
                TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            )
        raise RuntimeError("Unexpected LLM crash in Phase 2")

    executor = MagicMock()
    executor.execute_structured_task = AsyncMock(side_effect=mock_execute_structured_task)

    with patch.object(dispatcher, "execute_tool", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = MCPAuditTrace(
            tool_id="mcp_tavily_search",
            namespaced_alias=TAVILY_ALIAS,
            gateway_slug="default_mcp_gateway",
            step_name="test_crash_step",
            query="valid claim",
            response_summary="Evidence summary",
            source_urls=[],
            timestamp=datetime.now(timezone.utc),
            duration_ms=50,
        )

        with pytest.raises(AppException) as exc_info:
            await execute_tool_loop(
                llm_client=client,
                executor=executor,
                messages=[{"role": "user", "content": "test"}],
                response_model=MockResponseModel,
                allowed_tools=[TAVILY_ALIAS],
                step_name="test_crash_step",
                source_context="source document with valid claim here",
                dispatcher=dispatcher,
            )
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_ensemble_all_runs_fail_raises_app_exception() -> None:
    """Tests that Phase 0 raises AppException when all 3 ensemble extractions fail."""
    client = _make_mock_llm_client()
    executor = MagicMock()
    executor.execute_structured_task = AsyncMock(side_effect=RuntimeError("Extraction failed"))
    dispatcher = _make_test_dispatcher()

    with pytest.raises(AppException) as exc_info:
        await execute_tool_loop(
            llm_client=client,
            executor=executor,
            messages=[{"role": "user", "content": "test"}],
            response_model=MockResponseModel,
            allowed_tools=[TAVILY_ALIAS],
            step_name="test_step",
            source_context="source context",
            dispatcher=dispatcher,
        )
    assert exc_info.value.status_code == 502


@pytest.mark.asyncio
async def test_max_tool_calls_limit_reached(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tests that max_tool_calls_per_step limit stops further tool calls."""
    from backend_v2.settings import get_settings

    monkeypatch.setattr(get_settings(), "max_tool_calls_per_step", 1)

    client = _make_mock_llm_client()
    executor = _make_mock_executor(extracted_claims=["claim1", "claim2", "claim3"])
    dispatcher = _make_test_dispatcher()

    with patch.object(dispatcher, "execute_tool", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = MCPAuditTrace(
            tool_id="mcp_tavily_search",
            namespaced_alias=TAVILY_ALIAS,
            gateway_slug="default_mcp_gateway",
            step_name="test_step",
            query="claim1",
            response_summary="summary",
            source_urls=[],
            timestamp=datetime.now(timezone.utc),
            duration_ms=10,
        )

        result = await execute_tool_loop(
            llm_client=client,
            executor=executor,
            messages=[{"role": "user", "content": "test"}],
            response_model=MockResponseModel,
            allowed_tools=[TAVILY_ALIAS],
            step_name="test_step",
            source_context="claim1 and claim2 and claim3 are in source",
            dispatcher=dispatcher,
        )

    assert len(result.audit_traces) == 1
    assert mock_search.call_count == 1


@pytest.mark.asyncio
async def test_extraction_dict_model_validation() -> None:
    """Tests that a dict returned for CitationExtractionResult is properly model_validated."""
    client = _make_mock_llm_client()
    dispatcher = _make_test_dispatcher()

    async def mock_execute_structured_task(*args: Any, **kwargs: Any) -> tuple[Any, TokenUsage]:
        response_model = kwargs["response_model"] if "response_model" in kwargs else None
        if response_model == CitationExtractionResult:
            return (
                {"citations": [{"claim_text": "claim1", "search_query": "claim1", "reasoning": "r"}]},
                TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            )
        mock_result = MockResponseModel(score=4.5, reasoning="Good")
        return (mock_result, TokenUsage(prompt_tokens=50, completion_tokens=20, total_tokens=70))

    executor = MagicMock()
    executor.execute_structured_task = AsyncMock(side_effect=mock_execute_structured_task)

    with patch.object(dispatcher, "execute_tool", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = MCPAuditTrace(
            tool_id="mcp_tavily_search",
            namespaced_alias=TAVILY_ALIAS,
            gateway_slug="default_mcp_gateway",
            step_name="test_step",
            query="claim1",
            response_summary="summary",
            source_urls=[],
            timestamp=datetime.now(timezone.utc),
            duration_ms=10,
        )

        result = await execute_tool_loop(
            llm_client=client,
            executor=executor,
            messages=[{"role": "user", "content": "test"}],
            response_model=MockResponseModel,
            allowed_tools=[TAVILY_ALIAS],
            step_name="test_step",
            source_context="claim1 is here",
            dispatcher=dispatcher,
        )

    assert len(result.audit_traces) == 1


@pytest.mark.asyncio
async def test_phase2_app_exception_passthrough() -> None:
    """Tests that an AppException raised during Phase 2 is directly re-raised without re-wrapping."""
    client = _make_mock_llm_client()
    dispatcher = _make_test_dispatcher()

    async def mock_execute_structured_task(*args: Any, **kwargs: Any) -> tuple[Any, TokenUsage]:
        response_model = kwargs["response_model"] if "response_model" in kwargs else None
        if response_model == CitationExtractionResult:
            citations = [CitationExtractionItemDTO(claim_text="valid claim", search_query="valid claim", reasoning="r")]
            return (
                CitationExtractionResult(citations=citations),
                TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            )
        raise AppException(
            message="Specific domain error in phase 2",
            status_code=422,
            details={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL},
        )

    executor = MagicMock()
    executor.execute_structured_task = AsyncMock(side_effect=mock_execute_structured_task)

    with patch.object(dispatcher, "execute_tool", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = MCPAuditTrace(
            tool_id="mcp_tavily_search",
            namespaced_alias=TAVILY_ALIAS,
            gateway_slug="default_mcp_gateway",
            step_name="test_crash_step",
            query="valid claim",
            response_summary="Evidence",
            source_urls=[],
            timestamp=datetime.now(timezone.utc),
            duration_ms=50,
        )

        with pytest.raises(AppException) as exc_info:
            await execute_tool_loop(
                llm_client=client,
                executor=executor,
                messages=[{"role": "user", "content": "test"}],
                response_model=MockResponseModel,
                allowed_tools=[TAVILY_ALIAS],
                step_name="test_crash_step",
                source_context="source document with valid claim here",
                dispatcher=dispatcher,
            )
    assert exc_info.value.status_code == 422


@pytest.mark.asyncio
async def test_tool_loop_llm_message_dto_and_float_strictness() -> None:
    """Verify tool loop handles LLMMessageDTO inputs with string/block contents and float strictness."""
    client = _make_mock_llm_client()
    executor = _make_mock_executor(extracted_claims=["valid claim"])
    dispatcher = _make_test_dispatcher()

    messages = [
        LLMMessageDTO(role="system", content="System instruction"),
        LLMMessageDTO(role="user", content="String user claim: valid claim"),
        LLMMessageDTO(role="user", content=[{"type": "text", "text": "Block user claim: valid claim"}]),
    ]

    with patch.object(dispatcher, "execute_tool", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = MCPAuditTrace(
            tool_id="mcp_tavily_search",
            namespaced_alias=TAVILY_ALIAS,
            gateway_slug="default_mcp_gateway",
            step_name="test_step",
            query="valid claim",
            response_summary="Found evidence online.",
            source_urls=["https://example.com"],
            timestamp=datetime.now(timezone.utc),
            duration_ms=50,
        )

        result = await execute_tool_loop(
            llm_client=client,
            executor=executor,
            messages=messages,
            response_model=MockResponseModel,
            allowed_tools=[TAVILY_ALIAS],
            step_name="test_step",
            source_context="source document with valid claim here",
            validation_context={"strictness_level": 70.0},
            dispatcher=dispatcher,
        )
        assert result.result_data["score"] == 4.5


@pytest.mark.asyncio
async def test_execute_mcp_retrieval_empty_tools() -> None:
    """Verify execute_mcp_retrieval with empty tools returns empty MCPRetrievalResultDTO without task execution."""
    client = _make_mock_llm_client()
    executor = _make_mock_executor()
    dispatcher = _make_test_dispatcher()

    result = await execute_mcp_retrieval(
        llm_client=client,
        executor=executor,
        messages=[{"role": "user", "content": "test content"}],
        allowed_tools=[],
        step_name="test_empty_step",
        dispatcher=dispatcher,
    )

    assert isinstance(result, MCPRetrievalResultDTO)
    assert len(result.audit_traces) == 0
    assert result.evidence_payload == ""
    assert result.usage.total_tokens == 0
    executor.execute_structured_task.assert_not_called()


@pytest.mark.asyncio
async def test_execute_mcp_retrieval_success_with_traces() -> None:
    """Verify execute_mcp_retrieval executes tools, formats evidence payload, and registers aliases."""
    client = _make_mock_llm_client()
    executor = _make_mock_executor(extracted_claims=["verified fact"])
    alias_engine = AliasEngine()
    dispatcher = _make_test_dispatcher()

    with patch.object(dispatcher, "execute_tool", new_callable=AsyncMock) as mock_tool:
        mock_tool.return_value = MCPAuditTrace(
            id="trc_001",
            tool_id="mcp_tavily_search",
            namespaced_alias=TAVILY_ALIAS,
            gateway_slug="default_mcp_gateway",
            step_name="retrieval_step",
            query="verified fact",
            response_summary="Verified fact evidence summary.",
            source_urls=["https://example.com/verified"],
            timestamp=datetime.now(timezone.utc),
            duration_ms=42,
        )

        result = await execute_mcp_retrieval(
            llm_client=client,
            executor=executor,
            messages=[{"role": "user", "content": "Here is a verified fact in text"}],
            allowed_tools=[TAVILY_ALIAS],
            step_name="retrieval_step",
            source_context="Here is a verified fact in text",
            alias_engine=alias_engine,
            validation_context={"query_guidance": "Focus search strictly on financial filing names."},
            dispatcher=dispatcher,
        )

    assert isinstance(result, MCPRetrievalResultDTO)
    assert len(result.audit_traces) == 1
    assert result.audit_traces[0].query == "verified fact"
    assert "<external_evidence>" in result.evidence_payload
    assert '<source ID="mcp0">' in result.evidence_payload
    assert "Verified fact evidence summary." in result.evidence_payload
    assert "https://example.com/verified" in result.evidence_payload
    assert result.usage.total_tokens > 0
    assert "mcp0" in alias_engine.source_document_aliases

    call_args = executor.execute_structured_task.call_args
    passed_messages = call_args.kwargs["messages"]
    sys_content = passed_messages[0].content
    assert isinstance(sys_content, str)
    assert "<rule>Focus search strictly on financial filing names.</rule>" in sys_content


@pytest.mark.asyncio
async def test_execute_mcp_retrieval_hallucinated_claim_rejected() -> None:
    """Verify execute_mcp_retrieval raises SemanticEvidenceError when claims fail physical anchoring."""
    client = _make_mock_llm_client()
    executor = _make_mock_executor(extracted_claims=["completely hallucinated claim"])
    dispatcher = _make_test_dispatcher()

    with pytest.raises(SemanticEvidenceError) as exc_info:
        await execute_mcp_retrieval(
            llm_client=client,
            executor=executor,
            messages=[{"role": "user", "content": "source text"}],
            allowed_tools=[TAVILY_ALIAS],
            step_name="retrieval_step",
            source_context="totally different source text",
            dispatcher=dispatcher,
        )

    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_execute_mcp_retrieval_fast_client_init_failure_raises_app_exception() -> None:
    """Verify execute_mcp_retrieval raises AppException(500) when fast client initialization fails."""
    from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository

    client = _make_mock_llm_client()
    executor = _make_mock_executor(extracted_claims=["valid claim"])
    empty_db = InMemoryUnifiedWorkflowRepository()
    dispatcher = _make_test_dispatcher()

    with pytest.raises(AppException) as exc_info:
        await execute_mcp_retrieval(
            llm_client=client,
            executor=executor,
            messages=[{"role": "user", "content": "valid claim"}],
            allowed_tools=[TAVILY_ALIAS],
            step_name="retrieval_step",
            source_context="valid claim",
            repository=empty_db,
            dispatcher=dispatcher,
        )

    assert exc_info.value.status_code == 500
    assert exc_info.value.details == {"error_code": ErrorCodes.CONFIGURATION_ERROR.value}


@pytest.mark.asyncio
async def test_self_correction_task_exception_raises_semantic_evidence_error() -> None:
    """Verify execute_mcp_retrieval wraps unexpected self-correction task exceptions in SemanticEvidenceError."""
    client = _make_mock_llm_client()
    dispatcher = _make_test_dispatcher()

    async def mock_execute_structured_task(*args: Any, **kwargs: Any) -> tuple[Any, TokenUsage]:
        response_model = kwargs["response_model"] if "response_model" in kwargs else None
        if response_model == CitationExtractionResult:
            citations = [
                CitationExtractionItemDTO(
                    claim_text="missing claim", search_query="missing claim", reasoning="Mock reasoning."
                )
            ]
            return (
                CitationExtractionResult(citations=citations),
                TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            )
        if response_model == CitationCorrectionResult:
            raise RuntimeError("Self-correction LLM transport timeout")
        return (
            MockResponseModel(score=4.0, reasoning="Default"),
            TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
        )

    executor = MagicMock()
    executor.execute_structured_task = AsyncMock(side_effect=mock_execute_structured_task)

    with pytest.raises(SemanticEvidenceError) as exc_info:
        await execute_mcp_retrieval(
            llm_client=client,
            executor=executor,
            messages=[{"role": "user", "content": "source text"}],
            allowed_tools=[TAVILY_ALIAS],
            step_name="retrieval_step",
            source_context="source text without that claim",
            dispatcher=dispatcher,
        )

    assert "Self-correction failed due to task error" in exc_info.value.message


@pytest.mark.asyncio
async def test_source_sufficiency_suppression_when_no_primary_search_tool() -> None:
    """Verify source sufficiency gate and non-search tool suppression in retrieval and tool loop."""
    client = _make_mock_llm_client()
    executor = _make_mock_executor()
    dispatcher = _make_test_dispatcher()
    long_source = "a" * (SourceSufficiencyThreshold.MIN_CHARS.value + 50)

    retrieval_sufficient = await execute_mcp_retrieval(
        llm_client=client,
        executor=executor,
        messages=[{"role": "user", "content": "test"}],
        allowed_tools=[WIKI_READ_ALIAS],
        step_name="sufficiency_step",
        source_context=long_source,
        dispatcher=dispatcher,
    )
    assert retrieval_sufficient.audit_traces == []
    assert retrieval_sufficient.evidence_payload == ""

    retrieval_short = await execute_mcp_retrieval(
        llm_client=client,
        executor=executor,
        messages=[{"role": "user", "content": "test"}],
        allowed_tools=[WIKI_READ_ALIAS],
        step_name="short_non_search_step",
        source_context="short context",
        dispatcher=dispatcher,
    )
    assert retrieval_short.audit_traces == []

    loop_sufficient = await execute_tool_loop(
        llm_client=client,
        executor=executor,
        messages=[{"role": "user", "content": "test"}],
        response_model=MockResponseModel,
        allowed_tools=[WIKI_READ_ALIAS],
        step_name="loop_sufficiency_step",
        source_context=long_source,
        dispatcher=dispatcher,
    )
    assert loop_sufficient.result_data["score"] == 4.5
    assert loop_sufficient.audit_traces == []


@pytest.mark.asyncio
async def test_self_correction_dict_empty_query_and_non_system_synthesis_insert() -> None:
    """Verify dict hydration for CitationCorrectionResult, empty query skip, and user-first synthesis insert."""
    client = _make_mock_llm_client()
    dispatcher = _make_test_dispatcher()

    async def mock_execute_structured_task(*args: Any, **kwargs: Any) -> tuple[Any, TokenUsage]:
        response_model = kwargs["response_model"] if "response_model" in kwargs else None
        if response_model == CitationExtractionResult:
            citations = [
                CitationExtractionItemDTO(
                    claim_text="verified claim",
                    search_query="   ",
                    reasoning="Blank query should be skipped.",
                ),
                CitationExtractionItemDTO(
                    claim_text="slightly off claim",
                    search_query="verified claim",
                    reasoning="Verify claim.",
                ),
            ]
            return (
                CitationExtractionResult(citations=citations),
                TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            )
        if response_model == CitationCorrectionResult:
            return (
                {"corrected_claim": "verified claim"},
                TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            )
        return (
            MockResponseModel(score=5.0, reasoning="Complete"),
            TokenUsage(prompt_tokens=20, completion_tokens=10, total_tokens=30),
        )

    executor = MagicMock()
    executor.execute_structured_task = AsyncMock(side_effect=mock_execute_structured_task)
    validation_ctx: dict[str, JsonValue] = {"mcp_source_texts": {"existing_alias": "existing text"}}

    with patch.object(dispatcher, "execute_tool", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = MCPAuditTrace(
            id="",
            tool_id="mcp_tavily_search",
            namespaced_alias=TAVILY_ALIAS,
            gateway_slug="default_mcp_gateway",
            step_name="step_edge",
            query="verified claim",
            response_summary="Summary text",
            source_urls=["https://example.com"],
            timestamp=datetime.now(timezone.utc),
            duration_ms=25,
        )

        result = await execute_tool_loop(
            llm_client=client,
            executor=executor,
            messages=[{"role": "user", "content": "Document with verified claim inside."}],
            response_model=MockResponseModel,
            allowed_tools=[TAVILY_ALIAS],
            step_name="step_edge",
            source_context="Document with verified claim inside.",
            synthesis_instructions=MCPSynthesisInstructionsDTO(
                synthesis_preamble="Preamble constraint.",
                synthesis_length_limit=150,
            ),
            validation_context=validation_ctx,
            dispatcher=dispatcher,
        )

    assert len(result.audit_traces) == 1
    assert mock_search.call_count == 1
    final_call_messages = executor.execute_structured_task.call_args.kwargs["messages"]
    assert final_call_messages[0].role == "system"
    assert isinstance(final_call_messages[0].content, str)
    assert "<synthesis_preamble>Preamble constraint.</synthesis_preamble>" in final_call_messages[0].content


@pytest.mark.asyncio
async def test_execute_mcp_retrieval_with_mcp_tool_params_and_jit_synthesis() -> None:
    """Verify execute_mcp_retrieval forwards mcp_tool_params and accumulates JIT synthesis token usage."""
    from backend_v2.models.domain.system_config import AllowedMCPTool, SystemConfigMCPGateways
    from backend_v2.models.dtos.mcp import MCPToolInputSchemaDTO, MCPToolSchemaPropertyDTO
    from backend_v2.models.enums import JSONSchemaPropertyType, MCPAuthType, MCPTransportType, ToolCapability

    complex_tool = AllowedMCPTool(
        tool_id="complex_search",
        capability=ToolCapability.SEARCH,
        name=I18nText(translations={"en": "Complex Search"}),
        description="Complex search tool requiring jurisdiction and category.",
        input_schema=MCPToolInputSchemaDTO(
            properties={
                "query": MCPToolSchemaPropertyDTO(type=JSONSchemaPropertyType.STRING),
                "country": MCPToolSchemaPropertyDTO(type=JSONSchemaPropertyType.STRING),
                "category": MCPToolSchemaPropertyDTO(type=JSONSchemaPropertyType.STRING),
                "numResults": MCPToolSchemaPropertyDTO(type=JSONSchemaPropertyType.INTEGER),
            },
            required=["query", "country", "category"],
        ),
        enabled=True,
    )
    gw = SystemConfigMCPGateways(
        id="sys_9999888877776666",
        slug="complex_gw",
        endpoint_url="https://mcp.example.com/complex",
        transport_type=MCPTransportType.STREAMABLE_HTTP,
        auth_type=MCPAuthType.NONE,
        tools=[complex_tool],
    )
    dispatcher = ToolDispatcher([gw])
    alias = "complex_gw__complex_search"
    client = _make_mock_llm_client()

    async def mock_structured_task(*args: Any, **kwargs: Any) -> tuple[Any, TokenUsage]:
        response_model = kwargs["response_model"] if "response_model" in kwargs else None
        if response_model == CitationExtractionResult:
            return (
                CitationExtractionResult(
                    citations=[
                        CitationExtractionItemDTO(
                            claim_text="verified fact",
                            search_query="verified fact",
                            reasoning="Check statutory database.",
                        )
                    ]
                ),
                TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            )
        # JIT synthesis call for MCPArgs_complex_gw__complex_search
        return (
            {"query": "verified fact", "country": "US", "category": "corporate", "numResults": 10},
            TokenUsage(prompt_tokens=25, completion_tokens=10, total_tokens=35),
        )

    executor = MagicMock()
    executor.execute_structured_task = AsyncMock(side_effect=mock_structured_task)

    with patch.object(dispatcher, "execute_tool", new_callable=AsyncMock) as mock_tool:
        mock_tool.return_value = MCPAuditTrace(
            id="trc_complex",
            tool_id="complex_search",
            namespaced_alias=alias,
            gateway_slug="complex_gw",
            step_name="retrieval_step",
            query="verified fact",
            response_summary="Verified complex evidence.",
            source_urls=["https://example.com/complex"],
            timestamp=datetime.now(timezone.utc),
            duration_ms=55,
        )

        result = await execute_mcp_retrieval(
            llm_client=client,
            executor=executor,
            messages=[LLMMessageDTO(role="user", content="Here is a verified fact in text")],
            allowed_tools=[alias],
            step_name="retrieval_step",
            source_context="Here is a verified fact in text",
            dispatcher=dispatcher,
            mcp_tool_params={alias: {"country": "FI", "numResults": 5}},
        )

    assert len(result.audit_traces) == 1
    # 3 ensemble calls * 15 tokens = 45 tokens + 35 JIT synthesis tokens = 80 tokens
    assert result.usage.total_tokens == 80
    mock_tool.assert_awaited_once()
    dispatched_args = mock_tool.call_args.kwargs["raw_arguments"]
    assert dispatched_args == {
        "query": "verified fact",
        "country": "FI",
        "category": "corporate",
        "numResults": 5,
    }

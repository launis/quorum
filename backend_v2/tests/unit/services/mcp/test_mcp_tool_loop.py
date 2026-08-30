"""Unit tests for deterministic MCP Tool Loop Conductor (Phase 0)."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel, ConfigDict, Field

from backend_v2.exceptions import SemanticEvidenceError
from backend_v2.models.domain.mcp import CitationExtractionItemDTO, CitationExtractionResult
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.services.mcp.mcp_tool_loop import execute_tool_loop


class MockResponseModel(BaseModel):
    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")
    score: float = Field(description="Test score.")
    reasoning: str = Field(description="Test reasoning.")


def _make_mock_llm_client() -> MagicMock:
    return MagicMock()


def _make_mock_executor(extracted_claims: list[str] | None = None) -> MagicMock:
    executor = MagicMock()

    async def mock_execute_structured_task(*args: Any, **kwargs: Any) -> tuple[Any, TokenUsage]:
        from backend_v2.models.domain.mcp import CitationCorrectionResult

        response_model = kwargs.get("response_model")
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
async def test_tool_loop_no_tools_passthrough() -> None:
    client = _make_mock_llm_client()
    executor = _make_mock_executor()
    result = await execute_tool_loop(
        llm_client=client,
        executor=executor,
        messages=[{"role": "user", "content": "test"}],
        response_model=MockResponseModel,
        allowed_tools=[],
        step_name="test_step",
    )
    assert result.result_data["score"] == 4.5
    assert len(result.audit_traces) == 0
    executor.execute_structured_task.assert_called_once()


@pytest.mark.asyncio
async def test_citation_extraction_empty_document() -> None:
    client = _make_mock_llm_client()
    executor = _make_mock_executor(extracted_claims=[])

    with patch("backend_v2.services.mcp.mcp_tool_loop.DISPATCHER.execute_tool") as mock_search:
        result = await execute_tool_loop(
            llm_client=client,
            executor=executor,
            messages=[{"role": "user", "content": "test"}],
            response_model=MockResponseModel,
            allowed_tools=["mcp_tavily_search"],
            step_name="test_step",
            source_context="some context",
        )

    assert len(result.audit_traces) == 0
    mock_search.assert_not_called()
    assert executor.execute_structured_task.call_count == 4


@pytest.mark.asyncio
async def test_citation_extraction_hallucinated_claim_rejected() -> None:
    client = _make_mock_llm_client()
    executor = _make_mock_executor(extracted_claims=["This claim does not exist in the source document"])

    with pytest.raises(SemanticEvidenceError) as exc_info:
        await execute_tool_loop(
            llm_client=client,
            executor=executor,
            messages=[{"role": "user", "content": "test"}],
            response_model=MockResponseModel,
            allowed_tools=["mcp_tavily_search"],
            step_name="test_step",
            source_context="Actual source context without the hallucinated claim.",
        )
    assert "Self-correction failed" in str(exc_info.value.message)


@pytest.mark.asyncio
async def test_execute_tool_loop_deterministic_search() -> None:
    client = _make_mock_llm_client()
    executor = _make_mock_executor(extracted_claims=["valid claim 1", "valid claim 2"])

    mock_settings = MagicMock()
    mock_settings.max_tool_calls_per_step = 3
    with (
        patch("backend_v2.services.mcp.mcp_tool_loop.DISPATCHER.execute_tool") as mock_search,
        patch("backend_v2.services.mcp.mcp_tool_loop.get_settings", return_value=mock_settings),
    ):
        from datetime import datetime, timezone

        from backend_v2.models.v2_core import MCPAuditTrace

        async def fake_search(*args: Any, **kwargs: Any):
            query = args[0] if args else kwargs.get("query", "test")
            return MCPAuditTrace(
                tool_id="mcp_tavily_search",
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
            allowed_tools=["mcp_tavily_search"],
            step_name="test_step",
            source_context="valid claim 1 and valid claim 2 are here.",
        )

    assert len(result.audit_traces) == 2
    assert result.audit_traces[0].query == "valid claim 1"
    assert result.audit_traces[1].query == "valid claim 2"
    assert mock_search.call_count == 2


@pytest.mark.asyncio
async def test_ensemble_vote_consensus() -> None:
    client = _make_mock_llm_client()
    executor = MagicMock()

    call_count = 0

    async def mock_execute_structured_task(*args: Any, **kwargs: Any) -> tuple[Any, TokenUsage]:
        nonlocal call_count
        response_model = kwargs.get("response_model")
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

    with patch("backend_v2.services.mcp.mcp_tool_loop.DISPATCHER.execute_tool") as mock_search:
        from datetime import datetime, timezone

        from backend_v2.models.v2_core import MCPAuditTrace

        async def fake_search(*args: Any, **kwargs: Any):
            query = kwargs.get("query") or (args[0] if args else "")
            return MCPAuditTrace(
                tool_id="mcp_tavily_search",
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
            allowed_tools=["mcp_tavily_search"],
            step_name="test_step",
            source_context="claim A claim B claim C",
        )

    assert len(result.audit_traces) == 1
    assert result.audit_traces[0].query == "claim B"
    assert result.usage.total_tokens == 115


@pytest.mark.asyncio
async def test_strictness_override_bypasses_physical_anchoring() -> None:
    client = _make_mock_llm_client()
    executor = _make_mock_executor(extracted_claims=["hallucinated claim"])

    with patch("backend_v2.services.mcp.mcp_tool_loop.DISPATCHER.execute_tool") as mock_search:
        from datetime import datetime, timezone

        from backend_v2.models.v2_core import MCPAuditTrace

        async def fake_search(*args: Any, **kwargs: Any):
            query = kwargs.get("query") or (args[0] if args else "")
            return MCPAuditTrace(
                tool_id="mcp_tavily_search",
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
            allowed_tools=["mcp_tavily_search"],
            step_name="test_step",
            source_context="totally unrelated source context",
            validation_context={"strictness_level": 85},
        )

    assert len(result.audit_traces) == 1
    assert result.audit_traces[0].query == "hallucinated claim"
    assert mock_search.call_count == 1


@pytest.mark.asyncio
async def test_agentic_self_reflection_success() -> None:
    client = _make_mock_llm_client()

    from backend_v2.models.domain.mcp import CitationCorrectionResult

    async def mock_execute_structured_task(*args: Any, **kwargs: Any) -> tuple[Any, TokenUsage]:
        response_model = kwargs.get("response_model")
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

    with patch("backend_v2.services.mcp.mcp_tool_loop.DISPATCHER.execute_tool") as mock_search:
        from datetime import datetime, timezone

        from backend_v2.models.v2_core import MCPAuditTrace

        async def fake_search(*args: Any, **kwargs: Any):
            query = kwargs.get("query") or (args[0] if args else "")
            return MCPAuditTrace(
                tool_id="mcp_tavily_search",
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
            allowed_tools=["mcp_tavily_search"],
            step_name="test_step",
            source_context="source context containing precise claim here",
            validation_context={"strictness_level": 100},
        )

    assert len(result.audit_traces) == 1
    assert mock_search.call_count == 1
    assert result.usage.total_tokens == 145


@pytest.mark.asyncio
async def test_agentic_self_reflection_failure_raises_error() -> None:
    client = _make_mock_llm_client()

    from backend_v2.models.domain.mcp import CitationCorrectionResult

    async def mock_execute_structured_task(*args: Any, **kwargs: Any) -> tuple[Any, TokenUsage]:
        response_model = kwargs.get("response_model")
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
            allowed_tools=["mcp_tavily_search"],
            step_name="test_step",
            source_context="source context with no overlap at all",
            validation_context={"strictness_level": 100},
        )
    assert "Self-correction failed" in str(exc_info.value.message)


def test_validate_query_relevance() -> None:
    """Tests validate_query_relevance for various contexts and query inputs."""
    from backend_v2.services.mcp.mcp_tool_loop import validate_query_relevance

    # Empty context or empty query
    assert validate_query_relevance("test query", "") is True
    assert validate_query_relevance("  ", "some context") is True

    # Relevant query (words overlap)
    assert (
        validate_query_relevance("Harvard medical research", "This document contains Harvard clinical findings.")
        is True
    )

    # Irrelevant query (no words overlap)
    assert (
        validate_query_relevance("Bitcoin exchange rate", "This document discusses pediatric nutrition exclusively.")
        is False
    )


def test_is_source_sufficient() -> None:
    """Tests is_source_sufficient against MIN_CHARS threshold."""
    from backend_v2.models.enums import SourceSufficiencyThreshold
    from backend_v2.services.mcp.mcp_tool_loop import is_source_sufficient

    short_text = "short text"
    assert is_source_sufficient(short_text) is False

    long_text = "a" * (SourceSufficiencyThreshold.MIN_CHARS.value + 10)
    assert is_source_sufficient(long_text) is True


def test_build_tool_evidence_message() -> None:
    """Tests _build_tool_evidence_message formatting for both empty and populated audit traces."""
    import datetime

    from backend_v2.models.v2_core import MCPAuditTrace
    from backend_v2.services.mcp.mcp_tool_loop import _build_tool_evidence_message

    # Empty response summary and empty sources
    empty_trace = MCPAuditTrace(
        id="t1",
        tool_id="mcp_tavily_search",
        step_name="step",
        query="query",
        reasoning="r",
        response_summary="",
        source_urls=[],
        timestamp=datetime.datetime.now(datetime.timezone.utc),
        duration_ms=10,
    )
    empty_msg = _build_tool_evidence_message(empty_trace, "call_123")
    assert empty_msg["role"] == "tool"
    assert empty_msg["tool_call_id"] == "call_123"
    assert "Search returned no results" in empty_msg["content"]

    # Populated trace
    populated_trace = MCPAuditTrace(
        id="t2",
        tool_id="mcp_tavily_search",
        step_name="step",
        query="verified query",
        reasoning="r",
        response_summary="Verified finding summary",
        source_urls=["https://example.com/source1"],
        timestamp=datetime.datetime.now(datetime.timezone.utc),
        duration_ms=10,
    )
    pop_msg = _build_tool_evidence_message(populated_trace, "call_456")
    assert pop_msg["role"] == "tool"
    assert "<query>verified query</query>" in pop_msg["content"]
    assert "<summary>Verified finding summary</summary>" in pop_msg["content"]
    assert "<url>https://example.com/source1</url>" in pop_msg["content"]


@pytest.mark.asyncio
async def test_execute_tool_loop_with_synthesis_instructions() -> None:
    """Tests execute_tool_loop injecting synthesis formatting constraints."""
    client = _make_mock_llm_client()
    executor = _make_mock_executor(extracted_claims=["valid claim"])

    synthesis_payload = {
        "synthesis_preamble": "Custom preamble for profile.",
        "synthesis_length_limit": 200,
    }

    with patch("backend_v2.services.mcp.mcp_tool_loop.DISPATCHER.execute_tool") as mock_search:
        import datetime

        from backend_v2.models.v2_core import MCPAuditTrace

        mock_search.return_value = MCPAuditTrace(
            tool_id="mcp_tavily_search",
            step_name="test_synth_step",
            query="valid claim",
            response_summary="Evidence summary",
            source_urls=["https://example.com"],
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            duration_ms=50,
        )

        result = await execute_tool_loop(
            llm_client=client,
            executor=executor,
            messages=[{"role": "system", "content": "Base prompt."}],
            response_model=MockResponseModel,
            allowed_tools=["mcp_tavily_search"],
            step_name="test_synth_step",
            source_context="source document text with valid claim here",
            synthesis_instructions=synthesis_payload,
        )

    assert result.result_data["score"] == 4.5
    call_args = executor.execute_structured_task.call_args.kwargs
    first_msg = call_args["messages"][0]["content"]
    assert "<synthesis_preamble>Custom preamble for profile.</synthesis_preamble>" in first_msg
    assert "<synthesis_length_limit>200</synthesis_length_limit>" in first_msg


@pytest.mark.asyncio
async def test_execute_tool_loop_invalid_synthesis_instructions_raises_app_exception() -> None:
    """Tests execute_tool_loop raising AppException on invalid synthesis instructions."""
    from backend_v2.exceptions import AppException

    client = _make_mock_llm_client()
    executor = _make_mock_executor(extracted_claims=["valid claim"])

    with patch("backend_v2.services.mcp.mcp_tool_loop.DISPATCHER.execute_tool") as mock_search:
        import datetime

        from backend_v2.models.v2_core import MCPAuditTrace

        mock_search.return_value = MCPAuditTrace(
            tool_id="mcp_tavily_search",
            step_name="test_synth_step",
            query="valid claim",
            response_summary="Evidence summary",
            source_urls=["https://example.com"],
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            duration_ms=50,
        )

        with pytest.raises(AppException) as exc_info:
            await execute_tool_loop(
                llm_client=client,
                executor=executor,
                messages=[{"role": "user", "content": "test"}],
                response_model=MockResponseModel,
                allowed_tools=["mcp_tavily_search"],
                step_name="test_synth_step",
                source_context="source document text with valid claim here",
                synthesis_instructions="invalid_non_dict_payload",
            )
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_execute_tool_loop_phase2_failure_raises_app_exception() -> None:
    """Tests execute_tool_loop catching unexpected Phase 2 crash and raising AppException."""
    from backend_v2.exceptions import AppException

    client = _make_mock_llm_client()

    async def mock_execute_structured_task(*args: Any, **kwargs: Any) -> tuple[Any, TokenUsage]:
        response_model = kwargs.get("response_model")
        if response_model == CitationExtractionResult:
            citations = [CitationExtractionItemDTO(claim_text="valid claim", search_query="valid claim", reasoning="r")]
            return (
                CitationExtractionResult(citations=citations),
                TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            )
        raise RuntimeError("Unexpected LLM crash in Phase 2")

    executor = MagicMock()
    executor.execute_structured_task = AsyncMock(side_effect=mock_execute_structured_task)

    with patch("backend_v2.services.mcp.mcp_tool_loop.DISPATCHER.execute_tool") as mock_search:
        import datetime

        from backend_v2.models.v2_core import MCPAuditTrace

        mock_search.return_value = MCPAuditTrace(
            tool_id="mcp_tavily_search",
            step_name="test_crash_step",
            query="valid claim",
            response_summary="Evidence summary",
            source_urls=[],
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            duration_ms=50,
        )

        with pytest.raises(AppException) as exc_info:
            await execute_tool_loop(
                llm_client=client,
                executor=executor,
                messages=[{"role": "user", "content": "test"}],
                response_model=MockResponseModel,
                allowed_tools=["mcp_tavily_search"],
                step_name="test_crash_step",
                source_context="source document with valid claim here",
            )
    assert exc_info.value.status_code == 500


@pytest.mark.asyncio
async def test_ensemble_all_runs_fail_raises_app_exception() -> None:
    """Tests that Phase 0 raises AppException when all 3 ensemble extractions fail."""
    from backend_v2.exceptions import AppException

    client = _make_mock_llm_client()
    executor = MagicMock()
    executor.execute_structured_task = AsyncMock(side_effect=RuntimeError("Extraction failed"))

    with pytest.raises(AppException) as exc_info:
        await execute_tool_loop(
            llm_client=client,
            executor=executor,
            messages=[{"role": "user", "content": "test"}],
            response_model=MockResponseModel,
            allowed_tools=["mcp_tavily_search"],
            step_name="test_step",
            source_context="source context",
        )
    assert exc_info.value.status_code == 502


@pytest.mark.asyncio
async def test_max_tool_calls_limit_reached(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tests that max_tool_calls_per_step limit stops further tool calls."""
    from backend_v2.settings import get_settings

    monkeypatch.setattr(get_settings(), "max_tool_calls_per_step", 1)

    client = _make_mock_llm_client()
    executor = _make_mock_executor(extracted_claims=["claim1", "claim2", "claim3"])

    with patch("backend_v2.services.mcp.mcp_tool_loop.DISPATCHER.execute_tool") as mock_search:
        import datetime

        from backend_v2.models.v2_core import MCPAuditTrace

        mock_search.return_value = MCPAuditTrace(
            tool_id="mcp_tavily_search",
            step_name="test_step",
            query="claim1",
            response_summary="summary",
            source_urls=[],
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            duration_ms=10,
        )

        result = await execute_tool_loop(
            llm_client=client,
            executor=executor,
            messages=[{"role": "user", "content": "test"}],
            response_model=MockResponseModel,
            allowed_tools=["mcp_tavily_search"],
            step_name="test_step",
            source_context="claim1 and claim2 and claim3 are in source",
        )

    assert len(result.audit_traces) == 1
    assert mock_search.call_count == 1


@pytest.mark.asyncio
async def test_extraction_dict_model_validation() -> None:
    """Tests that a dict returned for CitationExtractionResult is properly model_validated."""
    client = _make_mock_llm_client()

    async def mock_execute_structured_task(*args: Any, **kwargs: Any) -> tuple[Any, TokenUsage]:
        response_model = kwargs.get("response_model")
        if response_model == CitationExtractionResult:
            # Return raw dictionary instead of Pydantic model instance
            return (
                {"citations": [{"claim_text": "claim1", "search_query": "claim1", "reasoning": "r"}]},
                TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            )
        mock_result = MockResponseModel(score=4.5, reasoning="Good")
        return (mock_result, TokenUsage(prompt_tokens=50, completion_tokens=20, total_tokens=70))

    executor = MagicMock()
    executor.execute_structured_task = AsyncMock(side_effect=mock_execute_structured_task)

    with patch("backend_v2.services.mcp.mcp_tool_loop.DISPATCHER.execute_tool") as mock_search:
        import datetime

        from backend_v2.models.v2_core import MCPAuditTrace

        mock_search.return_value = MCPAuditTrace(
            tool_id="mcp_tavily_search",
            step_name="test_step",
            query="claim1",
            response_summary="summary",
            source_urls=[],
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            duration_ms=10,
        )

        result = await execute_tool_loop(
            llm_client=client,
            executor=executor,
            messages=[{"role": "user", "content": "test"}],
            response_model=MockResponseModel,
            allowed_tools=["mcp_tavily_search"],
            step_name="test_step",
            source_context="claim1 is here",
        )

    assert len(result.audit_traces) == 1


@pytest.mark.asyncio
async def test_phase2_app_exception_passthrough() -> None:
    """Tests that an AppException raised during Phase 2 is directly re-raised without re-wrapping."""
    from backend_v2.exceptions import AppException

    client = _make_mock_llm_client()

    async def mock_execute_structured_task(*args: Any, **kwargs: Any) -> tuple[Any, TokenUsage]:
        response_model = kwargs.get("response_model")
        if response_model == CitationExtractionResult:
            citations = [CitationExtractionItemDTO(claim_text="valid claim", search_query="valid claim", reasoning="r")]
            return (
                CitationExtractionResult(citations=citations),
                TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15),
            )
        raise AppException(message="Specific domain error in phase 2", status_code=422, details={})

    executor = MagicMock()
    executor.execute_structured_task = AsyncMock(side_effect=mock_execute_structured_task)

    with patch("backend_v2.services.mcp.mcp_tool_loop.DISPATCHER.execute_tool") as mock_search:
        import datetime

        from backend_v2.models.v2_core import MCPAuditTrace

        mock_search.return_value = MCPAuditTrace(
            tool_id="mcp_tavily_search",
            step_name="test_crash_step",
            query="valid claim",
            response_summary="Evidence",
            source_urls=[],
            timestamp=datetime.datetime.now(datetime.timezone.utc),
            duration_ms=50,
        )

        with pytest.raises(AppException) as exc_info:
            await execute_tool_loop(
                llm_client=client,
                executor=executor,
                messages=[{"role": "user", "content": "test"}],
                response_model=MockResponseModel,
                allowed_tools=["mcp_tavily_search"],
                step_name="test_crash_step",
                source_context="source document with valid claim here",
            )
    assert exc_info.value.status_code == 422

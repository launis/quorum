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

    with patch("backend_v2.services.mcp.mcp_tool_loop._execute_tavily_search") as mock_search:
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

    with patch("backend_v2.services.mcp.mcp_tool_loop._execute_tavily_search") as mock_search:
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

    with patch("backend_v2.services.mcp.mcp_tool_loop._execute_tavily_search") as mock_search:
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

    with patch("backend_v2.services.mcp.mcp_tool_loop._execute_tavily_search") as mock_search:
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

    with patch("backend_v2.services.mcp.mcp_tool_loop._execute_tavily_search") as mock_search:
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

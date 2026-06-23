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
        response_model = kwargs.get("response_model")
        if response_model == CitationExtractionResult:
            citations = [CitationExtractionItemDTO(claim_text=c, search_query=c) for c in (extracted_claims or [])]
            return (
                CitationExtractionResult(citations=citations),
                TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=10),
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
    assert executor.execute_structured_task.call_count == 2


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
    assert "not found in source text" in str(exc_info.value.message)


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

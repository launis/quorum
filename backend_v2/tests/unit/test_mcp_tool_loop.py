"""Unit tests for MCP Tool Loop Conductor.

All tests use mocked LLM and Tavily — no live API calls.
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel, ConfigDict, Field

from backend_v2.services.mcp.mcp_tool_loop import (
    MCPToolLoopResult,
    execute_tool_loop,
)


class MockResponseModel(BaseModel):
    """Minimal Pydantic schema for test verification."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    score: float = Field(description="Test score.")
    reasoning: str = Field(description="Test reasoning.")


def _make_mock_llm_client(
    chat_returns: str | dict[str, Any] | None = None,
    structured_returns: tuple[Any, dict[str, Any]] | None = None,
) -> MagicMock:
    """Build a mock LLMClient with configurable returns."""
    client = MagicMock()

    # run_chat returns
    if chat_returns is not None:
        client.run_chat = AsyncMock(return_value=chat_returns)
    else:
        client.run_chat = AsyncMock(return_value="Direct text response.")

    # run_structured_task returns
    if structured_returns is not None:
        client.run_structured_task = AsyncMock(return_value=structured_returns)
    else:
        mock_result = MockResponseModel(score=4.5, reasoning="Well-supported claim.")
        client.run_structured_task = AsyncMock(return_value=(mock_result, {"total_tokens": 100}))

    return client


@pytest.mark.asyncio
async def test_tool_loop_no_tools_passthrough() -> None:
    """Empty allowed_tools → direct structured output, zero overhead."""
    mock_result = MockResponseModel(score=3.0, reasoning="No tools needed.")
    client = _make_mock_llm_client(structured_returns=(mock_result, {"total_tokens": 50}))

    result = await execute_tool_loop(
        llm_client=client,
        messages=[{"role": "user", "content": "test"}],
        response_model=MockResponseModel,
        allowed_tools=[],
        step_name="test_step",
    )

    assert isinstance(result, MCPToolLoopResult)
    assert result.result_data["score"] == 3.0
    assert len(result.audit_traces) == 0
    # run_chat should NOT be called when no tools
    client.run_chat.assert_not_called()
    client.run_structured_task.assert_called_once()


@pytest.mark.asyncio
async def test_tool_loop_single_search() -> None:
    """LLM requests one search → evidence injected → matrix completed."""
    # Phase 1: LLM returns a tool_call
    tool_call_response = {
        "tool_calls": [
            {
                "function": {
                    "name": "mcp_tavily_search",
                    "arguments": '{"query": "Finland population 2024"}',
                },
            }
        ],
        "content": "",
    }
    # After evidence injection, LLM returns text (no more tool calls)
    # We set side_effect: first call returns tool_call, second returns text
    mock_client = _make_mock_llm_client()
    mock_client.run_chat = AsyncMock(
        side_effect=[
            tool_call_response,
            "Direct response after evidence.",
        ]
    )

    mock_result = MockResponseModel(score=4.5, reasoning="Supported by search.")
    mock_client.run_structured_task = AsyncMock(return_value=(mock_result, {"total_tokens": 200}))

    with patch("backend_v2.services.mcp.mcp_tool_loop._execute_tavily_search") as mock_search:
        from datetime import datetime, timezone

        from backend_v2.models.v2_core import MCPAuditTrace

        mock_search.return_value = MCPAuditTrace(
            tool_id="mcp_tavily_search",
            step_name="step_judge",
            query="Finland population 2024",
            response_summary="Finland has 5.6 million people.",
            source_urls=["https://example.com"],
            timestamp=datetime.now(timezone.utc),
            duration_ms=500,
        )

        result = await execute_tool_loop(
            llm_client=mock_client,
            messages=[{"role": "user", "content": "evaluate Finland"}],
            response_model=MockResponseModel,
            allowed_tools=["mcp_tavily_search"],
            step_name="step_judge",
        )

    assert result.result_data["score"] == 4.5
    assert len(result.audit_traces) == 1
    assert result.audit_traces[0].query == "Finland population 2024"
    assert "https://example.com" in result.audit_traces[0].source_urls
    mock_client.run_structured_task.assert_called_once()


@pytest.mark.asyncio
async def test_tool_loop_max_calls_enforced() -> None:
    """LLM keeps requesting searches → hard cap at MAX_TOOL_CALLS."""
    # LLM always returns a tool_call (infinite loop attempt)
    tool_call_response = {
        "tool_calls": [
            {
                "function": {
                    "name": "mcp_tavily_search",
                    "arguments": '{"query": "test query"}',
                },
            }
        ],
        "content": "",
    }
    mock_client = _make_mock_llm_client()
    mock_client.run_chat = AsyncMock(return_value=tool_call_response)

    mock_result = MockResponseModel(score=2.0, reasoning="Limited evidence.")
    mock_client.run_structured_task = AsyncMock(return_value=(mock_result, {"total_tokens": 300}))

    with patch("backend_v2.services.mcp.mcp_tool_loop._execute_tavily_search") as mock_search:
        from datetime import datetime, timezone

        from backend_v2.models.v2_core import MCPAuditTrace

        mock_search.return_value = MCPAuditTrace(
            tool_id="mcp_tavily_search",
            step_name="step_infinite",
            query="test query",
            response_summary="Answer.",
            source_urls=[],
            timestamp=datetime.now(timezone.utc),
            duration_ms=100,
        )

        result = await execute_tool_loop(
            llm_client=mock_client,
            messages=[{"role": "user", "content": "test"}],
            response_model=MockResponseModel,
            allowed_tools=["mcp_tavily_search"],
            step_name="step_infinite",
        )

    # Should enforce max 3 tool calls (Restored base limit)
    assert len(result.audit_traces) == 3
    # Structured output still produced
    assert result.result_data["score"] == 2.0


@pytest.mark.asyncio
async def test_tool_loop_tavily_failure_graceful() -> None:
    """Tavily throws → audit logged with empty response → matrix still produced."""
    tool_call_response = {
        "tool_calls": [
            {
                "function": {
                    "name": "mcp_tavily_search",
                    "arguments": '{"query": "broken query"}',
                },
            }
        ],
        "content": "",
    }
    mock_client = _make_mock_llm_client()
    # First chat returns tool_call, second returns text (loop exits)
    mock_client.run_chat = AsyncMock(
        side_effect=[
            tool_call_response,
            "No more searches.",
        ]
    )

    mock_result = MockResponseModel(score=3.5, reasoning="Proceeded without evidence.")
    mock_client.run_structured_task = AsyncMock(return_value=(mock_result, {"total_tokens": 150}))

    with patch("backend_v2.services.mcp.mcp_tool_loop._execute_tavily_search") as mock_search:
        from datetime import datetime, timezone

        from backend_v2.models.v2_core import MCPAuditTrace

        # Simulate a failed search — audit trace with empty response (Graceful Degradation)
        mock_search.return_value = MCPAuditTrace(
            tool_id="mcp_tavily_search",
            step_name="step_broken",
            query="broken query",
            response_summary="",
            source_urls=[],
            timestamp=datetime.now(timezone.utc),
            duration_ms=50,
        )

        result = await execute_tool_loop(
            llm_client=mock_client,
            messages=[{"role": "user", "content": "test"}],
            response_model=MockResponseModel,
            allowed_tools=["mcp_tavily_search"],
            step_name="step_broken",
        )

    # Audit trace logged with empty response (Graceful Degradation)
    assert len(result.audit_traces) == 1
    assert result.audit_traces[0].response_summary == ""
    # Matrix still produced successfully
    assert result.result_data["score"] == 3.5


# ============================================================================
# REGRESSION TESTS — March 2026 MCP Pipeline Fixes
# ============================================================================


@pytest.mark.asyncio
async def test_tool_call_id_preserved_from_llm() -> None:
    """Regression: tool_call_id in evidence message MUST match the LLM's original call ID.

    Bug: We generated our own ID (mcp_tavily_search_{step_name}) instead of using
    the LLM's call_00f4cd04... ID, causing LiteLLM/Gemini 'Missing corresponding
    tool call' crash.
    """
    # LLM returns a tool_call with a SPECIFIC id
    llm_call_id = "call_abc123def456"
    tool_call_response = {
        "tool_calls": [
            {
                "id": llm_call_id,  # ← This is the LLM's original ID
                "function": {
                    "name": "mcp_tavily_search",
                    "arguments": '{"query": "test regression"}',
                },
            }
        ],
        "content": "",
    }

    mock_client = _make_mock_llm_client()
    mock_client.run_chat = AsyncMock(
        side_effect=[
            tool_call_response,
            "Done searching.",
        ]
    )

    mock_result = MockResponseModel(score=5.0, reasoning="Regression test.")
    mock_client.run_structured_task = AsyncMock(return_value=(mock_result, {"total_tokens": 100}))

    with patch("backend_v2.services.mcp.mcp_tool_loop._execute_tavily_search") as mock_search:
        from datetime import datetime, timezone

        from backend_v2.models.v2_core import MCPAuditTrace

        mock_search.return_value = MCPAuditTrace(
            tool_id="mcp_tavily_search",
            step_name="step_regression",
            query="test regression",
            response_summary="Result found.",
            source_urls=["https://example.com"],
            timestamp=datetime.now(timezone.utc),
            duration_ms=200,
        )

        result = await execute_tool_loop(
            llm_client=mock_client,
            messages=[{"role": "user", "content": "test"}],
            response_model=MockResponseModel,
            allowed_tools=["mcp_tavily_search"],
            step_name="step_regression",
        )

    assert result.result_data["score"] == 5.0

    # Verify the structured task was called with messages containing the CORRECT tool_call_id
    call_args = mock_client.run_structured_task.call_args
    final_messages = call_args.kwargs.get("messages", call_args.args[0] if call_args.args else [])

    # Find the tool response message in final_messages
    tool_msgs = [m for m in final_messages if m.get("role") == "tool"]
    assert len(tool_msgs) >= 1, "Expected at least one tool response message"
    assert tool_msgs[0]["tool_call_id"] == llm_call_id, (
        f"tool_call_id mismatch: expected '{llm_call_id}', got '{tool_msgs[0]['tool_call_id']}'"
    )


def test_build_tool_evidence_message_uses_explicit_id() -> None:
    """Regression: _build_tool_evidence_message must use the provided tool_call_id."""
    from datetime import datetime, timezone

    from backend_v2.models.v2_core import MCPAuditTrace
    from backend_v2.services.mcp.mcp_tool_loop import _build_tool_evidence_message

    audit = MCPAuditTrace(
        tool_id="mcp_tavily_search",
        step_name="step_test",
        query="test query",
        response_summary="Some results.",
        source_urls=["https://example.com"],
        timestamp=datetime.now(timezone.utc),
        duration_ms=100,
    )

    llm_id = "call_xyz789"
    msg = _build_tool_evidence_message(audit, tool_call_id=llm_id)

    assert msg["role"] == "tool"
    assert msg["tool_call_id"] == llm_id, "Must use the LLM's original call ID"
    assert "test query" in msg["content"]


def test_build_tool_evidence_message_empty_results() -> None:
    """Empty search results still use the correct tool_call_id."""
    from datetime import datetime, timezone

    from backend_v2.models.v2_core import MCPAuditTrace
    from backend_v2.services.mcp.mcp_tool_loop import _build_tool_evidence_message

    audit = MCPAuditTrace(
        tool_id="mcp_tavily_search",
        step_name="step_empty",
        query="nothing",
        response_summary="",
        source_urls=[],
        timestamp=datetime.now(timezone.utc),
        duration_ms=50,
    )

    llm_id = "call_empty123"
    msg = _build_tool_evidence_message(audit, tool_call_id=llm_id)

    assert msg["tool_call_id"] == llm_id
    assert "no results" in msg["content"].lower()


@pytest.mark.asyncio
async def test_phase2_messages_contain_tool_roles() -> None:
    """Regression: Phase 2 messages must include assistant+tool roles (not flattened).

    Bug: run_chat was flattening all messages to system+user, silently dropping
    assistant and tool messages from the evidence injection.
    """
    llm_call_id = "call_phase2_test"
    tool_call_response = {
        "tool_calls": [
            {
                "id": llm_call_id,
                "function": {
                    "name": "mcp_tavily_search",
                    "arguments": '{"query": "phase 2 test"}',
                },
            }
        ],
        "content": "",
    }

    mock_client = _make_mock_llm_client()
    mock_client.run_chat = AsyncMock(
        side_effect=[
            tool_call_response,
            "No more tools.",
        ]
    )

    mock_result = MockResponseModel(score=4.0, reasoning="Phase 2 test.")
    mock_client.run_structured_task = AsyncMock(return_value=(mock_result, {"total_tokens": 150}))

    with patch("backend_v2.services.mcp.mcp_tool_loop._execute_tavily_search") as mock_search:
        from datetime import datetime, timezone

        from backend_v2.models.v2_core import MCPAuditTrace

        mock_search.return_value = MCPAuditTrace(
            tool_id="mcp_tavily_search",
            step_name="step_p2",
            query="phase 2 test",
            response_summary="Evidence found.",
            source_urls=["https://evidence.com"],
            timestamp=datetime.now(timezone.utc),
            duration_ms=300,
        )

        await execute_tool_loop(
            llm_client=mock_client,
            messages=[{"role": "system", "content": "You are a judge."}, {"role": "user", "content": "evaluate"}],
            response_model=MockResponseModel,
            allowed_tools=["mcp_tavily_search"],
            step_name="step_p2",
        )

    # Verify Phase 2 received messages with ALL roles (not just system+user)
    call_args = mock_client.run_structured_task.call_args
    final_messages = call_args.kwargs.get("messages", call_args.args[0] if call_args.args else [])
    roles = [m.get("role") for m in final_messages]

    assert "assistant" in roles, f"Missing 'assistant' tool_call message in Phase 2. Roles: {roles}"
    assert "tool" in roles, f"Missing 'tool' evidence message in Phase 2. Roles: {roles}"
    assert "user" in roles, f"Missing 'user' messages in Phase 2. Roles: {roles}"


# ============================================================================
# FAULT INJECTION TESTS — Would have CAUGHT the original bugs
# ============================================================================


def test_static_tool_call_id_causes_mismatch() -> None:
    """FAULT INJECTION: Proves that generating a static ID instead of using LLM's ID
    would produce a mismatched tool_call_id — the exact bug that crashed LiteLLM/Gemini.
    """
    from datetime import datetime, timezone

    from backend_v2.models.v2_core import MCPAuditTrace
    from backend_v2.services.mcp.mcp_tool_loop import _build_tool_evidence_message

    audit = MCPAuditTrace(
        tool_id="mcp_tavily_search",
        step_name="steprule_factcheck1234ab",
        query="test",
        response_summary="result",
        source_urls=[],
        timestamp=datetime.now(timezone.utc),
        duration_ms=100,
    )

    # The LLM returns THIS id
    llm_id = "call_00f4cd04b21447a19c536e214651"

    # OLD BUG: would have generated "mcp_tavily_search_steprule_factcheck1234ab"
    static_id = f"{audit.tool_id}_{audit.step_name}"

    # Prove the mismatch
    assert static_id != llm_id, "Static ID should NOT match LLM's dynamic call ID"

    # Prove the fix uses the CORRECT id
    msg = _build_tool_evidence_message(audit, tool_call_id=llm_id)
    assert msg["tool_call_id"] == llm_id
    assert msg["tool_call_id"] != static_id


def test_llm_response_accepts_tool_call_messages() -> None:
    """FAULT INJECTION: Proves that LLMResponse.messages MUST accept dicts with
    content=None and tool_calls=[list] — the exact structure that crashed Pydantic.

    OLD BUG: messages was typed as list[dict[str, str]] which rejected None and list values.
    """
    from backend_v2.models.llm import LLMResponse

    # This is the exact message structure that caused the ValidationError
    tool_call_assistant_msg = {
        "role": "assistant",
        "content": None,  # ← OLD BUG: str type rejected None
        "tool_calls": [  # ← OLD BUG: str type rejected list
            {
                "id": "call_123",
                "function": {"name": "mcp_tavily_search", "arguments": '{"query": "test"}'},
                "type": "function",
            }
        ],
    }
    tool_response_msg = {
        "role": "tool",
        "tool_call_id": "call_123",
        "content": "Search results here.",
    }

    # Must NOT raise ValidationError
    response = LLMResponse(
        content="Final answer.",
        token_usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        messages=[
            {"role": "system", "content": "You are a judge."},
            {"role": "user", "content": "Evaluate this."},
            tool_call_assistant_msg,
            tool_response_msg,
        ],
    )

    assert response.messages is not None
    assert len(response.messages) == 4
    # Verify the None content survived
    assert response.messages[2]["content"] is None
    # Verify the list tool_calls survived
    assert isinstance(response.messages[2]["tool_calls"], list)


def test_llm_response_rejects_missing_content() -> None:
    """LLMResponse.content (the top-level field) must still be a required string.
    Only messages[].content can be None (for assistant tool_call messages).
    """
    import pydantic

    from backend_v2.models.llm import LLMResponse

    with pytest.raises(pydantic.ValidationError):
        LLMResponse(
            content=None,  # type: ignore
            token_usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        )


@pytest.mark.asyncio
async def test_tool_loop_malformed_json_fails_fast() -> None:
    """FAULT INJECTION: Proves that LLM hallucinating a malformed JSON argument
    raises a Fail-Fast VALIDATION_FAILED AppException instead of duck-typing.
    """
    from backend_v2.exceptions import AppException

    tool_call_response = {
        "tool_calls": [
            {
                "function": {
                    "name": "mcp_tavily_search",
                    "arguments": "I am not JSON, just a raw string hallucination.",
                },
            }
        ],
        "content": "",
    }

    mock_client = _make_mock_llm_client()
    mock_client.run_chat = AsyncMock(return_value=tool_call_response)

    with pytest.raises(AppException) as exc_info:
        await execute_tool_loop(
            llm_client=mock_client,
            messages=[{"role": "user", "content": "test"}],
            response_model=MockResponseModel,
            allowed_tools=["mcp_tavily_search"],
            step_name="step_duck_typing",
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == "VALIDATION_FAILED"
    assert "malformed JSON for tool arguments" in exc_info.value.message

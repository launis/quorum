from unittest.mock import AsyncMock
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.mcp import (
    MCPToolLoopResult,
    OpenAIFunctionCallDTO,
    OpenAIProbeResponseDTO,
    OpenAIToolCallDTO,
    TavilyToolArgsDTO,
)
from backend_v2.models.v2_core import MCPAuditTrace


def test_openai_function_call_dto_valid() -> None:
    data = {"name": "mcp_tavily_search", "arguments": '{"query": "test"}'}
    model = OpenAIFunctionCallDTO.model_validate(data)
    assert model.name == "mcp_tavily_search"
    assert model.arguments == '{"query": "test"}'


def test_openai_function_call_dto_forbids_extra() -> None:
    data = {"name": "mcp_tavily_search", "arguments": '{"query": "test"}', "extra_field": "not allowed"}
    with pytest.raises(ValidationError):
        OpenAIFunctionCallDTO.model_validate(data)


def test_openai_tool_call_dto_valid() -> None:
    data = {
        "id": "call_123",
        "type": "function",
        "function": {"name": "mcp_tavily_search", "arguments": '{"query": "test"}'},
    }
    model = OpenAIToolCallDTO.model_validate(data)
    assert model.id == "call_123"
    assert model.type == "function"
    assert model.function.name == "mcp_tavily_search"


def test_openai_tool_call_dto_accepts_provider_specific_fields() -> None:
    data = {
        "id": "call_123",
        "type": "function",
        "function": {"name": "mcp_tavily_search", "arguments": '{"query": "test"}'},
        "provider_specific_fields": {"thought_signature": "Cu...7yJQl4aGsEaLDmOw1eSQ=="},
    }
    model = OpenAIToolCallDTO.model_validate(data)
    assert model.id == "call_123"


def test_openai_probe_response_dto_valid() -> None:
    data = {
        "tool_calls": [
            {
                "id": "call_123",
                "type": "function",
                "function": {"name": "mcp_tavily_search", "arguments": '{"query": "test"}'},
            }
        ],
        "content": "thinking...",
    }
    model = OpenAIProbeResponseDTO.model_validate(data)
    assert model.content == "thinking..."
    assert model.tool_calls is not None
    assert len(model.tool_calls) == 1
    assert model.tool_calls[0].id == "call_123"


def test_openai_probe_response_dto_forbids_extra() -> None:
    data = {
        "tool_calls": [],
        "content": "hello",
        "usage": {},  # not allowed
    }
    with pytest.raises(ValidationError):
        OpenAIProbeResponseDTO.model_validate(data)


def test_tavily_tool_args_dto_valid() -> None:
    data = {"query": "test query"}
    model = TavilyToolArgsDTO.model_validate(data)
    assert model.query == "test query"


def test_mcp_tool_loop_result_valid() -> None:
    audit = MCPAuditTrace(
        tool_id="mcp_tavily_search",
        step_name="test_step",
        query="test query",
        response_summary="summary",
        source_urls=["http://example.com"],
        timestamp=datetime.now(timezone.utc),
        duration_ms=100,
    )
    data = {
        "result_data": {"key": "value"},
        "audit_traces": [audit.model_dump()],
        "usage": {"prompt_tokens": 100, "completion_tokens": 0, "total_tokens": 100},
    }
    model = MCPToolLoopResult.model_validate(data)
    assert model.result_data["key"] == "value"
    assert len(model.audit_traces) == 1
    assert model.audit_traces[0].query == "test query"
    assert model.usage.total_tokens == 100

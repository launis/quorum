"""Unit tests for ToolDispatcher in MCP services."""

from __future__ import annotations

from typing import Any

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.domain.tools import BaseTool
from backend_v2.models.dtos.mcp import MCPFunctionDefinitionDTO, MCPToolDeclarationDTO
from backend_v2.services.mcp.dispatcher import ToolDispatcher


class DummyTestTool(BaseTool):
    """Concrete mock tool for testing ToolDispatcher."""

    def __init__(self, tool_id: str, declaration: MCPToolDeclarationDTO) -> None:
        self._tool_id = tool_id
        self._declaration = declaration
        self.last_kwargs: dict[str, Any] = {}

    @property
    def tool_id(self) -> str:
        return self._tool_id

    @property
    def declaration(self) -> MCPToolDeclarationDTO:
        return self._declaration

    async def execute(self, **kwargs: Any) -> MCPAuditTrace:
        self.last_kwargs = kwargs
        return MCPAuditTrace(
            tool_id=self._tool_id,
            step_name="step_test",
            query=str(kwargs.get("query", "default_query")),
            response_summary="dummy output",
        )


def _create_dummy_tool(tool_id: str) -> DummyTestTool:
    fn_def = MCPFunctionDefinitionDTO(
        name=tool_id,
        description=f"Description for {tool_id}",
        parameters={"type": "object", "properties": {}},
    )
    declaration = MCPToolDeclarationDTO(function=fn_def)
    return DummyTestTool(tool_id=tool_id, declaration=declaration)


def test_tool_dispatcher_init_and_get_declarations() -> None:
    tool_a = _create_dummy_tool("tool_a")
    tool_b = _create_dummy_tool("tool_b")
    dispatcher = ToolDispatcher([tool_a, tool_b])

    # Should only return declarations for allowed tools that exist
    decls = dispatcher.get_declarations(["tool_a", "non_existent"])
    assert len(decls) == 1
    assert decls[0].function.name == "tool_a"

    # All allowed
    all_decls = dispatcher.get_declarations(["tool_a", "tool_b"])
    assert len(all_decls) == 2


@pytest.mark.asyncio
async def test_tool_dispatcher_execute_success() -> None:
    tool_a = _create_dummy_tool("tool_a")
    dispatcher = ToolDispatcher([tool_a])

    trace = await dispatcher.execute_tool("tool_a", query="search terms", extra_flag=True)
    assert trace.tool_id == "tool_a"
    assert trace.query == "search terms"
    assert tool_a.last_kwargs.get("extra_flag") is True


@pytest.mark.asyncio
async def test_tool_dispatcher_execute_not_found_raises() -> None:
    dispatcher = ToolDispatcher([])

    with pytest.raises(AppException) as exc_info:
        await dispatcher.execute_tool("missing_tool")

    assert exc_info.value.status_code == 400
    assert "missing_tool" in str(exc_info.value.message)

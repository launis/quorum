"""Unit tests for ToolDispatcher in MCP services."""

from __future__ import annotations

from typing import Any

import pytest
from pydantic import JsonValue

from backend_v2.exceptions import AppException
from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.domain.tools import BaseSearchTool, BaseTool
from backend_v2.models.dtos.mcp import MCPFunctionDefinitionDTO, MCPToolDeclarationDTO
from backend_v2.models.enums import ToolCapability
from backend_v2.services.mcp.dispatcher import ToolDispatcher


class DummySearchTestTool(BaseSearchTool):
    """Mock search tool implementing BaseSearchTool."""

    def __init__(self, tool_id: str, declaration: MCPToolDeclarationDTO) -> None:
        self._tool_id = tool_id
        self._declaration = declaration

    @property
    def tool_id(self) -> str:
        return self._tool_id

    @property
    def declaration(self) -> MCPToolDeclarationDTO:
        return self._declaration

    async def execute(self, **kwargs: JsonValue) -> MCPAuditTrace:
        return MCPAuditTrace(
            tool_id=self._tool_id,
            step_name="step_test",
            query=str(kwargs.get("query", "")),
            response_summary="dummy search output",
        )


class DummyReaderTestTool(BaseTool):
    """Mock reader tool implementing DOCUMENT_READER capability."""

    def __init__(self, tool_id: str, declaration: MCPToolDeclarationDTO) -> None:
        self._tool_id = tool_id
        self._declaration = declaration

    @property
    def tool_id(self) -> str:
        return self._tool_id

    @property
    def capability(self) -> ToolCapability:
        return ToolCapability.DOCUMENT_READER

    @property
    def declaration(self) -> MCPToolDeclarationDTO:
        return self._declaration

    async def execute(self, **kwargs: JsonValue) -> MCPAuditTrace:
        return MCPAuditTrace(
            tool_id=self._tool_id,
            step_name="step_test",
            response_summary="dummy reader output",
        )


class DummyTestTool(BaseTool):
    """Concrete mock tool for testing ToolDispatcher."""

    def __init__(self, tool_id: str, declaration: MCPToolDeclarationDTO) -> None:
        self._tool_id = tool_id
        self._declaration = declaration
        self.last_kwargs: dict[str, JsonValue] = {}

    @property
    def tool_id(self) -> str:
        return self._tool_id

    @property
    def capability(self) -> ToolCapability:
        return ToolCapability.SEARCH

    @property
    def declaration(self) -> MCPToolDeclarationDTO:
        return self._declaration

    async def execute(self, **kwargs: JsonValue) -> MCPAuditTrace:
        self.last_kwargs = kwargs
        query_val = "default_query"
        if "query" in kwargs:
            query_val = str(kwargs["query"])
        return MCPAuditTrace(
            tool_id=self._tool_id,
            step_name="step_test",
            query=query_val,
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
    assert tool_a.last_kwargs["extra_flag"] is True


@pytest.mark.asyncio
async def test_tool_dispatcher_execute_not_found_raises() -> None:
    dispatcher = ToolDispatcher([])

    with pytest.raises(AppException) as exc_info:
        await dispatcher.execute_tool("missing_tool")

    assert exc_info.value.status_code == 400
    assert "missing_tool" in str(exc_info.value.message)


@pytest.mark.asyncio
async def test_tool_dispatcher_execute_timeout_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    tool_a = _create_dummy_tool("timeout_tool")

    async def slow_execute(**kwargs: Any) -> MCPAuditTrace:
        raise TimeoutError("Simulated timeout")

    monkeypatch.setattr(tool_a, "execute", slow_execute)

    dispatcher = ToolDispatcher([tool_a])
    with pytest.raises(AppException) as exc_info:
        await dispatcher.execute_tool("timeout_tool")

    assert exc_info.value.status_code == 504
    assert "timed out" in str(exc_info.value.message)


@pytest.mark.asyncio
async def test_tool_dispatcher_execute_generic_exception_recorded(monkeypatch: pytest.MonkeyPatch) -> None:
    tool_a = _create_dummy_tool("error_tool")

    async def failing_execute(**kwargs: Any) -> MCPAuditTrace:
        raise ValueError("Simulated tool crash")

    monkeypatch.setattr(tool_a, "execute", failing_execute)

    dispatcher = ToolDispatcher([tool_a])
    with pytest.raises(ValueError, match="Simulated tool crash"):
        await dispatcher.execute_tool("error_tool")


def test_tool_dispatcher_get_tools_by_capability() -> None:
    """Verify get_tools_by_capability filters and preserves order of allowed_tools."""
    search_tool = DummySearchTestTool("search_1", _create_dummy_tool("search_1").declaration)
    reader_tool = DummyReaderTestTool("reader_1", _create_dummy_tool("reader_1").declaration)
    dispatcher = ToolDispatcher([search_tool, reader_tool])

    # Search capability matching
    search_tools = dispatcher.get_tools_by_capability(["search_1", "reader_1"], ToolCapability.SEARCH)
    assert len(search_tools) == 1
    assert search_tools[0].tool_id == "search_1"

    # Reader capability matching
    reader_tools = dispatcher.get_tools_by_capability(["search_1", "reader_1"], ToolCapability.DOCUMENT_READER)
    assert len(reader_tools) == 1
    assert reader_tools[0].tool_id == "reader_1"

    # Unknown capability / empty match
    action_tools = dispatcher.get_tools_by_capability(["search_1", "reader_1"], ToolCapability.ACTION)
    assert action_tools == []

    # Filtered by allowed_tools
    filtered = dispatcher.get_tools_by_capability(["reader_1"], ToolCapability.SEARCH)
    assert filtered == []


def test_tool_dispatcher_resolve_primary_search_tool_precedence() -> None:
    """Verify resolve_primary_search_tool preserves step author precedence hierarchy."""
    search_a = DummySearchTestTool("search_a", _create_dummy_tool("search_a").declaration)
    search_b = DummySearchTestTool("search_b", _create_dummy_tool("search_b").declaration)
    reader = DummyReaderTestTool("reader_1", _create_dummy_tool("reader_1").declaration)
    dispatcher = ToolDispatcher([search_a, search_b, reader])

    # Precedence: search_a first
    primary = dispatcher.resolve_primary_search_tool(["search_a", "search_b"])
    assert primary is not None
    assert primary.tool_id == "search_a"

    # Precedence: search_b first
    primary_b = dispatcher.resolve_primary_search_tool(["search_b", "search_a"])
    assert primary_b is not None
    assert primary_b.tool_id == "search_b"

    # Reader followed by search
    primary_after_reader = dispatcher.resolve_primary_search_tool(["reader_1", "search_b"])
    assert primary_after_reader is not None
    assert primary_after_reader.tool_id == "search_b"

    # Non-existent tool skipped
    primary_skip_unknown = dispatcher.resolve_primary_search_tool(["non_existent", "search_a"])
    assert primary_skip_unknown is not None
    assert primary_skip_unknown.tool_id == "search_a"

    # None resolved when no search tools allowed
    assert dispatcher.resolve_primary_search_tool(["reader_1"]) is None
    assert dispatcher.resolve_primary_search_tool([]) is None


def test_tool_dispatcher_has_capability() -> None:
    """Verify has_capability returns True only when capability is present in allowed tools."""
    search_tool = DummySearchTestTool("search_1", _create_dummy_tool("search_1").declaration)
    dispatcher = ToolDispatcher([search_tool])

    assert dispatcher.has_capability(["search_1"], ToolCapability.SEARCH) is True
    assert dispatcher.has_capability(["search_1"], ToolCapability.DOCUMENT_READER) is False
    assert dispatcher.has_capability([], ToolCapability.SEARCH) is False


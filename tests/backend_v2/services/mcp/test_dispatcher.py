from typing import Any

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.domain.tools import BaseTool
from backend_v2.models.v2_core import MCPAuditTrace
from backend_v2.services.mcp.dispatcher import ToolDispatcher


class DummyToolA(BaseTool):
    @property
    def tool_id(self) -> str:
        return "mcp_dummy_a"

    @property
    def declaration(self) -> dict[str, Any]:
        return {"name": "dummy_a", "description": "Dummy tool A"}

    async def execute(self, **kwargs: Any) -> MCPAuditTrace:
        return MCPAuditTrace(id="trace_a", tool_id="mcp_dummy_a", step_name="test_step", query="dummy a")


class DummyToolB(BaseTool):
    @property
    def tool_id(self) -> str:
        return "mcp_dummy_b"

    @property
    def declaration(self) -> dict[str, Any]:
        return {"name": "dummy_b", "description": "Dummy tool B"}

    async def execute(self, **kwargs: Any) -> MCPAuditTrace:
        return MCPAuditTrace(id="trace_b", tool_id="mcp_dummy_b", step_name="test_step", query="dummy b")


def test_dispatcher_initialization() -> None:
    dispatcher = ToolDispatcher(tools=[DummyToolA(), DummyToolB()])
    assert "mcp_dummy_a" in dispatcher._registry
    assert "mcp_dummy_b" in dispatcher._registry


def test_get_declarations() -> None:
    dispatcher = ToolDispatcher(tools=[DummyToolA(), DummyToolB()])
    decls = dispatcher.get_declarations(["mcp_dummy_a"])
    assert len(decls) == 1
    assert decls[0]["name"] == "dummy_a"

    # Testing fallback behavior or ignore if allowed tool isn't registered
    decls2 = dispatcher.get_declarations(["mcp_dummy_a", "mcp_unknown"])
    assert len(decls2) == 1


@pytest.mark.asyncio
async def test_execute_tool_success() -> None:
    dispatcher = ToolDispatcher(tools=[DummyToolA()])
    trace = await dispatcher.execute_tool("mcp_dummy_a", arg="val")
    assert trace.id == "trace_a"


@pytest.mark.asyncio
async def test_execute_tool_not_found() -> None:
    dispatcher = ToolDispatcher(tools=[DummyToolA()])
    with pytest.raises(AppException) as exc_info:
        await dispatcher.execute_tool("mcp_unknown", arg="val")
    
    assert exc_info.value.status_code == 400
    assert "not found" in exc_info.value.message.lower()

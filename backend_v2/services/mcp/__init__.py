"""MCP Module Initialization."""

from backend_v2.services.mcp.dispatcher import ToolDispatcher
from backend_v2.services.mcp.mcp_tool_loop import DISPATCHER, execute_tool_loop

__all__ = ["DISPATCHER", "ToolDispatcher", "execute_tool_loop"]

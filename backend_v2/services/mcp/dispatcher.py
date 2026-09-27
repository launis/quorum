"""MCP Tool Dispatcher Module.

Provides registry and execution dispatching for MCP tools with OpenTelemetry instrumentation and timeouts.
"""

import asyncio
from typing import Any

import opentelemetry.trace as trace

from backend_v2.core.telemetry import get_tracer
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.domain.tools import BaseTool
from backend_v2.models.dtos.mcp import MCPToolDeclarationDTO
from backend_v2.settings import get_settings


class ToolDispatcher:
    """Registry and dispatcher for MCP tools."""

    def __init__(self, tools: list[BaseTool]) -> None:
        """Initialize the dispatcher with a list of tools.

        Args:
            tools: List of tool instances to register.
        """
        self._registry: dict[str, BaseTool] = {tool.tool_id: tool for tool in tools}

    def get_declarations(self, allowed_tools: list[str]) -> list[MCPToolDeclarationDTO]:
        """Get the OpenAI schema declarations for the specified tools.

        Args:
            allowed_tools: List of tool IDs to include.

        Returns:
            List of tool declaration dictionaries.
        """
        declarations = []
        for tool_id in allowed_tools:
            if tool_id in self._registry:
                declarations.append(self._registry[tool_id].declaration)
        return declarations

    async def execute_tool(self, tool_id: str, **kwargs: Any) -> MCPAuditTrace:
        """Execute a tool by ID.

        Args:
            tool_id: The ID of the tool to execute.
            **kwargs: Arguments to pass to the tool.

        Returns:
            MCPAuditTrace: The execution trace.

        Raises:
            AppException: If the tool is not found, or execution times out.
        """
        if tool_id not in self._registry:
            raise AppException(
                message=f"Tool '{tool_id}' not found in registry.",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "tool_id": tool_id},
            )

        tool = self._registry[tool_id]
        timeout_sec = get_settings().mcp_default_timeout_seconds

        tracer = get_tracer(__name__)
        with tracer.start_as_current_span("mcp.tool_call") as span:
            span.set_attribute("mcp.tool_id", tool_id)
            try:
                async with asyncio.timeout(timeout_sec):
                    return await tool.execute(**kwargs)
            except TimeoutError as te:
                span.record_exception(te)
                span.set_status(trace.StatusCode.ERROR, f"MCP tool execution timed out after {timeout_sec}s")
                raise AppException(
                    message=f"MCP tool '{tool_id}' timed out after {timeout_sec} seconds.",
                    status_code=504,
                    details={"error_code": ErrorCodes.SERVICE_UNAVAILABLE.value, "tool_id": tool_id},
                ) from te
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.StatusCode.ERROR, str(e))
                raise

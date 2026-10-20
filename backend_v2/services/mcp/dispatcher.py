"""MCP Tool Dispatcher Module.

Provides registry and execution dispatching for MCP tools with OpenTelemetry instrumentation and timeouts.
"""

import asyncio
from typing import Any

import opentelemetry.trace as trace

from backend_v2.core.telemetry import get_tracer
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.domain.tools import BaseSearchTool, BaseTool
from backend_v2.models.dtos.mcp import MCPToolDeclarationDTO
from backend_v2.models.enums import ToolCapability
from backend_v2.settings import get_settings


class ToolDispatcher:
    """Registry and dispatcher for MCP tools."""

    def __init__(self, tools: list[BaseTool]) -> None:
        """Initialize the dispatcher with a list of tools.

        Args:
            tools: List of tool instances to register.
        """
        self._registry: dict[str, BaseTool] = {tool.tool_id: tool for tool in tools}
        self._capability_index: dict[ToolCapability, list[BaseTool]] = {cap: [] for cap in ToolCapability}
        for tool in tools:
            self._capability_index[tool.capability].append(tool)

    def get_declarations(self, allowed_tools: list[str]) -> list[MCPToolDeclarationDTO]:
        """Get the OpenAI schema declarations for the specified tools.

        Args:
            allowed_tools: List of tool IDs to include.

        Returns:
            List of tool declarations conforming to MCPToolDeclarationDTO.
        """
        declarations: list[MCPToolDeclarationDTO] = []
        for tool_id in allowed_tools:
            if tool_id in self._registry:
                declarations.append(self._registry[tool_id].declaration)
        return declarations

    def get_tools_by_capability(self, allowed_tools: list[str], capability: ToolCapability) -> list[BaseTool]:
        """Return allowed tools implementing the specified capability preserving allowed_tools order.

        Args:
            allowed_tools: List of tool IDs to filter.
            capability: Operational capability category to match.

        Returns:
            List of matching tool instances.
        """
        tools_with_cap = self._capability_index[capability]
        if not tools_with_cap:
            return []
        return [
            self._registry[t_id]
            for t_id in allowed_tools
            if t_id in self._registry and self._registry[t_id].capability == capability
        ]

    def resolve_primary_search_tool(self, allowed_tools: list[str]) -> BaseSearchTool | None:
        """Resolve primary search tool preserving explicit step configuration priority.

        The order of tools in allowed_tools defines the precedence hierarchy.
        Returns the first tool matching ToolCapability.SEARCH, or None if no search tool is allowed.

        Args:
            allowed_tools: Ordered list of allowed tool IDs.

        Returns:
            First matching BaseSearchTool instance, or None.
        """
        for tool_id in allowed_tools:
            if tool_id not in self._registry:
                continue
            tool = self._registry[tool_id]
            if tool.capability == ToolCapability.SEARCH and isinstance(tool, BaseSearchTool):
                return tool
        return None

    def has_capability(self, allowed_tools: list[str], capability: ToolCapability) -> bool:
        """Check if any allowed tool implements the given capability.

        Args:
            allowed_tools: List of tool IDs to check.
            capability: Operational capability to test.

        Returns:
            True if at least one allowed tool implements capability.
        """
        return len(self.get_tools_by_capability(allowed_tools, capability)) > 0

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

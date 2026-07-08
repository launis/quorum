from typing import Any

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.tools import BaseTool
from backend_v2.models.v2_core import MCPAuditTrace


class ToolDispatcher:
    """Registry and dispatcher for MCP tools."""

    def __init__(self, tools: list[BaseTool]) -> None:
        """Initialize the dispatcher with a list of tools.

        Args:
            tools: List of tool instances to register.
        """
        self._registry: dict[str, BaseTool] = {tool.tool_id: tool for tool in tools}

    def get_declarations(self, allowed_tools: list[str]) -> list[dict[str, Any]]:
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
            AppException: If the tool is not found.
        """
        if tool_id not in self._registry:
            raise AppException(
                message=f"Tool '{tool_id}' not found in registry.",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "tool_id": tool_id},
            )

        tool = self._registry[tool_id]
        return await tool.execute(**kwargs)

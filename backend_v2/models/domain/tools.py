from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from backend_v2.models.domain.system_config import MCPAuditTrace

if TYPE_CHECKING:
    from backend_v2.models.dtos.mcp import MCPToolDeclarationDTO


class BaseTool(ABC):
    """Abstract interface for all MCP tools.

    Enforces the Single Responsibility Principle by decoupling tool execution
    from the main orchestrator loop.
    """

    @property
    @abstractmethod
    def tool_id(self) -> str:
        """The strictly defined unique identifier for the tool."""
        pass

    @property
    @abstractmethod
    def declaration(self) -> MCPToolDeclarationDTO | dict[str, Any]:
        """The tool declaration in OpenAI JSON schema format."""
        pass

    @abstractmethod
    async def execute(self, **kwargs: Any) -> MCPAuditTrace:
        """Execute the tool logic and return a standard audit trace.

        Returns:
            MCPAuditTrace: The standard execution trace for the orchestrator.
        """
        pass

"""Domain contracts and input DTOs for MCP tools."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Annotated, Any

from pydantic import BaseModel, ConfigDict, Field

from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.enums import ToolCapability

if TYPE_CHECKING:
    from backend_v2.models.dtos.mcp import MCPToolDeclarationDTO

__all__ = [
    "BaseSearchTool",
    "BaseTool",
    "StandardSearchInputDTO",
]


class StandardSearchInputDTO(BaseModel):
    """Standardized validated input payload for all search capability tools."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, arbitrary_types_allowed=True)

    query: Annotated[str, Field(min_length=1, description="Search query string")]
    step_name: Annotated[str, Field(description="Name of the calling step")] = "unknown_step"
    target_language: Annotated[str, Field(description="Target language code")] = "en"
    reasoning: Annotated[str, Field(description="Search rationale")] = ""
    claim_text: Annotated[str | None, Field(default=None, description="Verbatim claim being verified")] = None
    llm_client: Annotated[Any, Field(default=None, description="Optional LLM client for translation")] = None


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
    def capability(self) -> ToolCapability:
        """The operational capability implemented by this tool."""
        pass

    @property
    @abstractmethod
    def declaration(self) -> MCPToolDeclarationDTO:
        """The tool declaration in OpenAI JSON schema format."""
        pass

    @abstractmethod
    async def execute(self, **kwargs: Any) -> MCPAuditTrace:
        """Execute the tool logic and return a standard audit trace.

        Returns:
            MCPAuditTrace: The standard execution trace for the orchestrator.
        """
        pass


class BaseSearchTool(BaseTool):
    """Abstract base class for all search capability MCP tools."""

    @property
    def capability(self) -> ToolCapability:
        """Return SEARCH capability."""
        return ToolCapability.SEARCH

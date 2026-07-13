from typing import Any

from backend_v2.models.domain.tools import BaseTool
from backend_v2.models.v2_core import MCPAuditTrace


class DummyTool(BaseTool):
    @property
    def tool_id(self) -> str:
        return "mcp_dummy"

    @property
    def declaration(self) -> dict[str, Any]:
        return {"name": "dummy"}

    async def execute(self, **kwargs: Any) -> MCPAuditTrace:
        return MCPAuditTrace(id="trace123", query="test")


def test_base_tool_instantiation() -> None:
    tool = DummyTool()
    assert tool.tool_id == "mcp_dummy"
    assert tool.declaration == {"name": "dummy"}

from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.exceptions import AppException
from backend_v2.services.mcp.tools.tavily import TavilyTool


@pytest.mark.asyncio
async def test_tavily_tool_execute_success() -> None:
    tool = TavilyTool()

    mock_result = AsyncMock()
    mock_result.answer = "Tavily summary"
    mock_result.source_urls = ["https://example.com"]

    with patch("backend_v2.services.mcp.tools.tavily.tavily_search", new_callable=AsyncMock) as mock_tavily:
        mock_tavily.return_value = mock_result

        trace = await tool.execute(query="test query", step_name="test_step")
        assert trace.tool_id == "mcp_tavily_search"
        assert trace.response_summary == "Tavily summary"
        assert trace.source_urls == ["https://example.com"]


@pytest.mark.asyncio
async def test_tavily_tool_execute_failure() -> None:
    tool = TavilyTool()

    with patch("backend_v2.services.mcp.tools.tavily.tavily_search", new_callable=AsyncMock) as mock_tavily:
        mock_tavily.side_effect = Exception("API Error")

        with pytest.raises(AppException) as exc_info:
            await tool.execute(query="test query", step_name="test_step")

        assert exc_info.value.status_code == 502

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel

from backend.hooks.search import execute_google_search
from backend.models.domain.analyst import AnalystOutput, Hypothesis


class DummyState(BaseModel):
    context_variables: dict

@pytest.mark.asyncio
async def test_search_hook_data_hygiene():
    """Test that SearchHook isolates data and does NOT inject into AnalystOutput.rag_evidence."""
    # Setup initial AnalystOutput with some existing evidence
    initial_analyst = AnalystOutput(
        thought_process="Thinking...",
        conclusion="Conclusion.",
        confidence_score=0.9,
        hypotheses=[Hypothesis(id="h1", claim_text="Test", search_query="test query", evidence_found=False, quotes=[])],
        rag_evidence=["Existing Evidence 1"]
    )

    # Setup state
    state = DummyState(context_variables={"step_analyst": initial_analyst.model_dump()})
    object.__setattr__(state, "get_context", MagicMock(return_value=initial_analyst))
    object.__setattr__(state, "model_copy", MagicMock(side_effect=lambda update: DummyState(context_variables=update["context_variables"])))

    # Mock the search tool and LLM client
    mock_tool_instance = MagicMock()

    # Create fake search result item with snippet
    class FakeResult:
        title="Test Title"
        link="http://test.com"
        snippet="This is a massive summary of text from google."
    mock_tool_instance.search.return_value = [FakeResult()]

    mock_client = AsyncMock()
    mock_client._config.model_name = "vertex_ai/gemini-2.5-flash"
    mock_client._config.supports_grounding = True

    with patch('backend.llm.client.LLMClient.from_strategy', return_value=mock_client), \
         patch('backend.hooks.search.VertexAISearchTool', return_value=mock_tool_instance), \
         patch('backend.hooks.search.inflate', return_value=MagicMock(language="en")):

        # Execute hook
        new_state = await execute_google_search(state)

        # 1. Verify search_result was created in context
        assert "search_result" in new_state.context_variables
        search_res = new_state.context_variables["search_result"]
        assert len(search_res.results) == 1
        assert search_res.results[0].snippet == "This is a massive summary of text from google."

        # 2. Verify AnalystOutput was NOT flooded with the search snippet
        # (It should still ONLY have its original 1 item)
        # Note: step_analyst is now unchanged in the updated code, so it might not even be in the copy update,
        # or it might be in context_variables exactly as before. Let's just check the state dictionary.

        # In the refactored code, we removed `new_context["step_analyst"] = updated_analyst` entirely
        assert "step_analyst" not in new_state.context_variables or new_state.context_variables["step_analyst"] == initial_analyst.model_dump()

from unittest.mock import MagicMock, patch

import pytest

from backend.exceptions import AppException, ConfigurationError, ErrorCodes
from backend.hooks.search import execute_google_search
from backend.hooks.search_client import SearchResultItem as ClientSearchResultItem
from backend.models.domain.analyst import AnalystOutput, Hypothesis, SearchResult
from backend.models.state import WorkflowState


@pytest.fixture
def mock_repo():
    class MockDriver:
        async def get(self, table, key):
            return {
                "models": {
                    "google": {
                        "deep": {
                            "model_name": "vertex_ai/gemini-2.5-pro",
                            "temperature": 0.7,
                            "tpm_limit": 500000,
                            "rpm_limit": 3000,
                            "supports_grounding": True
                        },
                        "SearchHook": {
                            "model_name": "vertex_ai/gemini-2.5-pro",
                            "temperature": 0.0,
                            "tpm_limit": 500000,
                            "rpm_limit": 3000,
                            "supports_grounding": True,
                            "allowed_tools": []
                        }
                    }
                }
            }
    class MockRepo:
        driver = MockDriver()
    return MockRepo()

@pytest.fixture
def mock_state():
    return WorkflowState(workflow_id="test_wf", context_variables={})


@pytest.mark.asyncio
async def test_missing_step_analyst(mock_state, mock_repo):
    """Should return state unchanged if step_analyst is missing."""
    new_state = await execute_google_search(mock_state, mock_repo)
    assert new_state == mock_state
    assert "search_result" not in new_state.context_variables


@pytest.mark.asyncio
async def test_invalid_step_analyst_schema(mock_state, mock_repo):
    """Fail Fast: Should raise AppException if step_analyst data is invalid."""
    mock_state = mock_state.model_copy(update={"context_variables": {"step_analyst": {"invalid": "data"}}})

    with pytest.raises(AppException) as exc:
        await execute_google_search(mock_state, mock_repo)

    assert exc.value.error_code == ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED


@pytest.mark.asyncio
async def test_no_hypotheses(mock_state, mock_repo):
    """Should skip search if no valid hypotheses."""
    analyst_output = AnalystOutput(
        hypotheses=[Hypothesis(id="1", claim_text="dummy claim", evidence_found=False, search_query="foo", quotes=[])],
        rag_evidence=[],
        thought_process="Thinking...",
        conclusion="Conclusion",
        confidence_score=0.9,
    )
    mock_state = mock_state.model_copy(update={"context_variables": {"step_analyst": analyst_output}})

    new_state = await execute_google_search(mock_state, mock_repo)
    assert new_state.context_variables.get("search_result") is None


@pytest.mark.asyncio
async def test_config_error_fail_fast(mock_state, mock_repo):
    """Fail Fast: Should raise ConfigurationError if tool init fails, BUT only if queries exist."""
    analyst_output = AnalystOutput(
        hypotheses=[Hypothesis(id="1", claim_text="claim", evidence_found=False, search_query="test query", quotes=[])],
        rag_evidence=[],
        thought_process="Thinking...",
        conclusion="Conclusion",
        confidence_score=0.9,
    )
    mock_state = mock_state.model_copy(update={"context_variables": {"step_analyst": analyst_output}})

    # Patch VertexAISearchTool to raise ConfigurationError
    with patch("backend.hooks.search.VertexAISearchTool", side_effect=ConfigurationError("Missing keys")):
        with pytest.raises(ConfigurationError):
            await execute_google_search(mock_state, mock_repo)


@pytest.mark.asyncio
async def test_execution_success(mock_state, mock_repo):
    """Should populate search_result on success."""
    analyst_output = AnalystOutput(
        hypotheses=[Hypothesis(id="1", claim_text="claim", evidence_found=False, search_query="test query", quotes=[])],
        rag_evidence=[],
        thought_process="Thinking...",
        conclusion="Conclusion",
        confidence_score=0.9,
    )
    mock_state = mock_state.model_copy(update={"context_variables": {"step_analyst": analyst_output}})

    mock_tool_instance = MagicMock()
    # Mock search return
    mock_tool_instance.search.return_value = [
        ClientSearchResultItem(title="Title", link="http://link", snippet="Snippet", query="test query")
    ]

    with patch("backend.hooks.search.VertexAISearchTool", return_value=mock_tool_instance):
        new_state = await execute_google_search(mock_state, mock_repo)

        assert "search_result" in new_state.context_variables
        result = new_state.context_variables["search_result"]
        assert isinstance(result, SearchResult)
        assert len(result.results) == 1
        assert result.results[0].title == "Title"


@pytest.mark.asyncio
async def test_execution_failure_fail_fast(mock_state, mock_repo):
    """Fail Fast: Should raise AppException(SEARCH_EXECUTION_FAILED) on error."""
    analyst_output = AnalystOutput(
        hypotheses=[Hypothesis(id="1", claim_text="claim", evidence_found=False, search_query="test query", quotes=[])],
        rag_evidence=[],
        thought_process="Thinking...",
        conclusion="Conclusion",
        confidence_score=0.9,
    )
    mock_state = mock_state.model_copy(update={"context_variables": {"step_analyst": analyst_output}})

    mock_tool_instance = MagicMock()
    mock_tool_instance.search.side_effect = Exception("API Down")

    with patch("backend.hooks.search.VertexAISearchTool", return_value=mock_tool_instance):
        with pytest.raises(AppException) as exc:
            await execute_google_search(mock_state, mock_repo)

        assert exc.value.error_code == ErrorCodes.SEARCH_EXECUTION_FAILED


@pytest.mark.asyncio
async def test_language_context(mock_state, mock_repo):
    """Verify language is passed from state to tool."""
    analyst_output = AnalystOutput(
        hypotheses=[Hypothesis(id="1", claim_text="claim", evidence_found=False, search_query="test query", quotes=[])],
        rag_evidence=[],
        thought_process="Thinking...",
        conclusion="Conclusion",
        confidence_score=0.9,
    )
    mock_state = mock_state.model_copy(
        update={
            "context_variables": {
                "step_analyst": analyst_output,
                "inputs": {
                    "history_text": "History",
                    "product_text": "Product",
                    "reflection_text": "Reflection",
                    "language": "fi",
                },
            }
        }
    )

    mock_tool_instance = MagicMock()
    mock_tool_instance.search.return_value = []

    with patch("backend.hooks.search.VertexAISearchTool", return_value=mock_tool_instance):
        await execute_google_search(mock_state, mock_repo)

        # Verify tool.search called with language='fi'
        mock_tool_instance.search.assert_called_with(["test query"], limit=3, language="fi")

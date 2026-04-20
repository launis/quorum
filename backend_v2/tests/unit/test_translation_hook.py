from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.core.hook_registry import HookDependencies, HookState
from backend_v2.hooks.translation_hook import translation_hook


@pytest.fixture
def mock_repository() -> AsyncMock:
    return AsyncMock()


@pytest.mark.asyncio
async def test_translation_hook_skips_when_target_en_or_missing(mock_repository: AsyncMock) -> None:
    """Ensure it skips translation cleanly when language is 'en' or missing."""
    state = HookState(
        execution_id="sub-123",
        workflow_id="wf-123",
        step_id="step-123",
        task_blueprint="bp-123",
        metadata={},
        global_context_vars={},
        inputs={"language": "en", "data": "value"},
    )
    deps = HookDependencies(repository=mock_repository)

    res = await translation_hook(state, deps)  # type: ignore[misc]

    assert res.success is True
    assert res.state_delta == {}

    # Missing language
    state2 = HookState(
        execution_id="sub-123",
        workflow_id="wf-123",
        metadata={},
        global_context_vars={},
        inputs={"data": "value"},
    )
    res2 = await translation_hook(state2, deps)  # type: ignore[misc]
    assert res2.success is True
    assert res2.state_delta == {}


@pytest.mark.asyncio
@patch("backend_v2.hooks.translation_hook.LLMClient.from_strategy")
async def test_translation_hook_role_segregation_and_success(
    mock_from_strategy: AsyncMock, mock_repository: AsyncMock
) -> None:
    """Ensures that the TranslationHook STRICTLY separates System and User roles."""
    state = HookState(
        execution_id="sub-123",
        workflow_id="wf-123",
        step_id="step-123",
        task_blueprint="bp-123",
        metadata={},
        global_context_vars={},
        inputs={"language": "fi", "title": "Example Title", "_private": "hidden"},
    )
    deps = HookDependencies(repository=mock_repository)

    # Setup Mock
    mock_client = AsyncMock()
    # Mock LLM response string (should be valid JSON as per prompt)
    mock_llm_response = '{"title": "Esimerkki Otsikko"}'
    mock_client.run_chat.return_value = mock_llm_response
    mock_from_strategy.return_value = mock_client

    res = await translation_hook(state, deps)  # type: ignore[misc]

    assert res.success is True
    assert res.state_delta["title"] == "Esimerkki Otsikko"
    assert res.state_delta["_private"] == "hidden"  # Preserved field

    # Assert Role Segregation
    mock_from_strategy.assert_called_once_with("fast", repository=mock_repository)
    mock_client.run_chat.assert_called_once()

    call_kwargs = mock_client.run_chat.call_args.kwargs
    messages = call_kwargs["messages"]

    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert "SÄÄNTÖ: Toimit automaattisena JSON-kääntäjänä." in messages[0]["content"]
    assert "fi" in messages[0]["content"]  # Embedded target language

    assert messages[1]["role"] == "user"
    assert "Lähde JSON" in messages[1]["content"]
    assert "Example Title" in messages[1]["content"]

from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.database.repository import AbstractWorkflowRepository
from backend_v2.hooks.synthesis import (
    HookDependencies,
    HookState,
    SynthesisOutputDTO,
    SynthesisSectionDTO,
    text_consolidation_hook,
)


@pytest.fixture
def mock_repository() -> AbstractWorkflowRepository:
    return AsyncMock(spec=AbstractWorkflowRepository)


@pytest.fixture
def mock_state() -> HookState:
    return HookState(
        execution_id="exe_123",
        workflow_id="wf_123",
        step_id="step_123",
        inputs={"some_step_id": {"reasoning_trace": {"conclusion": "This is a conclusion"}}},
        global_context_vars={"profile_id": "prf_456", "language": "fi"},
        metadata={},
    )


@pytest.fixture
def mock_deps(mock_repository: AbstractWorkflowRepository) -> HookDependencies:
    return HookDependencies(repository=mock_repository)


@pytest.mark.asyncio
async def test_text_consolidation_hook_success(mock_state: HookState, mock_deps: HookDependencies) -> None:
    # Set up active profile dict
    active_profile = {
        "id": "prf_456",
        "layouts": [
            {
                "presetView": "1d_metrics",
                "title": {"fi": "Otsikko 1"},
                "synthesis": {"preamble_text": {"fi": "Tee vitsi"}},
            }
        ]
    }
    # Provide the mocked profile from SSOT
    mock_deps.repository.get_all_output_profiles = AsyncMock(return_value=[active_profile])  # type: ignore
    
    # Mock missing execution and workflow queries
    mock_deps.repository.get_workflow_by_id = AsyncMock(return_value={"default_profile_id": "prf_456"})  # type: ignore
    mock_deps.repository.get_execution = AsyncMock(return_value={})  # type: ignore

    # Provide mocked prompt blocks
    mock_deps.repository.get_all_prompt_blocks = AsyncMock(return_value=[])  # type: ignore

    # Mock the LLM Client
    with patch("backend_v2.hooks.synthesis.LLMClient") as MockClient:
        mock_instance = AsyncMock()
        MockClient.from_strategy = AsyncMock(return_value=mock_instance)
        
        # Mock structured response
        mock_instance.run_structured_task.return_value = (
            SynthesisOutputDTO(
                synthesized_markdown="Global markdown.",
                cited_sources=["[1] Source A"],
                section_syntheses=[
                    SynthesisSectionDTO(
                        layout_id="layout_0_1d_metrics",
                        synthesized_markdown="Section markdown."
                    )
                ]
            ),
            {"prompt_tokens": 100, "completion_tokens": 50}
        )

        result = await text_consolidation_hook(mock_state, mock_deps)

        assert result.success is True
        assert result.state_delta is not None
        assert result.state_delta["synthesized_markdown"] == "Global markdown."
        assert result.state_delta["section_syntheses"] == {"layout_0_1d_metrics": "Section markdown."}

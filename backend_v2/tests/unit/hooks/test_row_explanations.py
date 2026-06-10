from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.core.hook_registry import HookDependencies, HookState
from backend_v2.hooks.synthesis import text_consolidation_hook
from backend_v2.models.dtos.output_profile import OutputProfileResponseDTO
from backend_v2.models.state import StepOutputDTO
from backend_v2.models.v2_core import I18nText, SynthesisConfigDTO


@pytest.mark.asyncio
@pytest.mark.skip("Legacy architecture obsolete")
async def test_synthesis_row_explanations_with_atom_quotes() -> None:
    """TDD Repro: Ensure SynthesisHook uses atom_quotes instead of empty justifications."""
    # Mock LLM Client
    mock_client = AsyncMock()
    # Mock the LLM returning a valid MatrixExplanationsResult
    from backend_v2.models.dtos.synthesis import MatrixExplanationsResult, SynthesisRowExplanationDTO

    mock_res = MatrixExplanationsResult(
        explanations=[
            SynthesisRowExplanationDTO(
                matrix_id="blk_matrix1", row_explanation="The user successfully asked a question."
            )
        ]
    )
    from backend_v2.models.domain.usage import TokenUsage

    mock_usage = TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15)

    # Provide the mock execution result
    mock_executor = AsyncMock()
    mock_executor.execute_structured_task.return_value = (mock_res, mock_usage)

    # 1. Provide the atom_quotes in the state snapshot
    # We provide the DTOs inside the inputs dict
    available_dtos = [
        # The quotes block injected by scoring hook
        StepOutputDTO(
            step_id="step_score",
            block_id="atom_quotes",
            data_type="unknown",
            payload={"blk_matrix1": ["User: How does this work?"]},
        ),
        # The matrix score payload
        StepOutputDTO(
            step_id="step_score",
            block_id="blk_matrix1",
            data_type="unknown",
            payload={"normalized_score": 100.0, "justification": ""},  # In V2, justification is empty
        ),
    ]

    mock_state = HookState(
        execution_id="test_exec",
        workflow_id="test_wf",
        global_context_vars={},
        inputs={"steps": [dto.model_dump() for dto in available_dtos]},
        metadata={"token_usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}},
    )

    # Active profile expects synthesis
    active_profile = OutputProfileResponseDTO(
        id="prof_1",
        slug="prof",
        workflow_id="wf_1",
        name=I18nText(translations={"fi": "Testi", "en": "Test"}, default_locale="en"),
        synthesis=SynthesisConfigDTO(system_prompt="Test"),
        layouts=[],
    )

    mock_comp_repo = AsyncMock()
    mock_comp_repo.get_output_profile_by_id.return_value = active_profile.model_dump()

    mock_deps = HookDependencies(
        exec_repo=AsyncMock(),
        workflow_repo=AsyncMock(),
        comp_repo=mock_comp_repo,
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=AsyncMock(),
    )

    with (
        patch("backend_v2.hooks.synthesis.LLMTaskExecutor", return_value=mock_executor),
        patch("backend_v2.hooks.synthesis.LLMClient.from_strategy", return_value=mock_client),
    ):
        result = await text_consolidation_hook(mock_state, mock_deps)  # type: ignore

    # The hook should have called the LLM with the quotes, and returned the explanation
    assert result.success is True
    assert "blk_matrix1" in result.state_delta["row_explanations"]
    assert result.state_delta["row_explanations"]["blk_matrix1"] == "The user successfully asked a question."

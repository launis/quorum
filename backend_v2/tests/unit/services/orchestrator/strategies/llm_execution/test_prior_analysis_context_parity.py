"""Regression tests for prior_analysis and step dependency context compilation parity.

Ensures that ContextBuilder.build() produces canonical $steps. mappings compatible with
PromptCompiler.build_xml_context() prefix validation without triggering Unsupported source_path prefix.
"""

from unittest.mock import MagicMock

import pytest

from backend_v2.core.hook_registry import HookState
from backend_v2.models.domain.inputs import DomainInputValue
from backend_v2.models.dtos.hook_state import ExecutionInputsDTO, GlobalContextVarsDTO
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import StepOutputDTO
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler
from backend_v2.services.orchestrator.strategies.llm_execution.context_builder import ContextBuilder


def _make_hook_state(
    *,
    steps: list[StepOutputDTO] | None = None,
) -> HookState:
    """Helper to construct HookState with step dependencies."""
    dyn: dict[str, DomainInputValue] = {}
    if steps is not None:
        dyn["steps"] = steps
    return HookState(
        execution_id="exc_test",
        workflow_id="wf_test",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(
            raw_inputs={},
            dynamic_inputs=dyn,
        ),
    )


def test_context_builder_to_prompt_compiler_prior_analysis_pipeline(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that prior_analysis ($steps) passes through ContextBuilder to PromptCompiler without prefix error."""
    monkeypatch.setattr(
        "litellm.token_counter",
        lambda model, text: 10,
    )

    mock_context_router = MagicMock()
    mock_pruned = MagicMock()
    mock_pruned.model_dump.return_value = {"pruned": True}
    mock_context_router.route_and_prune.return_value = mock_pruned
    monkeypatch.setattr(
        "backend_v2.services.orchestrator.strategies.llm_execution.context_builder.ContextRouter",
        mock_context_router,
    )

    steps = [
        StepOutputDTO(
            step_id="step_prev",
            block_id="blk_prev",
            data_type="text",
            payload="Analysis summary from previous step",
        )
    ]
    state_data = _make_hook_state(steps=steps)

    input_mappings = {"prior_analysis": "$steps"}

    llm_context_data, new_input_mappings = ContextBuilder.build(
        input_mappings=input_mappings,
        state_data=state_data,
        output_profile=None,
        schema_map={"step_prev": "TEXT", "blk_prev": "TEXT"},
    )

    compiler = PromptCompiler()
    xml = compiler.build_xml_context(
        input_mappings=new_input_mappings,
        state_data=llm_context_data,
        target_locale="en",
        expected_inputs=[],
    )

    assert '<matrix_input source_id="prior_analysis">' in xml
    assert "<ai_draft_context>" in xml
    assert "Analysis summary from previous step" in xml


def test_context_builder_to_prompt_compiler_specific_step_pipeline(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that specific step dependency ($steps.step_prev) passes without prefix error."""
    monkeypatch.setattr(
        "litellm.token_counter",
        lambda model, text: 10,
    )

    steps = [
        StepOutputDTO(
            step_id="step_prev",
            block_id="blk_prev",
            data_type="text",
            payload="Specific step output",
        )
    ]
    state_data = _make_hook_state(steps=steps)

    input_mappings = {"results": "$steps.step_prev"}

    llm_context_data, new_input_mappings = ContextBuilder.build(
        input_mappings=input_mappings,
        state_data=state_data,
        output_profile=None,
        schema_map={"step_prev": "TEXT", "blk_prev": "TEXT"},
    )

    compiler = PromptCompiler()
    xml = compiler.build_xml_context(
        input_mappings=new_input_mappings,
        state_data=llm_context_data,
        target_locale="en",
        expected_inputs=[],
    )

    assert '<matrix_input source_id="results">' in xml
    assert "<ai_draft_context>" in xml
    assert "Specific step output" in xml

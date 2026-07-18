from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.core.hook_registry import HookResult
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.v2_core import ExecutionStatus, I18nText, StepRule, Workflow
from backend_v2.services.orchestrator.dag_executor import DAGExecutor


@pytest.fixture
def mock_repo() -> Any:
    repo = AsyncMock()
    from backend_v2.models.enums import BlockDataType

    repo.get_all_prompt_blocks.return_value = [
        {
            "id": "blk_0123456789abcdef0123456789ab",
            "slug": "task_bp",
            "label": {"default_locale": "fi", "translations": {"fi": "Testi", "en": "Test"}},
            "description": {"default_locale": "fi", "translations": {"fi": "Kuvaus", "en": "Desc"}},
            "category_id": "system_rule",
            "type": BlockDataType.STRING,
            "allow_decimals": False,
            "output_extensions": [],
        },
        {
            "id": "blk_573802341db9d68c",
            "slug": "zero_trust_extraction_protocol",
            "category_id": "system_rule",
            "type": BlockDataType.STRING,
            "label": {"default_locale": "en", "translations": {"en": "Zero-Trust", "fi": "Zero-Trust"}},
            "description": {"default_locale": "en", "translations": {"en": "Zero-Trust", "fi": "Zero-Trust"}},
            "ai_description": "Strict extraction protocol.",
            "allow_decimals": False,
            "output_extensions": [],
        },
    ]
    repo.get_step.return_value = {
        "id": "step_1111111111111111",
        "slug": "task_bp",
        "name": {"default_locale": "fi", "translations": {"fi": "Vaihe", "en": "Step"}},
        "role_block_id": None,
        "extraction_protocol_block_id": "blk_573802341db9d68c",
        "criteria_block_ids": ["blk_0123456789abcdef0123456789ab"],
        "model_strategy": "fast",
        "pre_hooks": [],
    }
    repo.get_step_by_id.return_value = repo.get_step.return_value
    repo.get_workflow.return_value = {
        "id": "wf_5555555555555555",
        "slug": "wf_test_slug",
        "status": "draft",
        "version": 1,
        "default_profile_id": "prof_dddd1111dddd1111",
        "name": {"default_locale": "en", "translations": {"en": "Test WF", "fi": "Test WF"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc", "fi": "Desc"}},
        "steps": [{"id": "step_1111111111111111", "task_blueprint": "task_bp"}],
    }
    repo.get_output_profile_by_id.return_value = {
        "id": "prof_dddd1111dddd1111",
        "slug": "test_profile",
        "workflow_id": "wf_5555555555555555",
        "name": {"default_locale": "en", "translations": {"en": "Test Profile"}},
        "visible_block_extensions": [],
        "visible_workflow_extensions": [],
    }
    return repo


@pytest.fixture
def mock_compiler() -> Any:
    compiler = MagicMock()
    compiler.build_xml_context.return_value = "<test>context</test>"
    schema_mock = MagicMock()
    schema_mock.__name__ = "MockSchema"
    schema_mock.model_json_schema.return_value = {"type": "object"}

    mock_validated = MagicMock()
    mock_validated.model_dump.return_value = {
        "blk_0123456789abcdef0123456789ab": {
            "exact_quotes": [""],
            "contextual_override": True,
            "semantic_reasoning": "Because",
            "localized_anchors_found": ["mock anchor"],
            "status": "PASS",
        }
    }
    mock_block = MagicMock()
    mock_block.exact_quotes = ""
    mock_block.contextual_override = True
    mock_block.semantic_reasoning = "Because"
    mock_block.model_copy.return_value = mock_block
    mock_validated.blk_0123456789abcdef0123456789ab = mock_block
    mock_validated.model_copy.return_value = mock_validated

    schema_mock.model_validate.return_value = mock_validated
    compiler.build_dynamic_schema.return_value = schema_mock
    compiler.compile_chunk_prompt.return_value.metadata = {}
    compiler.compile_chunk_prompt.return_value.static_messages = []
    compiler.compile_chunk_prompt.return_value.dynamic_messages = []
    return compiler


@pytest.mark.asyncio
async def test_dag_executor_uses_prompt_blocks_instead_of_matrices(mock_repo: Any, mock_compiler: Any) -> None:
    # Setup Executor
    executor = DAGExecutor(
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        prompt_block_repo=mock_repo,
        output_profile_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
        prompt_compiler=mock_compiler,
    )  # noqa: E501

    # Setup basic valid workflow
    workflow = Workflow(
        id="wf_5555555555555555",
        slug="wf_test_slug",
        status="draft",
        version=1,
        default_profile_id="prof_dddd1111dddd1111",
        name=I18nText(default_locale="en", translations={"en": "Test WF", "fi": "Test WF"}),
        description=I18nText(default_locale="en", translations={"en": "Desc", "fi": "Desc"}),
        steps=[StepRule(id="step_1111111111111111", task_blueprint="task_bp")],
    )

    # Execute
    with patch("backend_v2.llm.client.LLMClient.from_strategy", new_callable=AsyncMock) as mock_strategy:
        mock_bound_client = AsyncMock()
        mock_bound_client._config = MagicMock()
        mock_bound_client._config.provider = "mock_llm_99"

        from backend_v2.models.domain.usage import TokenUsage

        mock_bound_client.run_structured_task.return_value = (
            MagicMock(),
            TokenUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30),
        )

        mock_strategy.return_value = mock_bound_client

        with (
            patch(
                "backend_v2.services.orchestrator.two_pass_atomizer.TwoPassAtomizer.execute_phase_0",
                new_callable=AsyncMock,
            ) as mock_phase_0,
            patch(
                "backend_v2.services.orchestrator.two_pass_atomizer.TwoPassAtomizer.execute_phase_1",
                new_callable=AsyncMock,
            ) as mock_phase_1,
            patch(
                "backend_v2.services.orchestrator.sliding_window_linker.SlidingWindowLinker.link_graph",
                new_callable=AsyncMock,
            ) as mock_link,
            patch(
                "backend_v2.services.orchestrator.enriched_dag_executor.EnrichedDagExecutor.execute_graph",
                new_callable=AsyncMock,
            ) as mock_execute_graph,
            patch("backend_v2.services.orchestrator.result_projector.ResultProjector.project") as mock_project,
        ):
            mock_phase_0.return_value = MagicMock()
            mock_phase_1.return_value = MagicMock()
            mock_link.return_value = MagicMock()
            mock_execute_graph.return_value = MagicMock()

            class MockResultDTO:
                def model_dump(self) -> dict[str, Any]:
                    return {"id": "blk_0123456789abcdef0123456789ab", "contextual_override": True}

            mock_project.return_value = ([MockResultDTO()], {})

            mock_hook_state = MagicMock()
            mock_hook_state.inputs = {"chat_log": "this_is_a_very_long_test_string_to_bypass_fail_fast"}
            mock_hook_state.global_context_vars = {}

            mock_repo.get_execution.return_value = {
                "id": "exe_1231231231231231",
                "workflow_id": "wf_5555555555555555",
                "status": ExecutionStatus.PENDING,
                "active_profile_id": "prof_dddd1111dddd1111",
                "raw_inputs": {"dynamic_inputs": {"chat_log": "this_is_a_very_long_test_string_to_bypass_fail_fast"}},
                "metadata": {"target_locale": "fi", "profile_id": "prof_dddd1111dddd1111"},
            }

            # Also mock the hook registry to prevent "Hook not found" errors in isolated tests
            with patch("backend_v2.services.orchestrator.dag_executor.hook_registry") as mock_hooks:
                mock_hooks.execute = AsyncMock(
                    return_value=HookResult(
                        success=True,
                        state_delta={"inputs": {"chat_log": "this_is_a_very_long_test_string_to_bypass_fail_fast"}},
                    )
                )

                record = await executor.execute_workflow(
                    execution_id="exe_1231231231231231",
                    workflow=workflow,
                    raw_inputs=WorkflowInputs.model_validate(
                        {"dynamic_inputs": {"chat_log": "this_is_a_very_long_test_string_to_bypass_fail_fast"}}
                    ),
                )

    # Assert repo called new method instead of get_all_matrices
    mock_repo.get_all_prompt_blocks.assert_called_once()
    assert not hasattr(mock_repo, "get_all_matrices") or not mock_repo.get_all_matrices.called
    assert record.status == ExecutionStatus.RUNNING
    from backend_v2.models.state import StateProjector

    print(f"DEBUG TRACE: {record.execution_trace}")
    projector = StateProjector()
    results = projector.fold_trace(record.execution_trace)
    print(f"DEBUG RESULTS: {results}")

    found = False
    for dto in results:
        if dto.step_id == "step_1111111111111111" and dto.block_id == "results":
            if isinstance(dto.payload, list) and len(dto.payload) > 0:
                first_res = dto.payload[0]
                if (
                    first_res.get("id") == "blk_0123456789abcdef0123456789ab"
                    and first_res.get("contextual_override") is True
                ):
                    found = True
                    break
    assert found

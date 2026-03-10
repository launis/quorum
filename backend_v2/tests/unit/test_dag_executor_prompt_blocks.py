import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from backend_v2.models.v2_core import Workflow, StepRule, I18nText, ExecutionStatus
from backend_v2.services.orchestrator.dag_executor import DAGExecutor

@pytest.fixture
def mock_repo():
    repo = AsyncMock()
    repo.get_all_prompt_blocks.return_value = [
        {
            "id": "block_test",
            "label": {"default_locale": "fi", "translations": {"fi": "Testi"}},
            "description": {"default_locale": "fi", "translations": {"fi": "Kuvaus"}},
            "category_id": "test",
            "type": "string",
            "allow_decimals": False,
            "strictness_level": 50,
            "require_justification": False
        }
    ]
    repo.get_step_by_id.return_value = {
        "id": "bp_1",
        "slug": "task_bp",
        "name": {"default_locale": "fi", "translations": {}},
        "prompt_blocks": ["block_test"],
        "pre_hooks": []
    }
    return repo


@pytest.fixture
def mock_compiler():
    compiler = MagicMock()
    compiler.build_xml_context.return_value = "<test>context</test>"
    # Mocking a dynamic schema
    schema_mock = MagicMock()
    schema_mock.model_json_schema.return_value = {"type": "object"}
    compiler.build_dynamic_schema.return_value = schema_mock
    return compiler


@pytest.mark.asyncio
async def test_dag_executor_uses_prompt_blocks_instead_of_matrices(mock_repo, mock_compiler):
    # Setup Executor
    executor = DAGExecutor(repository=mock_repo, prompt_compiler=mock_compiler)

    # Setup basic valid workflow
    workflow = Workflow(
        id="wf_test",
        name=I18nText(default_locale="en", translations={"en": "Test WF"}),
        description=I18nText(default_locale="en", translations={"en": "Desc"}),
        steps=[
            StepRule(id="step_1", task_blueprint="task_bp")
        ]
    )

    # Execute
    # We mock LLMClient.from_strategy to avoid actual LLM calls
    with patch("backend_v2.llm.client.LLMClient.from_strategy", new_callable=AsyncMock) as mock_strategy:
        mock_bound_client = AsyncMock()
        mock_bound_client.run_structured_task.return_value = MagicMock(model_dump=lambda: {"test_res": 1})
        mock_strategy.return_value = mock_bound_client

        record = await executor.execute_workflow(
            execution_id="exec_123",
            workflow=workflow,
            raw_inputs={"test_input": "data"}
        )

    # Assert repo called new method instead of get_all_matrices
    mock_repo.get_all_prompt_blocks.assert_called_once()
    assert not hasattr(mock_repo, "get_all_matrices") or not mock_repo.get_all_matrices.called
    assert record.status == ExecutionStatus.COMPLETED
    assert record.results["step_1"]["test_res"] == 1

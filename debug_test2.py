import asyncio
from backend_v2.tests.unit.test_dag_executor_prompt_blocks import mock_repo, mock_compiler
from backend_v2.services.orchestrator.dag_executor import DAGExecutor
from backend_v2.models.v2_core import Workflow, StepRule, I18nText
import backend_v2.llm.client
from unittest.mock import AsyncMock, MagicMock
async def test():
    repo = mock_repo()
    comp = mock_compiler()
    executor = DAGExecutor(repository=repo, prompt_compiler=comp)
    workflow = Workflow(
        id='wf_test', slug='test_wf', name=I18nText(default_locale='en', translations={'en': 'Test WF'}),
        description=I18nText(default_locale='en', translations={'en': 'Desc'}),
        steps=[StepRule(id='step_1', task_blueprint='task_bp')]
    )
    backend_v2.llm.client.LLMClient.from_strategy = AsyncMock()
    mock_bound_client = AsyncMock()
    mock_bound_client.run_structured_task.return_value = MagicMock(model_dump=lambda: {'test_res': 1})
    backend_v2.llm.client.LLMClient.from_strategy.return_value = mock_bound_client
    res = await executor.execute_workflow('exec_123', workflow, {'test_input': 'data'})
    print('STATUS REC:', res.status)
    if res.errors: print('ERRORS:', res.errors)
asyncio.run(test())
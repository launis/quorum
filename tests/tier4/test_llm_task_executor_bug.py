import pytest
from pydantic import BaseModel

from backend_v2.exceptions import AgentExecutionError, LogicalValidationError
from backend_v2.services.llm_task_executor import LLMTaskExecutor


class DummyModel(BaseModel):
    name: str


class MockPromptCompiler:
    def get_schema_healing_prompt(self, *args, **kwargs):
        return "Fix it please."


class MockClient:
    def __init__(self):
        self._config = type("Config", (), {"caching_strategy": None, "provider": "mock"})()

    async def run_structured_task(self, **kwargs):
        raise LogicalValidationError(validation_error_msg="Stuck Loop Error 123")


@pytest.mark.asyncio
async def test_stuck_loop_throws_exception_not_fallback():
    executor = LLMTaskExecutor(MockPromptCompiler())
    client = MockClient()

    try:
        result, usage = await executor.execute_structured_task(
            client=client,
            messages=[{"role": "user", "content": "hello this is long enough string payload to pass length check"}],
            response_model=DummyModel,
        )
        raise AssertionError(f"Bug Present! Expected exception, but got fallback result: {result}")
    except AgentExecutionError:
        pass  # Fixed state, exception properly raised!

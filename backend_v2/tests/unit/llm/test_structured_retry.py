from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel

from backend_v2.exceptions import AgentExecutionError
from backend_v2.llm.client import LLMClient
from backend_v2.models.llm import LLMProviderConfig
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler


class MockLLMResponse:
    def __init__(self, content: str):
        self.content = content
        self.token_usage = {
            "prompt_tokens": 10,
            "completion_tokens": 10,
            "total_tokens": 20,
            "cached_tokens": 0,
            "reasoning_tokens": 0,
            "cost_usd": 0.0,
        }


class DummyModel(BaseModel):
    id: int
    name: str


@pytest.fixture
def mock_repository() -> MagicMock:
    repo = MagicMock()
    repo.get_model_registry = AsyncMock(
        return_value={
            "models": {
                "fast": {
                    "provider": "lite_llm",
                    "model_name": "gpt-4o-mini",
                    "temperature": 0.2,
                    "max_tokens": 1000,
                    "is_active": True,
                    "tpm_limit": 10000,
                    "rpm_limit": 1000,
                }
            }
        }
    )
    return repo


@pytest.mark.asyncio
async def test_run_structured_task_self_healing_success(mock_repository: MagicMock) -> None:
    """Tests that the self-healing retry loop successfully catches a JSON error
    on the first attempt and successfully recovers with valid JSON on the second.
    """
    config = LLMProviderConfig(
        id="prv_12345678",
        provider="lite_llm",
        model_name="fast",
        tpm_limit=1000,
        rpm_limit=100,
        temperature=0.2,
        default_max_tokens=1000,
    )
    client = LLMClient(config=config)
    executor = LLMTaskExecutor(PromptCompiler())

    # 1. Invalid JSON missing quote
    bad_response = MockLLMResponse('{"id": 1, "name": "Broken}')
    # 2. Correct JSON
    good_response = MockLLMResponse('{"id": 1, "name": "Fixed"}')

    mock_provider = AsyncMock()
    mock_provider.generate = AsyncMock()
    mock_provider.generate.side_effect = [bad_response, good_response]

    with patch("backend_v2.llm.provider.LLMFactory.create_provider", return_value=mock_provider):
        messages = [{"role": "user", "content": "Hello world this is a properly sized payload for testing"}]

        result, usage = await executor.execute_structured_task(
            client=client,
            messages=messages,
            response_model=DummyModel,
            max_schema_retries=2,
            max_logical_retries=1,
        )

        # Assert execution
        assert getattr(result, "name", "") == "Fixed"
        assert isinstance(result, DummyModel)
        assert mock_provider.generate.call_count == 2
        assert usage.total_tokens == 40  # 20 from first attempt + 20 from second attempt


@pytest.mark.asyncio
async def test_run_structured_task_self_healing_exhaustion(mock_repository: MagicMock) -> None:
    """Tests that the self-healing circuit breaker triggers an AgentExecutionError
    if the maximum number of retries is exhausted with invalid schema outputs.
    """
    config = LLMProviderConfig(
        id="prv_12345678",
        provider="lite_llm",
        model_name="fast",
        tpm_limit=1000,
        rpm_limit=100,
        temperature=0.2,
        default_max_tokens=1000,
    )
    client = LLMClient(config=config)
    executor = LLMTaskExecutor(PromptCompiler())

    # Persistent Pydantic validation failures (e.g. wrong type for id)
    bad_responses = [
        MockLLMResponse('{"id": "not_an_int", "name": "Failure1"}'),
        MockLLMResponse('{"id": "still_fails", "name": "Failure2"}'),
    ]

    mock_provider = AsyncMock()
    mock_provider.generate = AsyncMock()
    mock_provider.generate.side_effect = bad_responses  # Exactly 2 fail responses

    with patch("backend_v2.llm.provider.LLMFactory.create_provider", return_value=mock_provider):
        with pytest.raises(AgentExecutionError) as exc_info:
            # Limit retries to 2 for exhaust test
            await executor.execute_structured_task(
                client=client,
                messages=[
                    {"role": "user", "content": "Execute! This is a long enough payload to pass the fail-fast check"}
                ],
                response_model=DummyModel,
                max_schema_retries=1,
                max_logical_retries=0,
            )

        assert "AGENT_SCHEMA_VALIDATION_FAILED" in str(exc_info.value)
        assert mock_provider.generate.call_count == 2

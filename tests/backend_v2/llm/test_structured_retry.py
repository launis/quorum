import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel, ValidationError

from backend_v2.exceptions import AgentExecutionError, ConfigurationError
from backend_v2.llm.client import LLMClient


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
def mock_repository():
    repo = MagicMock()
    repo.get_model_registry = AsyncMock(
        return_value={
            "models": {
                "fast": {
                    "provider": "openai",
                    "model_name": "gpt-4o-mini",
                    "temperature": 0.2,
                    "max_tokens": 1000,
                    "is_active": True,
                }
            }
        }
    )
    return repo


@pytest.mark.asyncio
async def test_run_structured_task_self_healing_success(mock_repository):
    """
    Tests that the self-healing retry loop successfully catches a JSON error
    on the first attempt and successfully recovers with valid JSON on the second.
    """
    client = LLMClient()

    # 1. Invalid JSON missing quote
    bad_response = MockLLMResponse('{"id": 1, "name": "Broken}')
    # 2. Correct JSON
    good_response = MockLLMResponse('{"id": 1, "name": "Fixed"}')

    mock_provider = AsyncMock()
    mock_provider.generate.side_effect = [bad_response, good_response]

    with patch("backend_v2.llm.client.LLMFactory.create_provider", return_value=mock_provider):
        messages = [{"role": "user", "content": "Hello"}]
        
        result, usage = await client.run_structured_task(
            messages=messages,
            response_model=DummyModel,
            model="fast",
            max_retries=3,
        )

        # Assert execution
        assert getattr(result, "name", "") == "Fixed"
        assert isinstance(result, DummyModel)
        assert mock_provider.generate.call_count == 2
        assert usage["total_tokens"] == 40  # 20 from first attempt + 20 from second attempt


@pytest.mark.asyncio
async def test_run_structured_task_self_healing_exhaustion(mock_repository):
    """
    Tests that the self-healing circuit breaker triggers an AgentExecutionError
    if the maximum number of retries is exhausted with invalid schema outputs.
    """
    client = LLMClient()

    # Persistent Pydantic validation failures (e.g. wrong type for id)
    bad_responses = [
        MockLLMResponse('{"id": "not_an_int", "name": "Failure1"}'),
        MockLLMResponse('{"id": "still_fails", "name": "Failure2"}'),
    ]

    mock_provider = AsyncMock()
    mock_provider.generate.side_effect = bad_responses  # Exactly 2 fail responses

    with patch("backend_v2.llm.client.LLMFactory.create_provider", return_value=mock_provider):
        with pytest.raises(AgentExecutionError) as exc_info:
            # Limit retries to 2 for exhaust test
            await client.run_structured_task(
                messages=[{"role": "user", "content": "Execute!"}],
                response_model=DummyModel,
                model="fast",
                max_retries=2,
            )

        assert "Self-Healing exhausted" in str(exc_info.value)
        assert mock_provider.generate.call_count == 2

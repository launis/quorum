from typing import Any, cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend_v2.exceptions import AgentExecutionError
from backend_v2.llm.client import LLMClient


class DummyConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    provider: str = "lite_llm"
    model_name: str = "pytest-model-1"
    temperature: float = 0.0
    default_max_tokens: int = 1000
    is_active: bool = True
    tpm_limit: int = 10000
    rpm_limit: int = 1000
    caching_strategy: str = "none"
    top_p: float | None = None
    top_k: int | None = None


class DummyStrictModel(BaseModel):
    """Epic 12: Micro-CoT validation test model."""

    step_1_evidence_quote: str | None = Field(default=None)
    step_4_final_score: int

    @model_validator(mode="before")
    def force_logic(cls, values: Any) -> Any:
        """Socratic logic constraint."""
        if isinstance(values, dict):
            score = values.get("step_4_final_score")
            quote = values.get("step_1_evidence_quote")
            if score == 5 and not quote:
                raise ValueError("CRITICAL LOGICAL ERROR: High score but no quote.")
        return values


@pytest.mark.asyncio
@patch("backend_v2.llm.provider.LLMFactory.create_provider")
async def test_finops_circuit_breaker_missing_usage(mock_create_provider: MagicMock) -> None:
    """Epic 12 Phase 3: Assert missing token usage crashes the Node securely."""
    mock_provider = AsyncMock()
    mock_provider.generate = AsyncMock()
    mock_create_provider.return_value = mock_provider

    # LLM Provider responds but "forgets" FinOps token metrics
    mock_response = MagicMock()
    mock_response.content = '{"step_4_final_score": 5}'
    mock_response.token_usage = None

    mock_provider.generate.return_value = mock_response

    client = LLMClient(config=cast(Any, DummyConfig()))

    # Circuit Breaker must trigger AgentExecutionError (CRITICAL)
    with pytest.raises(AgentExecutionError) as exc:
        await client.run_structured_task(
            messages=[{"role": "user", "content": "Test"}], response_model=DummyStrictModel
        )

    # Check for the correct 7807 Error Code inside the exception representation
    assert "AGENT_EXECUTION_CRITICAL" in str(exc.value)


@pytest.mark.asyncio
@patch("backend_v2.llm.provider.LLMFactory.create_provider")
async def test_semantic_self_healing_retry(mock_create_provider: MagicMock) -> None:
    """Epic 12 Phase 3: Assert Socratic prompt injection on logical validation errors."""
    mock_provider = AsyncMock()
    mock_provider.generate = AsyncMock()
    mock_create_provider.return_value = mock_provider

    usage = {
        "prompt_tokens": 10,
        "completion_tokens": 5,
        "total_tokens": 15,
        "cached_tokens": 0,
        "reasoning_tokens": 0,
        "cost_usd": 0.01,
    }

    # First Generation: LLM Hallucinates a high score without evidence
    mock_fail_response = MagicMock()
    mock_fail_response.content = '{"step_4_final_score": 5, "step_1_evidence_quote": null}'
    mock_fail_response.token_usage = usage

    # Second Generation: LLM fixes logic using the Socratic prompt
    mock_success_response = MagicMock()
    mock_success_response.content = '{"step_4_final_score": 5, "step_1_evidence_quote": "Found it"}'
    mock_success_response.token_usage = usage

    mock_provider.generate.side_effect = [mock_fail_response, mock_success_response]

    client = LLMClient(config=cast(Any, DummyConfig()))
    messages = [{"role": "user", "content": "Evaluate text"}]

    from backend_v2.services.llm_task_executor import LLMTaskExecutor
    from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler

    compiler = PromptCompiler()
    executor = LLMTaskExecutor(prompt_compiler=compiler)

    result_model, total_usage = await executor.execute_structured_task(
        client=client, messages=messages, response_model=DummyStrictModel, max_schema_retries=2, max_logical_retries=2
    )

    # 1. Structural Assertions
    assert mock_provider.generate.call_count == 2
    assert result_model.step_4_final_score == 5
    assert result_model.step_1_evidence_quote == "Found it"

    # 2. Cumulative FinOps Validation (10 + 10 prompt tokens, 5 + 5 completion)
    assert total_usage.completion_tokens == 10
    assert total_usage.total_tokens == 30
    assert abs(total_usage.cost_usd - 0.02) < 0.001

    # 3. Micro-CoT Feedback Injection Validation
    args, kwargs = mock_provider.generate.call_args_list[1]
    msgs = kwargs.get("messages", [])

    # The self-healing loop appends to the existing user message
    assert len(msgs) == 1
    socratic_system = msgs[-1].get("content", "")

    # Confirm Semantic instruction strings
    assert "CRITICAL LOGICAL ERROR" in socratic_system
    assert "STRICT JSON SCHEMA VALIDATION FAILED" in socratic_system

import pytest
from unittest.mock import AsyncMock, MagicMock
from pydantic import BaseModel, ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.schema_factory import SchemaFactory
from backend_v2.models.v2_core import PromptBlock
from backend_v2.llm.client import LLMSchemaValidationError


@pytest.mark.asyncio
async def test_synthesis_schema_hallucination_repro():
    """Reproduces the Schema Validation hallucination error where eval_1 is an object instead of a string."""
    
    # 1. Setup a mocked LLMClient that returns the hallucinated JSON
    mock_client = AsyncMock()
    mock_client.provider_id = "test_provider"
    
    # Simulate LiteLLM returning a nested object for a string field
    mock_response = {
        "reasoning_trace": "Some reasoning.",
        "evaluation_notes": "Some notes.",
        "eval_1": {
            "section_syntheses": [
                {"section_name": "Johdanto", "summary": "Test summary"}
            ]
        }
    }
    
    # Since run_structured_task does the validation, we need to mock it to actually run the Pydantic validation
    # or just let run_structured_task raise the LLMSchemaValidationError like in the trace.
    async def fake_run_structured_task(messages, response_model, **kwargs):
        try:
            return response_model.model_validate(mock_response), {"prompt_tokens": 10}
        except ValidationError as e:
            raise LLMSchemaValidationError("LLM Schema Validation Failed", validation_error_msg=e.json()) from e

    mock_client.run_structured_task = fake_run_structured_task
    
    executor = LLMTaskExecutor(prompt_compiler=AsyncMock())
    
    # 2. Setup the dynamic schema exactly like the synthesis block
    class DynamicResponseModel(BaseModel):
        reasoning_trace: str
        evaluation_notes: str
        eval_1: str
    
    long_test_payload = "This is a very long test payload that satisfies the fail-fast length check of the executor. " * 50
    # 3. Execute and verify it fails with the exact AGENT_SCHEMA_VALIDATION_FAILED code
    with pytest.raises(AppException) as exc_info:
        await executor.execute_structured_task(
            client=mock_client,
            messages=[{"role": "user", "content": long_test_payload}],
            response_model=DynamicResponseModel,
            max_schema_retries=0
        )
        
    assert exc_info.value.details["error_code"] == ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED

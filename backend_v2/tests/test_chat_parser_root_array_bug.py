import pytest
import json
from unittest.mock import AsyncMock, patch
from backend_v2.services.chat_parser import ChatParserService
from backend_v2.models.v2_core import ChatHistoryDTO

@pytest.mark.asyncio
async def test_chat_parser_root_array_bug():
    """TDD Repro for Tier 4 Bug Hunting: LLM returning raw list instead of ChatHistoryDTO object."""
    
    # Mock LLMClient
    mock_client = AsyncMock()
    
    # We mock LLMTaskExecutor to simulate the exact failure scenario.
    # Actually, we should mock the provider/client generating the raw string, 
    # but the error comes from executor.execute_structured_task returning or throwing ValidationError.
    # Wait, the ValidationError is thrown inside `run_structured_task` when `model_validate_json` is called.
    
    from pydantic_core._pydantic_core import ValidationError
    from backend_v2.exceptions import LLMSchemaValidationError
    
    # We want to test the LLM returning a raw array `[...]`
    # Let's mock LLMClient.run_structured_task directly to simulate the Pydantic fail-fast.
    
    raw_array_json = '[{"role": "user", "content": "Miten sitra..."}]'
    
    # Let's simulate what LLMClient.run_structured_task does natively:
    try:
        ChatHistoryDTO.model_validate_json(raw_array_json)
        pytest.fail("Should have thrown ValidationError!")
    except Exception as e:
        assert "Input should be an object" in str(e)
        assert "input_type=list" in str(e)


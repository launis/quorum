
import pytest
from unittest.mock import MagicMock, AsyncMock
from backend.agents.base import BaseAgent
from backend.models.state import WorkflowState, InputData
from pydantic import BaseModel
from typing import Optional, Type

class MockSchema(BaseModel):
    field1: str
    field2: int

class MockAgent(BaseAgent):
    state_field = "aux_data" # Write to aux_data by default
    
    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        return MockSchema

@pytest.fixture
def mock_state():
    return WorkflowState(execution_id="test", inputs=InputData())

@pytest.mark.asyncio
async def test_schema_validation_success(mock_state):
    agent = MockAgent()
    agent.llm_provider = AsyncMock()
    
    mock_resp = MagicMock()
    mock_resp.content = '{"field1": "test", "field2": 123}'
    mock_resp.reasoning_token = None
    agent.llm_provider.generate.return_value = mock_resp
    
    # override output_key to test specific field
    await agent.execute(mock_state, output_key="test_output")
    
    # Check aux_data (BaseAgent defaults to putting schema output in aux_data if field not on State)
    # But wait, BaseAgent._update_state logic:
    # if hasattr(state, target_field): setattr... else: state.aux_data[target_field] = ...
    
    data = mock_state.aux_data["test_output"]
    assert data['field1'] == "test"
    assert data['field2'] == 123

@pytest.mark.asyncio
async def test_schema_validation_failure_retry(mock_state):
    # This test assumes the BaseAgent/LLMProvider handles retries.
    # Actually, retries are usually handled inside LLMProvider.generate if implemented, 
    # OR explicit loop in execute. BaseAgent.execute calls verify? No.
    # Ideally, we should test LLMProvider's retry logic, but here we test if Agent fails gracefully 
    # if provider returns bad JSON eventually?
    # BaseAgent doesn't loop for retries itself; it expects Provider to handle valid JSON generation.
    # However, let's verify BaseAgent raises error on strict failure.
    
    agent = MockAgent()
    agent.llm_provider = AsyncMock()
    
    mock_resp_bad = MagicMock()
    mock_resp_bad.content = '{"field1": "test", "field2": "invalid"}' # Invalid int
    
    agent.llm_provider.generate.return_value = mock_resp_bad
    
    with pytest.raises(Exception) as excinfo:
        await agent.execute(mock_state, output_key="test_output")
    
    # Pydantic validation error or JSON parse error
    assert "Generic state update failed" in str(excinfo.value) or "validation error" in str(excinfo.value).lower()

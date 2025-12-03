import pytest
from unittest.mock import MagicMock, patch
from backend.agents.base import BaseAgent
from pydantic import BaseModel, ValidationError

class MockSchema(BaseModel):
    field1: str
    field2: int

class MockAgent(BaseAgent):
    def construct_user_prompt(self, **kwargs) -> str:
        return "mock prompt"

    def _process(self, validation_schema=None, **kwargs):
        return self.get_json_response(
            prompt="mock prompt",
            validation_schema=validation_schema
        )

def test_schema_validation_success():
    agent = MockAgent()
    
    # Mock LLM response
    with patch.object(agent, '_call_llm', return_value='{"field1": "test", "field2": 123}'):
        result = agent._process(validation_schema=MockSchema)
        
    assert result['field1'] == "test"
    assert result['field2'] == 123

def test_schema_validation_failure_retry():
    agent = MockAgent()
    
    # Mock LLM response: first invalid, then valid
    with patch.object(agent, '_call_llm', side_effect=[
        '{"field1": "test", "field2": "invalid"}', # Invalid type for field2
        '{"field1": "test", "field2": 123}'        # Valid
    ]):
        result = agent._process(validation_schema=MockSchema)
        
    assert result['field1'] == "test"
    assert result['field2'] == 123

def test_schema_validation_failure_max_retries():
    agent = MockAgent()
    
    # Mock LLM response: always invalid
    with patch.object(agent, '_call_llm', return_value='{"field1": "test", "field2": "invalid"}'):
        result = agent._process(validation_schema=MockSchema)
        
    assert "error" in result
    assert "Schema validation failed" in result['error']


import asyncio
import logging
from pydantic import BaseModel
from unittest.mock import AsyncMock, MagicMock
import sys

# Add project root
sys.path.append("c:\\src\\quorum")

from backend.llm.provider import LiteLLMProvider, LLMResponse

# Setup Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("Test")

# Define Schema
class TestSchema(BaseModel):
    message: str
    count: int

async def test_hydration():
    logger.info("Starting Hydration Test...")
    
    # 1. Instantiate Provider (Mocking Router to avoid real calls)
    # Use a real provider prefix to pass inner validation, but we won't call it.
    provider = LiteLLMProvider(model_name="gpt-3.5-turbo", api_key="fake")
    provider.router = AsyncMock()
    
    # 2. Mock Response (Dict Format mimicking JSON mode)
    mock_response_dict = {
        "message": "Hello World",
        "count": 42
    }
    
    # Mock the Router response structure
    mock_completion_obj = MagicMock()
    # Pydantic models (like what LiteLLM returns) have a .model_dump() or .dict() method
    mock_completion_obj.model_dump.return_value = {"id": "mock-id", "usage": {"total_tokens": 100}}
    
    mock_usage = MagicMock()
    mock_usage.prompt_tokens = 50
    mock_usage.completion_tokens = 50
    mock_usage.total_tokens = 100
    mock_completion_obj.usage = mock_usage

    mock_choice = MagicMock()
    mock_message = MagicMock()
    
    # The Important Part: Content is a JSON string, NO parsed field
    mock_message.content = '{"message": "Hello World", "count": 42}'
    mock_message.parsed = None # Simulate non-parsing provider
    
    mock_choice.message = mock_message
    mock_completion_obj.choices = [mock_choice]
    
    # Make router return this
    provider.router.acompletion.return_value = mock_completion_obj
    
    # 3. Call Generate with Schema
    logger.info("Calling generate with schema...")
    response = await provider.generate(
        prompt="test",
        response_schema=TestSchema
    )
    
    # 4. Assertions
    logger.info(f"Response Type: {type(response.parsed_content)}")
    
    assert response.parsed_content is not None, "Parsed Content is None"
    assert isinstance(response.parsed_content, TestSchema), f"Expected TestSchema, got {type(response.parsed_content)}"
    assert response.parsed_content.message == "Hello World", "Data mismatch"
    
    print("\nSUCCESS: Provider successfully hydrated Dict -> Pydantic Model!")

if __name__ == "__main__":
    try:
        asyncio.run(test_hydration())
    except Exception as e:
        print(f"\nFAILURE: {e}")
        exit(1)

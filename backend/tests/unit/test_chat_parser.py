import json
import pytest
from unittest.mock import AsyncMock, patch

from backend.exceptions import AppException, ErrorCodes, ConfigurationError
from backend.models.dtos.chat_history import ChatHistoryDTO, ChatMessageDTO, ChatRole
from backend.services.chat_parser import parse_pasted_chat

@pytest.fixture
def mock_llm_client():
    with patch("backend.services.chat_parser.LLMClient") as mock_client_class:
        mock_client = AsyncMock()
        # LLMClient.from_strategy IS an async function, so its mock needs to be an AsyncMock returning the instance
        mock_client_class.from_strategy = AsyncMock(return_value=mock_client)
        yield mock_client

@pytest.fixture
def valid_llm_response():
    data = {
        "conversation": [
            {"order": 1, "role": ChatRole.USER, "text": "Hello there"},
            {"order": 2, "role": ChatRole.AI, "text": "Hi! How can I help?"}
        ]
    }
    return ChatHistoryDTO.model_validate(data)

@pytest.mark.asyncio
async def test_parse_empty_input_fails_fast():
    # Arrange
    empty_input = "   \n  "
    
    # Act & Assert
    with pytest.raises(AppException) as exc_info:
        await parse_pasted_chat(empty_input)
        
    assert exc_info.value.details["error_code"] == ErrorCodes.EMPTY_INPUT.value
    assert exc_info.value.status_code == 400

@pytest.mark.asyncio
async def test_parse_success(mock_llm_client, valid_llm_response):
    # Arrange
    raw_text = "User: Hello there\nAI: Hi! How can I help?"
    mock_llm_client.run_structured_task.return_value = valid_llm_response

    # Act
    result = await parse_pasted_chat(raw_text)

    # Assert
    assert isinstance(result, ChatHistoryDTO)
    assert len(result.conversation) == 2
    assert result.conversation[0].role == ChatRole.USER
    assert result.conversation[1].text == "Hi! How can I help?"
    
    # Verify LLM call
    mock_llm_client.run_structured_task.assert_called_once()
    kwargs = mock_llm_client.run_structured_task.call_args.kwargs
    assert kwargs["response_model"] == ChatHistoryDTO
    assert kwargs["temperature"] == 0.0

@pytest.mark.asyncio
async def test_parse_invalid_schema_fails_fast(mock_llm_client):
    # Arrange
    raw_text = "Some random text"
    
    # Mocking a Pydantic Validation Error since run_structured_task now raises it
    from pydantic import ValidationError
    
    # To properly simulate ValidationError, we inject an error side effect 
    class MockErrorModel(ChatHistoryDTO):
        pass
        
    try:
        MockErrorModel.model_validate({"conversation": [{"wrong_key": "User"}]})
    except ValidationError as e:
        validation_error = e

    mock_llm_client.run_structured_task.side_effect = validation_error

    # Act & Assert
    with pytest.raises(AppException) as exc_info:
        await parse_pasted_chat(raw_text)
        
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert exc_info.value.status_code == 400

@pytest.mark.asyncio
async def test_configuration_error_propagation():
    # Arrange
    with patch("backend.services.chat_parser.LLMClient.from_strategy") as mock_from_strategy:
        mock_from_strategy.side_effect = ConfigurationError("API key missing")
        
        # Act & Assert
        with pytest.raises(AppException) as exc_info:
            await parse_pasted_chat("Some valid text")
            
        assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value
        assert exc_info.value.status_code == 500

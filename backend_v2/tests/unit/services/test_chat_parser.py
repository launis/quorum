from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.v2_core import ChatHistoryDTO
from backend_v2.services.chat_parser import ChatParserService


@pytest.fixture
def mock_repository() -> AsyncMock:
    """Provides an isolated AsyncMock for the database repository."""
    return AsyncMock()


@pytest.mark.asyncio
async def test_chat_parser_empty_input_fails_fast(mock_repository: AsyncMock) -> None:
    """FAIL-FAST: Ensure empty input raises immediate AppException."""
    with pytest.raises(AppException) as excinfo:
        await ChatParserService.parse_pasted_chat("", mock_repository)

    assert excinfo.value.details["error_code"] == ErrorCodes.EMPTY_INPUT.value


@pytest.mark.asyncio
@patch("backend_v2.services.chat_parser.LLMClient.from_strategy")
async def test_chat_parser_role_segregation_and_success(
    mock_from_strategy: AsyncMock, mock_repository: AsyncMock
) -> None:
    """Ensures that the ChatParser STRICTLY separates System and User roles to prevent prompt injection."""
    # Setup mock LLM Client (Architectural Mocking Mandate)
    mock_client = AsyncMock()

    # Setup a valid DTO response
    from backend_v2.models.v2_core import ChatMessageDTO

    mock_dto = ChatHistoryDTO(
        conversation=[
            ChatMessageDTO(role="User", content="Hello"),
            ChatMessageDTO(role="AI", content="Hi"),
        ]
    )
    mock_client.run_structured_task.return_value = (
        mock_dto,
        {"prompt_tokens": 10, "completion_tokens": 0, "total_tokens": 10},
    )

    from unittest.mock import MagicMock

    mock_config = MagicMock()
    mock_config.caching_strategy = "none"
    mock_config.model_copy.return_value = mock_config
    mock_client._config = mock_config

    mock_from_strategy.return_value = mock_client

    # Execute
    raw_paste = "User: Hello\nAI: Hi"
    res = await ChatParserService.parse_pasted_chat(raw_paste, mock_repository)

    # Assert successful parse
    assert res == mock_dto

    mock_from_strategy.assert_called_once_with("fast", repository=mock_repository, pipeline_name="chat_parser")
    mock_client.run_structured_task.assert_called_once()

    call_kwargs = mock_client.run_structured_task.call_args.kwargs
    messages = call_kwargs["messages"]

    # The absolute critical test: Verify there is a system role AND a user role
    assert len(messages.static_messages) == 1
    assert len(messages.dynamic_messages) == 1
    assert messages.static_messages[0].role == "system"
    assert "data-mining expert" in messages.static_messages[0].content

    assert messages.dynamic_messages[0].role == "user"
    assert raw_paste in messages.dynamic_messages[0].content

    assert call_kwargs["response_model"] == ChatHistoryDTO

"""Unit tests for ChatParserService.

Validates anchor-based boundary slicing, role segregation, Fail-Fast schema validation,
and exception handling under modern V2 architecture.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.models.dtos.ingress import ChatTurnAnchorDTO, ChatTurnAnchorsResponseDTO
from backend_v2.services.chat_parser import ChatParserService


@pytest.fixture
def mock_repository() -> AsyncMock:
    """Provide an isolated AsyncMock for the database repository."""
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
    """Ensure ChatParser segregates roles and slices exact verbatim turns via anchors."""
    mock_client = AsyncMock()

    mock_anchors = ChatTurnAnchorsResponseDTO(
        turns=[
            ChatTurnAnchorDTO(speaker="user", start_phrase="Hello there", end_phrase="how are you"),
            ChatTurnAnchorDTO(speaker="ai", start_phrase="I am doing well", end_phrase="help you today"),
        ]
    )
    mock_client.run_structured_task.return_value = (
        mock_anchors,
        {"prompt_tokens": 10, "completion_tokens": 0, "total_tokens": 10},
    )

    mock_config = MagicMock()
    mock_config.caching_strategy = "none"
    mock_config.model_copy.return_value = mock_config
    mock_client._config = mock_config

    mock_from_strategy.return_value = mock_client

    raw_paste = "User: Hello there, how are you\nAI: I am doing well, how can I help you today?"
    res = await ChatParserService.parse_pasted_chat(raw_paste, mock_repository)

    assert len(res.conversation) == 2
    assert res.conversation[0].role == "user"
    assert res.conversation[0].content == "Hello there, how are you"
    assert res.conversation[1].role == "ai"
    assert res.conversation[1].content == "I am doing well, how can I help you today"

    mock_from_strategy.assert_called_once_with("fast", repository=mock_repository, pipeline_name="chat_parser")
    mock_client.run_structured_task.assert_called_once()

    call_kwargs = mock_client.run_structured_task.call_args.kwargs
    messages = call_kwargs["messages"]

    assert len(messages.static_messages) == 1
    assert len(messages.dynamic_messages) == 1
    assert messages.static_messages[0].role == "system"
    assert "boundary-detection expert" in messages.static_messages[0].content

    assert messages.dynamic_messages[0].role == "user"
    assert raw_paste in messages.dynamic_messages[0].content

    assert call_kwargs["response_model"] == ChatTurnAnchorsResponseDTO


@pytest.mark.asyncio
@patch("backend_v2.services.chat_parser.LLMClient.from_strategy")
async def test_chat_parser_configuration_error(mock_from_strategy: AsyncMock, mock_repository: AsyncMock) -> None:
    """Ensure ConfigurationError during LLMClient initialization triggers 500 AppException."""
    mock_from_strategy.side_effect = ConfigurationError("Model fast not found")
    with pytest.raises(AppException) as excinfo:
        await ChatParserService.parse_pasted_chat("User: Hi\nAI: Hello", mock_repository)

    assert excinfo.value.status_code == 500
    assert excinfo.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value


@pytest.mark.asyncio
@patch("backend_v2.services.chat_parser.LLMClient.from_strategy")
async def test_chat_parser_empty_conversation_fails_fast(
    mock_from_strategy: AsyncMock, mock_repository: AsyncMock
) -> None:
    """Ensure empty conversation list returned by LLM raises 400 VALIDATION_FAILED AppException."""
    mock_client = AsyncMock()
    mock_anchors = ChatTurnAnchorsResponseDTO(turns=[])
    mock_client.run_structured_task.return_value = (
        mock_anchors,
        {"prompt_tokens": 10, "completion_tokens": 0, "total_tokens": 10},
    )
    mock_from_strategy.return_value = mock_client

    with pytest.raises(AppException) as excinfo:
        await ChatParserService.parse_pasted_chat("Some text with no chat structure", mock_repository)

    assert excinfo.value.status_code == 400
    assert excinfo.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
@patch("backend_v2.services.chat_parser.LLMClient.from_strategy")
async def test_chat_parser_start_anchor_not_found_fails_fast(
    mock_from_strategy: AsyncMock, mock_repository: AsyncMock
) -> None:
    """Ensure start anchor missing from source text triggers 400 PARSING_FAILED AppException."""
    mock_client = AsyncMock()
    mock_anchors = ChatTurnAnchorsResponseDTO(
        turns=[
            ChatTurnAnchorDTO(
                speaker="user",
                start_phrase="Missing phrase that does not exist",
                end_phrase="how are you",
            ),
        ]
    )
    mock_client.run_structured_task.return_value = (
        mock_anchors,
        {"prompt_tokens": 10, "completion_tokens": 0, "total_tokens": 10},
    )
    mock_from_strategy.return_value = mock_client

    with pytest.raises(AppException) as excinfo:
        await ChatParserService.parse_pasted_chat("User: Hello there, how are you", mock_repository)

    assert excinfo.value.status_code == 400
    assert excinfo.value.details["error_code"] == ErrorCodes.PARSING_FAILED.value


@pytest.mark.asyncio
@patch("backend_v2.services.chat_parser.LLMClient.from_strategy")
async def test_chat_parser_end_anchor_not_found_fails_fast(
    mock_from_strategy: AsyncMock, mock_repository: AsyncMock
) -> None:
    """Ensure end anchor missing from source text after start triggers 400 PARSING_FAILED AppException."""
    mock_client = AsyncMock()
    mock_anchors = ChatTurnAnchorsResponseDTO(
        turns=[
            ChatTurnAnchorDTO(speaker="user", start_phrase="Hello there", end_phrase="nonexistent ending phrase"),
        ]
    )
    mock_client.run_structured_task.return_value = (
        mock_anchors,
        {"prompt_tokens": 10, "completion_tokens": 0, "total_tokens": 10},
    )
    mock_from_strategy.return_value = mock_client

    with pytest.raises(AppException) as excinfo:
        await ChatParserService.parse_pasted_chat("User: Hello there, how are you", mock_repository)

    assert excinfo.value.status_code == 400
    assert excinfo.value.details["error_code"] == ErrorCodes.PARSING_FAILED.value


@pytest.mark.asyncio
@patch("backend_v2.services.chat_parser.LLMClient.from_strategy")
async def test_chat_parser_validation_error(mock_from_strategy: AsyncMock, mock_repository: AsyncMock) -> None:
    """Ensure pydantic ValidationError raises 400 VALIDATION_FAILED AppException."""
    mock_client = AsyncMock()
    mock_client.run_structured_task.side_effect = ValidationError.from_exception_data(
        "ChatTurnAnchorsResponseDTO", line_errors=[]
    )
    mock_from_strategy.return_value = mock_client

    with pytest.raises(AppException) as excinfo:
        await ChatParserService.parse_pasted_chat("User: Hi\nAI: Hello", mock_repository)

    assert excinfo.value.status_code == 400
    assert excinfo.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
@patch("backend_v2.services.chat_parser.LLMClient.from_strategy")
async def test_chat_parser_json_decode_error(mock_from_strategy: AsyncMock, mock_repository: AsyncMock) -> None:
    """Ensure json.JSONDecodeError raises 400 VALIDATION_FAILED AppException."""
    mock_client = AsyncMock()
    mock_client.run_structured_task.side_effect = json.JSONDecodeError("Unterminated string", "doc", 0)
    mock_from_strategy.return_value = mock_client

    with pytest.raises(AppException) as excinfo:
        await ChatParserService.parse_pasted_chat("User: Hi\nAI: Hello", mock_repository)

    assert excinfo.value.status_code == 400
    assert excinfo.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
@patch("backend_v2.services.chat_parser.LLMClient.from_strategy")
async def test_chat_parser_unexpected_exception(mock_from_strategy: AsyncMock, mock_repository: AsyncMock) -> None:
    """Ensure generic runtime exceptions raise 502 BAD_GATEWAY AppException."""
    mock_client = AsyncMock()
    mock_client.run_structured_task.side_effect = RuntimeError("Network connection reset")
    mock_from_strategy.return_value = mock_client

    with pytest.raises(AppException) as excinfo:
        await ChatParserService.parse_pasted_chat("User: Hi\nAI: Hello", mock_repository)

    assert excinfo.value.status_code == 502
    assert excinfo.value.details["error_code"] == ErrorCodes.INTERNAL_SERVER_ERROR.value


@pytest.mark.asyncio
@patch("backend_v2.services.chat_parser.LLMClient.from_strategy")
async def test_chat_parser_unicode_whitespace_resilience(
    mock_from_strategy: AsyncMock, mock_repository: AsyncMock
) -> None:
    r"""Ensure anchors match source text containing Unicode whitespace variants (e.g. \u2002, \u00a0)."""
    mock_client = AsyncMock()
    mock_anchors = ChatTurnAnchorsResponseDTO(
        turns=[
            ChatTurnAnchorDTO(
                speaker="user",
                start_phrase="Hei miten menee tänään",
                end_phrase="haluaisin tietää enemmän",
            ),
            ChatTurnAnchorDTO(
                speaker="ai",
                start_phrase="Hei hyvin menee",
                end_phrase="voin auttaa mielelläni",
            ),
        ]
    )
    mock_client.run_structured_task.return_value = (
        mock_anchors,
        {"prompt_tokens": 50, "completion_tokens": 20, "total_tokens": 70},
    )
    mock_from_strategy.return_value = mock_client

    # Source text contains \u2002 (en space) and \u00a0 (no-break space)
    raw_source = (
        "Hei\u2002miten\u2002menee tänään, tässä on hieman tekstiä ja haluaisin\xa0tietää\xa0enemmän.\n\n"
        "Hei hyvin menee kiitos kysymästä, voin   auttaa\u2002mielelläni!"
    )

    history = await ChatParserService.parse_pasted_chat(raw_source, mock_repository)
    assert len(history.conversation) == 2
    assert history.conversation[0].role == "user"
    assert "haluaisin\xa0tietää\xa0enemmän" in history.conversation[0].content
    assert history.conversation[1].role == "ai"
    assert "voin   auttaa\u2002mielelläni" in history.conversation[1].content


def test_find_anchor_span_empty_or_whitespace_raises_value_error() -> None:
    """Ensure _find_anchor_span raises ValueError on empty or whitespace-only phrases."""
    with pytest.raises(ValueError, match="Anchor phrase cannot be empty"):
        ChatParserService._find_anchor_span("Some text", "", 0)

    with pytest.raises(ValueError, match="Anchor phrase cannot be empty"):
        ChatParserService._find_anchor_span("Some text", "   \t\n  ", 0)

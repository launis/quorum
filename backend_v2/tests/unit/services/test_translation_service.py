"""Tests for the translation service."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.models.llm import LLMMessageDTO
from backend_v2.models.prompts.common import (
    STATIC_LINGUISTIC_PROTOCOL,
    build_linguistic_parameters,
)
from backend_v2.services.translation_service import translate_text


def test_build_linguistic_parameters_default_source() -> None:
    """Verify default source language and English reasoning."""
    result = build_linguistic_parameters(target_locale="fi")

    assert "<source_data_language>Unknown/Original</source_data_language>" in result
    assert "<required_output_language>fi</required_output_language>" in result
    assert "<required_reasoning_language>English</required_reasoning_language>" in result


def test_build_linguistic_parameters_custom_source() -> None:
    """Verify custom source language is injected."""
    result = build_linguistic_parameters(target_locale="sv", source_language="de")

    assert "<source_data_language>de</source_data_language>" in result
    assert "<required_output_language>sv</required_output_language>" in result
    assert "<required_reasoning_language>English</required_reasoning_language>" in result


def test_static_linguistic_protocol_structure() -> None:
    """Verify the static protocol covers linguistic mandate and isolation rules."""
    assert "<linguistic_mandate>" in STATIC_LINGUISTIC_PROTOCOL
    assert "reasoning_trace" in STATIC_LINGUISTIC_PROTOCOL
    assert "English" in STATIC_LINGUISTIC_PROTOCOL
    assert STATIC_LINGUISTIC_PROTOCOL.startswith("<linguistic_mandate>")


@pytest.mark.anyio
@pytest.mark.parametrize(
    ("text", "target_lang", "has_client"),
    [
        ("", "fi", True),
        ("   ", "fi", True),
        ("Hello", "", True),
        ("Hello", "en", True),
        ("Hello", "EN", True),
        ("Hello", "fi", False),
    ],
)
async def test_translate_text_early_returns(
    text: str,
    target_lang: str,
    has_client: bool,
) -> None:
    """Verify translate_text early exit conditions return original text without LLM execution."""
    client: LLMClient | None = MagicMock(spec=LLMClient) if has_client else None
    assert await translate_text(text, target_lang, client) == text


@pytest.mark.anyio
async def test_translate_text_str_response_and_cdata_fencing() -> None:
    """Verify translate_text sends typed LLMMessageDTOs with CDATA user_payload fencing and strips string output."""
    mock_client = MagicMock(spec=LLMClient)
    mock_exec = AsyncMock(return_value="  Hei maailma  ")

    with patch(
        "backend_v2.services.translation_service.LLMTaskExecutor.execute_chat_task",
        new=mock_exec,
    ):
        result = await translate_text(
            "Hello <world>",
            "fi",
            mock_client,
            source_language="en",
        )

    assert result == "Hei maailma"
    mock_exec.assert_awaited_once()
    call_kwargs = mock_exec.call_args.kwargs
    assert call_kwargs["client"] is mock_client
    messages = call_kwargs["messages"]
    assert len(messages) == 2
    assert isinstance(messages[0], LLMMessageDTO)
    assert messages[0].role == "system"
    assert "<linguistic_mandate>" in str(messages[0].content)
    assert isinstance(messages[1], LLMMessageDTO)
    assert messages[1].role == "user"
    assert "<required_output_language>fi</required_output_language>" in str(messages[1].content)
    assert "<user_payload>\n<![CDATA[Hello <world>]]>\n</user_payload>" in str(messages[1].content)


@pytest.mark.anyio
async def test_translate_text_tuple_and_non_str_responses() -> None:
    """Verify translate_text unpacks tuple responses, converts non-string responses, and falls back on blank output."""
    mock_client = MagicMock(spec=LLMClient)

    with patch(
        "backend_v2.services.translation_service.LLMTaskExecutor.execute_chat_task",
        new=AsyncMock(return_value=("  Monikkotulos  ", {"total_tokens": 10})),
    ):
        tuple_res = await translate_text("Tuple input", "fi", mock_client)
    assert tuple_res == "Monikkotulos"

    with patch(
        "backend_v2.services.translation_service.LLMTaskExecutor.execute_chat_task",
        new=AsyncMock(return_value={"content": "dict_fallback"}),
    ):
        dict_res = await translate_text("Dict input", "fi", mock_client)
    assert dict_res == "{'content': 'dict_fallback'}"

    with patch(
        "backend_v2.services.translation_service.LLMTaskExecutor.execute_chat_task",
        new=AsyncMock(return_value="   "),
    ):
        blank_res = await translate_text("Original text", "fi", mock_client)
    assert blank_res == "Original text"


@pytest.mark.anyio
@pytest.mark.parametrize(
    "raised_exc",
    [
        AppException(
            message="Upstream failure",
            status_code=502,
            details={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.value},
        ),
        RuntimeError("Provider runtime crash"),
        ValueError("Invalid locale payload"),
    ],
)
async def test_translate_text_exception_fallback_and_dlq_logging(
    raised_exc: Exception,
) -> None:
    """Verify translate_text catches execution errors, logs structured DLQ error_code, and returns original text."""
    mock_client = MagicMock(spec=LLMClient)

    with (
        patch("backend_v2.services.translation_service.logger.error") as mock_log_error,
        patch(
            "backend_v2.services.translation_service.LLMTaskExecutor.execute_chat_task",
            new=AsyncMock(side_effect=raised_exc),
        ),
    ):
        result = await translate_text("Confidential Sitra input", "fi", mock_client)

    assert result == "Confidential Sitra input"
    mock_log_error.assert_called_once()
    extra = mock_log_error.call_args.kwargs["extra"]
    assert extra["error_code"] == ErrorCodes.AGENT_EXECUTION_CRITICAL.name
    assert extra["target_lang"] == "fi"
    assert extra["payload_length"] == len("Confidential Sitra input")

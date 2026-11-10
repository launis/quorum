"""Unit tests for ChatParserService prompt compilation and template isolation."""

from __future__ import annotations

import pytest

from backend_v2.core.template_processor import TemplateProcessor
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.system_config import ChatMessageDTO
from backend_v2.services.orchestrator.prompt_compiler_adapter import PromptCompilerAdapter

__all__ = [
    "test_chat_parser_caching_bug_repro",
    "test_chat_parser_safe_interpolate_missing_placeholder_error",
]


def test_chat_parser_caching_bug_repro() -> None:
    """Verify compiled chat parser messages retain non-empty dynamic user payloads."""
    raw_paste = "user: hello there\nai: how are you doing today?"
    user_content = TemplateProcessor.render_prompt(
        t"<context>\nHere is the raw text to process:\n</context>\n"
        t"<source_data>\n{raw_paste}\n</source_data>\n"
        t"<execution_parameters>\n<parsing_mode>strict</parsing_mode>\n</execution_parameters>"
    )
    messages: list[ChatMessageDTO] = [
        ChatMessageDTO(role="system", content="You are a boundary-detection expert."),
        ChatMessageDTO(role="user", content=user_content),
    ]

    compiler = PromptCompilerAdapter()
    compiled_prompt = compiler.compile_prompt(messages)
    dynamic_msgs = compiled_prompt.to_dynamic_flat()

    assert len(dynamic_msgs) > 0, (
        "Dynamic messages must not be empty to prevent Vertex AI 400 Bad Request when PromptCache is enabled."
    )


def test_chat_parser_safe_interpolate_missing_placeholder_error() -> None:
    """Negative: Verify TemplateProcessor.safe_interpolate raises AppException on missing placeholder."""
    with pytest.raises(AppException) as excinfo:
        TemplateProcessor.safe_interpolate("<source_data>{missing_placeholder}</source_data>", raw_paste="hello")

    assert excinfo.value.status_code == 400
    assert excinfo.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

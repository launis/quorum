"""Unit tests for ChatNormalizerService.

Validates ISTQB equivalence partitions and boundary value conditions for chat parsing,
markdown-fenced JSON extraction, deterministic fast-path regex parsing, paragraph and
table preservation, cryptographic Unicode noise marker preservation, and XML escaping.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import pytest
from pydantic import ValidationError

from backend_v2.database.interfaces import ISystemRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.inputs import ProcessedChatDTO
from backend_v2.models.v2_core import ChatHistoryDTO, ChatMessageDTO
from backend_v2.services.chat_normalizer import ChatNormalizerService
from backend_v2.services.chat_parser import ChatParserService


@pytest.fixture
def mock_system_repo() -> AsyncMock:
    """Provide an isolated AsyncMock implementing ISystemRepository."""
    return AsyncMock(spec=ISystemRepository)


class TestChatNormalizerService:
    """Test suite for ChatNormalizerService."""

    def test_strip_code_fences_plain_text(self) -> None:
        """Verify plain text without fences is returned trimmed."""
        text = "  Hello world  \n"
        assert ChatNormalizerService.strip_code_fences(text) == "Hello world"

    def test_strip_code_fences_json_block(self) -> None:
        """Verify markdown json block fences are stripped properly."""
        text = "```json\n{\"key\": \"val\"}\n```"
        assert ChatNormalizerService.strip_code_fences(text) == "{\"key\": \"val\"}"

    def test_try_parse_json_dict_format(self) -> None:
        """Verify parsing valid JSON object with conversation array."""
        payload = json.dumps({
            "conversation": [
                {"role": "user", "content": "Hi"},
                {"role": "ai", "content": "Hello"},
            ]
        })
        result = ChatNormalizerService.try_parse_json(payload)
        assert result is not None
        assert len(result.conversation) == 2
        assert result.conversation[0].role == "user"
        assert result.conversation[0].content == "Hi"

    def test_try_parse_json_list_format(self) -> None:
        """Verify parsing valid JSON array of chat message turns."""
        payload = json.dumps([
            {"role": "user", "content": "Query"},
            {"role": "assistant", "content": "Answer"},
        ])
        result = ChatNormalizerService.try_parse_json(payload)
        assert result is not None
        assert len(result.conversation) == 2
        assert result.conversation[1].content == "Answer"

    def test_try_parse_json_fenced_json(self) -> None:
        """Verify parsing markdown-fenced JSON string into ChatHistoryDTO."""
        payload = "```json\n" + json.dumps({
            "conversation": [
                {"role": "user", "content": "Question"},
                {"role": "ai", "content": "Response"},
            ]
        }) + "\n```"
        result = ChatNormalizerService.try_parse_json(payload)
        assert result is not None
        assert len(result.conversation) == 2

    def test_try_parse_json_invalid_schema(self) -> None:
        """Negative: Verify invalid JSON structure returns None."""
        assert ChatNormalizerService.try_parse_json('{"invalid": "data"}') is None
        assert ChatNormalizerService.try_parse_json('not json') is None

    def test_try_parse_fast_path_english_labels(self) -> None:
        """Verify fast-path regex matches English colon-delimited labels."""
        raw = "User: What is revenue?\nAssistant: Revenue is 10M."
        result = ChatNormalizerService.try_parse_fast_path(raw)
        assert result is not None
        assert len(result.conversation) == 2
        assert result.conversation[0].role == "user"
        assert result.conversation[0].content == "What is revenue?"
        assert result.conversation[1].role == "ai"
        assert result.conversation[1].content == "Revenue is 10M."

    def test_try_parse_fast_path_finnish_labels(self) -> None:
        """Verify fast-path regex matches Finnish colon-delimited labels."""
        raw = "Käyttäjä: Miten projekti etenee?\nChatGPT: Projekti on aikataulussa."
        result = ChatNormalizerService.try_parse_fast_path(raw)
        assert result is not None
        assert len(result.conversation) == 2
        assert result.conversation[0].role == "user"
        assert result.conversation[0].content == "Miten projekti etenee?"
        assert result.conversation[1].role == "ai"
        assert result.conversation[1].content == "Projekti on aikataulussa."

    def test_try_parse_fast_path_multiline_turns(self) -> None:
        """Verify multiline turns are concatenated properly under the same role."""
        raw = (
            "Human: Line 1 of question.\n"
            "Line 2 of question.\n\n"
            "Claude: Line 1 of answer.\n"
            "Line 2 of answer."
        )
        result = ChatNormalizerService.try_parse_fast_path(raw)
        assert result is not None
        assert len(result.conversation) == 2
        assert result.conversation[0].content == "Line 1 of question.\nLine 2 of question."
        assert result.conversation[1].content == "Line 1 of answer.\nLine 2 of answer."

    def test_try_parse_fast_path_single_turn_rejected(self) -> None:
        """Negative: Single turn conversation without AI must be rejected by fast-path."""
        raw = "User: Only one turn here."
        assert ChatNormalizerService.try_parse_fast_path(raw) is None

    def test_try_parse_fast_path_only_ai_rejected(self) -> None:
        """Negative: Conversation missing user turn must be rejected by fast-path."""
        raw = "Assistant: Hello.\nAI: Another greeting."
        assert ChatNormalizerService.try_parse_fast_path(raw) is None

    def test_clean_turn_content_preserves_paragraphs_and_tables(self) -> None:
        """Verify clean_turn_content preserves structural linebreaks, bullet points, and markdown tables."""
        raw = (
            "### Summary Header\n\n"
            "Paragraph one with some text.\n\n"
            "| Column 1 | Column 2 |\n"
            "| --- | --- |\n"
            "| Val A | Val B |\n\n"
            "- Bullet 1\n"
            "- Bullet 2"
        )
        cleaned = ChatNormalizerService.clean_turn_content(raw)
        assert "### Summary Header" in cleaned
        assert "\n\nParagraph one with some text." in cleaned
        assert "| Column 1 | Column 2 |" in cleaned
        assert "| Val A | Val B |" in cleaned
        assert "- Bullet 1\n- Bullet 2" in cleaned

    def test_clean_turn_content_strips_zero_width_chars(self) -> None:
        """Verify zero-width characters (BOM, soft-hyphens, ZWSP) are stripped."""
        raw = "Hello\ufeff\u200bWorld\u00ad!"
        cleaned = ChatNormalizerService.clean_turn_content(raw)
        assert cleaned == "HelloWorld!"

    def test_clean_turn_content_preserves_unicode_spaces(self) -> None:
        """Verify injected Unicode spaces (U+00A0, U+2002) survive normalization."""
        raw = "User\u00a0turn\u2002with\u2003special\u2009spaces."
        cleaned = ChatNormalizerService.clean_turn_content(raw)
        assert "\u00a0" in cleaned
        assert "\u2002" in cleaned
        assert "\u2003" in cleaned
        assert "\u2009" in cleaned
        assert cleaned == "User\u00a0turn\u2002with\u2003special\u2009spaces."

    def test_clean_turn_content_unicode_only_spaces_not_emptied(self) -> None:
        """Negative: Turn with Unicode spaces must not be completely emptied by ASCII stripping."""
        raw = "\u00a0\u00a0"
        cleaned = ChatNormalizerService.clean_turn_content(raw)
        assert cleaned == "\u00a0\u00a0"

    def test_build_processed_chat_xml_escaping_in_user_payload(self) -> None:
        """Verify user turn content has XML characters escaped in combined prompt payload."""
        dto = ChatHistoryDTO(
            conversation=[
                ChatMessageDTO(role="user", content="<script>alert('xss')</script> & </user_payload>"),
                ChatMessageDTO(role="ai", content="I cannot execute scripts."),
            ]
        )
        processed = ChatNormalizerService.build_processed_chat(dto)
        assert "<user_payload>" in processed.combined
        assert "&lt;script&gt;alert('xss')&lt;/script&gt; &amp; &lt;/user_payload&gt;" in processed.combined
        assert "<script>" not in processed.combined
        # Unescaped raw text in user_only stream
        assert processed.user_only == "<script>alert('xss')</script> & </user_payload>"
        assert processed.ai_only == "I cannot execute scripts."

    def test_build_processed_chat_preserves_user_unicode_markers(self) -> None:
        """Verify cryptographic noise markers in user turn are preserved in user_only and combined."""
        marker = "\u00a0"
        dto = ChatHistoryDTO(
            conversation=[
                ChatMessageDTO(role="user", content=f"Hello{marker}World!"),
                ChatMessageDTO(role="ai", content="Hello back!"),
            ]
        )
        processed = ChatNormalizerService.build_processed_chat(dto)
        assert marker in processed.user_only
        assert marker in processed.combined
        assert marker not in processed.ai_only

    @pytest.mark.asyncio
    async def test_parse_chat_to_dto_fast_path(self, mock_system_repo: AsyncMock) -> None:
        """Verify parse_chat_to_dto succeeds via fast-path without LLM fallback."""
        raw = "User: Need help\nAI: I am ready"
        with patch.object(ChatParserService, "parse_pasted_chat") as mock_llm_parse:
            result = await ChatNormalizerService.parse_chat_to_dto(raw, "chat_log", mock_system_repo)
            mock_llm_parse.assert_not_called()
            assert len(result.conversation) == 2

    @pytest.mark.asyncio
    async def test_parse_chat_to_dto_llm_fallback(self, mock_system_repo: AsyncMock) -> None:
        """Verify unstructured dialogue falls back to ChatParserService."""
        raw = "This is some unstructured narrative between two people discussing a plan."
        mock_chat = ChatHistoryDTO(
            conversation=[
                ChatMessageDTO(role="user", content="Person 1 statement"),
                ChatMessageDTO(role="ai", content="Person 2 response"),
            ]
        )
        with patch.object(ChatParserService, "parse_pasted_chat", return_value=mock_chat) as mock_llm_parse:
            result = await ChatNormalizerService.parse_chat_to_dto(raw, "chat_log", mock_system_repo)
            mock_llm_parse.assert_called_once_with(raw, system_repo=mock_system_repo)
            assert len(result.conversation) == 2

    @pytest.mark.asyncio
    async def test_parse_chat_to_dto_empty_input_raises_app_exception(
        self, mock_system_repo: AsyncMock
    ) -> None:
        """Negative: Empty or whitespace input raises AppException with EMPTY_INPUT."""
        with pytest.raises(AppException) as excinfo:
            await ChatNormalizerService.parse_chat_to_dto("", "chat_log", mock_system_repo)
        assert excinfo.value.details["error_code"] == ErrorCodes.EMPTY_INPUT.value

        with pytest.raises(AppException) as excinfo2:
            await ChatNormalizerService.parse_chat_to_dto("   \n\t  ", "chat_log", mock_system_repo)
        assert excinfo2.value.details["error_code"] == ErrorCodes.EMPTY_INPUT.value

    @pytest.mark.asyncio
    async def test_parse_chat_to_dto_llm_failure_raises_app_exception(
        self, mock_system_repo: AsyncMock
    ) -> None:
        """Negative: LLM parser returning empty conversation raises AppException."""
        raw = "Some prose"
        empty_chat = ChatHistoryDTO(conversation=[])
        with patch.object(ChatParserService, "parse_pasted_chat", return_value=empty_chat):
            with pytest.raises(AppException) as excinfo:
                await ChatNormalizerService.parse_chat_to_dto(raw, "chat_log", mock_system_repo)
            assert excinfo.value.details["error_code"] == ErrorCodes.PARSING_FAILED.value

    @pytest.mark.asyncio
    async def test_normalize_chat_end_to_end(self, mock_system_repo: AsyncMock) -> None:
        """Verify normalize_chat returns a valid ProcessedChatDTO."""
        raw = "User: Question\nAssistant: Answer"
        result = await ChatNormalizerService.normalize_chat(raw, "chat_log", mock_system_repo)
        assert isinstance(result, ProcessedChatDTO)
        assert "Question" in result.user_only
        assert "Answer" in result.ai_only
        assert "<user_payload>" in result.combined

    def test_processed_chat_dto_missing_required_field_raises(self) -> None:
        """Negative: Missing required fields in ProcessedChatDTO raises ValidationError."""
        with pytest.raises(ValidationError):
            ProcessedChatDTO.model_validate({"combined": "text", "user_only": "text"})

    def test_processed_chat_dto_extra_field_forbidden(self) -> None:
        """Negative: Extra fields in ProcessedChatDTO are strictly forbidden."""
        with pytest.raises(ValidationError):
            ProcessedChatDTO.model_validate({
                "combined": "text",
                "user_only": "text",
                "ai_only": "text",
                "extra_field": "invalid",
            })

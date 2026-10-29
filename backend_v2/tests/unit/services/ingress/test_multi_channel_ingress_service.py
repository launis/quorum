"""Unit tests for MultiChannelIngressService.

Validates multi-channel routing across PDF vector geometry, structured JSON,
fast-path colon regex, deterministic fluff stripping, and LLM anchor slicing fallback.
"""

from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import fitz
import pymupdf4llm
import pytest
from fastapi import status

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.system_config import ChatHistoryDTO, ChatMessageDTO
from backend_v2.services.ingress.multi_channel_ingress_service import MultiChannelIngressService
from backend_v2.tests.fakes.in_memory_repositories import InMemorySystemRepository


@pytest.fixture
def mock_system_repo() -> InMemorySystemRepository:
    """Provide an isolated in-memory repository implementing ISystemRepository."""
    return InMemorySystemRepository()


class TestMultiChannelIngressService:
    """Test suite for MultiChannelIngressService."""

    @pytest.mark.asyncio
    async def test_process_chat_empty_string_fails_fast(self, mock_system_repo: InMemorySystemRepository) -> None:
        """Negative: Empty string triggers immediate AppException with EMPTY_INPUT."""
        service = MultiChannelIngressService()
        with pytest.raises(AppException) as excinfo:
            await service.process_chat("", mock_system_repo, key="chat_log")

        assert excinfo.value.details["error_code"] == ErrorCodes.EMPTY_INPUT.value

    @pytest.mark.asyncio
    async def test_process_chat_none_input_fails_fast(self, mock_system_repo: InMemorySystemRepository) -> None:
        """Negative: None input triggers immediate AppException with EMPTY_INPUT."""
        service = MultiChannelIngressService()
        with pytest.raises(AppException) as excinfo:
            await service.process_chat(None, mock_system_repo, key="chat_log")

        assert excinfo.value.details["error_code"] == ErrorCodes.EMPTY_INPUT.value

    @pytest.mark.asyncio
    async def test_process_chat_empty_bytes_fails_fast(self, mock_system_repo: InMemorySystemRepository) -> None:
        """Negative: Empty byte payload triggers immediate AppException with EMPTY_INPUT."""
        service = MultiChannelIngressService()
        with pytest.raises(AppException) as excinfo:
            await service.process_chat(b"   \n  ", mock_system_repo, key="chat_log")

        assert excinfo.value.details["error_code"] == ErrorCodes.EMPTY_INPUT.value

    @pytest.mark.asyncio
    async def test_process_chat_invalid_bytes_encoding_fails_fast(
        self, mock_system_repo: InMemorySystemRepository
    ) -> None:
        """Negative: Corrupt non-PDF bytes that cannot be decoded as UTF-8 trigger VALIDATION_FAILED."""
        service = MultiChannelIngressService()
        corrupt_bytes = b"\xff\xfe\x00\x00\x80"
        with pytest.raises(AppException) as excinfo:
            await service.process_chat(corrupt_bytes, mock_system_repo, key="chat_log")

        assert excinfo.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    @pytest.mark.asyncio
    async def test_process_chat_llm_parser_app_exception_passthrough(
        self, mock_system_repo: InMemorySystemRepository
    ) -> None:
        """Negative: AppException raised by ChatParserService propagates directly without re-wrapping."""
        mock_parser = MagicMock()
        expected_exc = AppException(
            message="Model configuration missing",
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value, "input_key": "chat_log"},
        )
        mock_parser.parse_pasted_chat = AsyncMock(side_effect=expected_exc)

        service = MultiChannelIngressService(parser_service=mock_parser)
        with pytest.raises(AppException) as excinfo:
            await service.process_chat("Unstructured prose without colons", mock_system_repo, key="chat_log")

        assert excinfo.value is expected_exc
        assert excinfo.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value

    @pytest.mark.asyncio
    async def test_process_chat_llm_parser_unexpected_exception_wraps_parsing_failed(
        self, mock_system_repo: InMemorySystemRepository
    ) -> None:
        """Negative: Unexpected runtime error in ChatParserService wraps into AppException(PARSING_FAILED)."""
        mock_parser = MagicMock()
        mock_parser.parse_pasted_chat = AsyncMock(side_effect=RuntimeError("Unexpected tokenizer crash"))

        service = MultiChannelIngressService(parser_service=mock_parser)
        with pytest.raises(AppException) as excinfo:
            await service.process_chat("Unstructured prose without colons", mock_system_repo, key="chat_log")

        assert excinfo.value.status_code == status.HTTP_400_BAD_REQUEST
        assert excinfo.value.details["error_code"] == ErrorCodes.PARSING_FAILED.value
        assert excinfo.value.details["input_key"] == "chat_log"

    @pytest.mark.asyncio
    async def test_process_chat_structured_json_channel(self, mock_system_repo: InMemorySystemRepository) -> None:
        """Verify structured JSON channel deserializes directly without regex or LLM fallback."""
        service = MultiChannelIngressService()
        payload = json.dumps(
            {
                "conversation": [
                    {"role": "user", "content": "Question"},
                    {"role": "ai", "content": "Answer"},
                ]
            }
        )
        result = await service.process_chat(payload, mock_system_repo, key="chat_log")
        assert len(result.conversation) == 2
        assert result.conversation[0].role == "user"
        assert result.conversation[0].content == "Question"

    @pytest.mark.asyncio
    async def test_process_chat_fast_path_regex_channel(self, mock_system_repo: InMemorySystemRepository) -> None:
        """Verify fast-path regex channel parses standard colon dialogues deterministically."""
        service = MultiChannelIngressService()
        raw = "User: What is GDP?\nAssistant: GDP measures economic output."
        result = await service.process_chat(raw, mock_system_repo, key="chat_log")
        assert len(result.conversation) == 2
        assert result.conversation[0].role == "user"
        assert result.conversation[1].content == "GDP measures economic output."

    @pytest.mark.asyncio
    async def test_process_chat_fluff_stripping_and_llm_fallback(
        self, mock_system_repo: InMemorySystemRepository
    ) -> None:
        """Verify fluff stripping cleans browser copy-paste and falls back to LLM anchor parser."""
        mock_parser = MagicMock()
        mock_dto = ChatHistoryDTO(
            conversation=[
                ChatMessageDTO(role="user", content="Explain quantum computing"),
                ChatMessageDTO(role="ai", content="Quantum computing uses qubits"),
            ]
        )
        mock_parser.parse_pasted_chat = AsyncMock(return_value=mock_dto)

        service = MultiChannelIngressService(parser_service=mock_parser)
        raw = (
            "ChatGPT 4o\n"
            "Explain quantum computing\n"
            "Copy code\n"
            "Quantum computing uses qubits\n"
            "ChatGPT can make mistakes. Check important info.\n"
        )
        result = await service.process_chat(raw, mock_system_repo, key="chat_log")
        assert len(result.conversation) == 2
        mock_parser.parse_pasted_chat.assert_called_once()
        call_args = mock_parser.parse_pasted_chat.call_args[0]
        cleaned_text = call_args[0]
        assert "ChatGPT 4o" not in cleaned_text
        assert "Copy code" not in cleaned_text
        assert "ChatGPT can make mistakes" not in cleaned_text

    @pytest.mark.asyncio
    async def test_process_chat_pdf_conversation_channel(self, mock_system_repo: InMemorySystemRepository) -> None:
        """Verify PDF bytes with speech bubble drawings route directly to PdfChatExtractorService."""
        mock_pdf_extractor = MagicMock()
        mock_dto = ChatHistoryDTO(
            conversation=[
                ChatMessageDTO(role="user", content="PDF prompt"),
                ChatMessageDTO(role="ai", content="PDF response"),
            ]
        )
        mock_pdf_extractor.is_conversation_pdf.return_value = True
        mock_pdf_extractor.extract_conversation.return_value = mock_dto

        service = MultiChannelIngressService(pdf_extractor=mock_pdf_extractor)

        doc = fitz.open()
        doc.new_page()
        pdf_bytes = doc.tobytes()
        doc.close()

        result = await service.process_chat(pdf_bytes, mock_system_repo, key="chat_log", filename="chat.pdf")
        assert result == mock_dto
        mock_pdf_extractor.is_conversation_pdf.assert_called_once()
        mock_pdf_extractor.extract_conversation.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_chat_pdf_prose_fallback_channel(self, mock_system_repo: InMemorySystemRepository) -> None:
        """Verify non-conversation PDF bytes extract markdown and parse via fast path or LLM."""
        mock_pdf_extractor = MagicMock()
        mock_pdf_extractor.is_conversation_pdf.return_value = False
        mock_parser = MagicMock()
        mock_dto = ChatHistoryDTO(
            conversation=[
                ChatMessageDTO(role="user", content="Question from doc"),
                ChatMessageDTO(role="ai", content="Answer from doc"),
            ]
        )
        mock_parser.parse_pasted_chat = AsyncMock(return_value=mock_dto)

        service = MultiChannelIngressService(
            pdf_extractor=mock_pdf_extractor,
            parser_service=mock_parser,
        )

        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 100), "User: Question from doc\nAssistant: Answer from doc")
        pdf_bytes = doc.tobytes()
        doc.close()

        result = await service.process_chat(pdf_bytes, mock_system_repo, key="chat_log")
        assert len(result.conversation) >= 2
        assert any(t.role == "user" for t in result.conversation)
        assert any(t.role == "ai" for t in result.conversation)

    @pytest.mark.asyncio
    async def test_extract_pdf_channel_sync_picture_placeholder_falls_back_to_plain_text(
        self, mock_system_repo: InMemorySystemRepository
    ) -> None:
        """Verify PDF extraction falls back to plain page text when pymupdf4llm emits picture placeholders."""
        mock_pdf_extractor = MagicMock()
        mock_pdf_extractor.is_conversation_pdf.return_value = False

        service = MultiChannelIngressService(pdf_extractor=mock_pdf_extractor)

        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 100), "User: Fallback plain text question\nAssistant: Fallback plain text answer")
        pdf_bytes = doc.tobytes()
        doc.close()

        with patch.object(pymupdf4llm, "to_markdown", return_value="<!-- Start of picture text -->"):
            result = await service.process_chat(pdf_bytes, mock_system_repo, key="chat_log")

        assert len(result.conversation) == 2
        assert result.conversation[0].role == "user"
        assert "Fallback plain text question" in result.conversation[0].content

    @pytest.mark.asyncio
    async def test_process_chat_pdf_offloaded_to_thread(self, mock_system_repo: InMemorySystemRepository) -> None:
        """Verify that _extract_pdf_channel_sync is offloaded via asyncio.to_thread."""
        mock_pdf_extractor = MagicMock()
        mock_dto = ChatHistoryDTO(conversation=[ChatMessageDTO(role="user", content="Threaded turn")])
        service = MultiChannelIngressService(pdf_extractor=mock_pdf_extractor)

        doc = fitz.open()
        doc.new_page()
        pdf_bytes = doc.tobytes()
        doc.close()

        with patch(
            "backend_v2.services.ingress.multi_channel_ingress_service.asyncio.to_thread",
            wraps=asyncio.to_thread,
        ) as spy_to_thread:
            with patch.object(service, "_extract_pdf_channel_sync", return_value=mock_dto) as mock_sync_extract:
                result = await service.process_chat(pdf_bytes, mock_system_repo, key="chat_log")

                assert result == mock_dto
                spy_to_thread.assert_called_once()
                mock_sync_extract.assert_called_once_with(
                    pdf_bytes=pdf_bytes,
                    pdf_extractor=mock_pdf_extractor,
                    key="chat_log",
                    filename=None,
                )

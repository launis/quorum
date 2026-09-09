"""Unit tests for MultiChannelIngressService.

Validates multi-channel routing across PDF vector geometry, structured JSON,
fast-path colon regex, deterministic fluff stripping, and LLM anchor slicing fallback.
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.v2_core import ChatHistoryDTO, ChatMessageDTO
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
            await service.process_chat(None, mock_system_repo, key="chat_log")  # type: ignore[arg-type]

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
    async def test_process_chat_structured_json_channel(
        self, mock_system_repo: InMemorySystemRepository
    ) -> None:
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
    async def test_process_chat_fast_path_regex_channel(
        self, mock_system_repo: InMemorySystemRepository
    ) -> None:
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
    async def test_process_chat_pdf_conversation_channel(
        self, mock_system_repo: InMemorySystemRepository
    ) -> None:
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

        import fitz

        # Create minimal PDF bytes in memory
        doc = fitz.open()
        doc.new_page()
        pdf_bytes = doc.tobytes()
        doc.close()

        result = await service.process_chat(pdf_bytes, mock_system_repo, key="chat_log", filename="chat.pdf")
        assert result == mock_dto
        mock_pdf_extractor.is_conversation_pdf.assert_called_once()
        mock_pdf_extractor.extract_conversation.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_chat_pdf_prose_fallback_channel(
        self, mock_system_repo: InMemorySystemRepository
    ) -> None:
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

        import fitz

        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 100), "User: Question from doc\nAssistant: Answer from doc")
        pdf_bytes = doc.tobytes()
        doc.close()

        result = await service.process_chat(pdf_bytes, mock_system_repo, key="chat_log")
        assert len(result.conversation) >= 2
        assert any(t.role == "user" for t in result.conversation)
        assert any(t.role == "ai" for t in result.conversation)

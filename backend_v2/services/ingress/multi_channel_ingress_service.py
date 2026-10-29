"""Multi-Channel Ingress Service for unified chat transcript ingestion.

Dispatches conversational input across deterministic channels:
- Channel 1: PDF Vector Geometry & Bubble Extraction (PdfChatExtractorService)
- Channel 2: Clipboard & Text Ingress (Fluff Stripping + Fast-Path Regex + LLM Anchor Slicing)
"""

from __future__ import annotations

import asyncio
import logging

import fitz
from fastapi import status

from backend_v2.database.interfaces import ISystemRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.system_config import ChatHistoryDTO
from backend_v2.models.enums import LLMProvider
from backend_v2.services.chat_normalizer import ChatNormalizerService
from backend_v2.services.chat_parser import ChatParserService
from backend_v2.services.ingress.pdf_extractor import PdfChatExtractorService

logger = logging.getLogger(__name__)

__all__ = ["MultiChannelIngressService"]


class MultiChannelIngressService:
    """Unified deterministic chat ingress dispatcher across multi-model channels.

    Routes raw inputs through PDF geometry extraction, deterministic UI fluff stripping,
    fast-path regex parsing, or lightweight LLM anchor-based boundary slicing.
    """

    def __init__(
        self,
        parser_service: type[ChatParserService] | ChatParserService = ChatParserService,
        normalizer_service: type[ChatNormalizerService] | ChatNormalizerService = ChatNormalizerService,
        pdf_extractor: type[PdfChatExtractorService] | PdfChatExtractorService = PdfChatExtractorService,
    ) -> None:
        """Initialize MultiChannelIngressService with injected component services.

        Args:
            parser_service: Chat parser service for LLM anchor slicing fallback.
            normalizer_service: Chat normalizer service for cleaning and regex fast path.
            pdf_extractor: PDF chat extractor service for vector geometry bubble extraction.
        """
        self._parser = parser_service
        self._normalizer = normalizer_service
        self._pdf_extractor = pdf_extractor

    @staticmethod
    def _extract_pdf_channel_sync(
        pdf_bytes: bytes,
        pdf_extractor: type[PdfChatExtractorService] | PdfChatExtractorService,
        key: str,
        filename: str | None,
    ) -> ChatHistoryDTO | str:
        """Isolated CPU-bound PDF vector geometry and text extraction in background thread.

        Args:
            pdf_bytes: Raw binary bytes of the PDF document.
            pdf_extractor: Extractor instance or type for conversation bubbles.
            key: Input key identifier.
            filename: Optional source filename.

        Returns:
            ChatHistoryDTO if speech bubble conversation is detected, or extracted markdown string.
        """
        logger.info("[MultiChannelIngress] PDF magic bytes detected for %s (filename: %s)", key, filename)
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        try:
            if pdf_extractor.is_conversation_pdf(doc):
                logger.info("[MultiChannelIngress] Detected conversation speech bubbles in PDF for %s", key)
                return pdf_extractor.extract_conversation(doc)
            logger.info(
                "[MultiChannelIngress] PDF is not a speech bubble conversation; extracting markdown prose for %s",
                key,
            )
            import pymupdf4llm

            try:
                md_text = str(pymupdf4llm.to_markdown(doc))
            finally:
                pymupdf4llm.use_layout(False)

            if not md_text or not md_text.strip() or "<!-- Start of picture text -->" in md_text:
                plain_pages = [page.get_text("text") for page in doc]
                plain_text = "\n\n".join(plain_pages).strip()
                if plain_text:
                    md_text = plain_text

            return md_text
        finally:
            doc.close()

    async def _decode_or_extract_input(
        self,
        raw_input: str | bytes | None,
        key: str,
        filename: str | None,
    ) -> ChatHistoryDTO | str:
        """Validate, decode, or extract PDF content from raw conversational input.

        Args:
            raw_input: Raw text string or raw file bytes.
            key: Input key identifier.
            filename: Optional source filename to assist in routing or logging.

        Returns:
            ChatHistoryDTO if PDF speech bubbles were directly extracted, otherwise normalized raw text string.

        Raises:
            AppException: With ErrorCodes.EMPTY_INPUT if input is None or whitespace-only, or
                ErrorCodes.VALIDATION_FAILED if raw bytes fail UTF-8 decoding.
        """
        if raw_input is None:
            logger.error(
                "Null input received for chat key.",
                extra={"error_code": ErrorCodes.EMPTY_INPUT.name, "input_key": key},
            )
            raise AppException(
                message=f"Empty input received for {key}.",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.EMPTY_INPUT.value, "input_key": key},
            )

        if isinstance(raw_input, bytes) and raw_input.startswith(b"%PDF"):
            pdf_result = await asyncio.to_thread(
                self._extract_pdf_channel_sync,
                pdf_bytes=raw_input,
                pdf_extractor=self._pdf_extractor,
                key=key,
                filename=filename,
            )
            if isinstance(pdf_result, ChatHistoryDTO):
                return pdf_result
            raw_text = pdf_result
        elif isinstance(raw_input, bytes):
            try:
                raw_text = raw_input.decode("utf-8")
            except UnicodeDecodeError as e:
                logger.error(
                    "[MultiChannelIngress] Failed to decode raw bytes as UTF-8 for %s: %s",
                    key,
                    e,
                    exc_info=True,
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "input_key": key},
                )
                raise AppException(
                    message=f"Invalid byte encoding for {key}: expected UTF-8 text.",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "input_key": key},
                ) from e
        else:
            raw_text = raw_input

        if not raw_text or not raw_text.strip(" \t\r\n"):
            logger.error(
                "Empty input received for chat key.",
                extra={"error_code": ErrorCodes.EMPTY_INPUT.name, "input_key": key},
            )
            raise AppException(
                message=f"Empty input received for {key}.",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.EMPTY_INPUT.value, "input_key": key},
            )

        return raw_text

    async def process_chat(
        self,
        raw_input: str | bytes | None,
        system_repo: ISystemRepository,
        key: str = "chat_log",
        filename: str | None = None,
        registry_id: str | None = None,
        provider: LLMProvider | None = None,
    ) -> ChatHistoryDTO:
        """Dispatch and parse raw conversational input into ChatHistoryDTO.

        Args:
            raw_input: Raw text string or raw file bytes.
            system_repo: System repository for LLM model garden resolution.
            key: Input key identifier (e.g. 'chat_log').
            filename: Optional source filename to assist in routing or logging.
            registry_id: Optional authoritative model registry ID.
            provider: Optional explicit provider override.

        Returns:
            ChatHistoryDTO containing validated dialogue turns.

        Raises:
            AppException: With ErrorCodes.EMPTY_INPUT if input is empty,
                ErrorCodes.VALIDATION_FAILED if byte decoding fails, or
                ErrorCodes.PARSING_FAILED if LLM dialogue parsing fails.
        """
        # 1. Binary / PDF Vector Geometry & Text Decoding Channel
        resolved_input = await self._decode_or_extract_input(
            raw_input=raw_input,
            key=key,
            filename=filename,
        )
        if isinstance(resolved_input, ChatHistoryDTO):
            return resolved_input
        raw_text = resolved_input

        # 2. Structured JSON Channel (handles pre-extracted JSON or direct JSON submissions)
        chat_dto = self._normalizer.try_parse_json(raw_text)
        if chat_dto and chat_dto.conversation:
            logger.info("[MultiChannelIngress] Successfully parsed structured JSON chat for %s", key)
            return chat_dto

        # 3. Deterministic UI Fluff Stripping
        cleaned_text = self._normalizer.strip_known_ui_fluff(raw_text)

        # 4. Deterministic Fast-Path Colon Regex
        chat_dto = self._normalizer.try_parse_fast_path(cleaned_text)
        if chat_dto and chat_dto.conversation:
            logger.info("[MultiChannelIngress] Successfully parsed fast-path regex chat for %s", key)
            return chat_dto

        # 5. LLM Anchor-Based Slicing Fallback
        logger.info("[MultiChannelIngress] Delegating to LLM Anchor Slicing for %s", key)
        try:
            return await self._parser.parse_pasted_chat(
                cleaned_text,
                system_repo=system_repo,
                registry_id=registry_id,
                provider=provider,
            )
        except AppException:
            raise
        except Exception as e:
            logger.error(
                "LLM chat parser failed for %s: %s",
                key,
                e,
                exc_info=True,
                extra={"error_code": ErrorCodes.PARSING_FAILED.name, "input_key": key},
            )
            raise AppException(
                message=f"Failed to parse dialogue conversation for {key}: {e}",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.PARSING_FAILED.value, "input_key": key},
            ) from e

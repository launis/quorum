"""Multi-Channel Ingress Service for unified chat transcript ingestion.

Dispatches conversational input across deterministic channels:
- Channel 1: PDF Vector Geometry & Bubble Extraction (PdfChatExtractorService)
- Channel 2: Clipboard & Text Ingress (Fluff Stripping + Fast-Path Regex + LLM Anchor Slicing)
"""

from __future__ import annotations

import logging

import fitz
import pymupdf4llm
from fastapi import status

from backend_v2.database.interfaces import ISystemRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.v2_core import ChatHistoryDTO
from backend_v2.services.chat_normalizer import ChatNormalizerService
from backend_v2.services.chat_parser import ChatParserService
from backend_v2.services.ingress.pdf_chat_extractor import PdfChatExtractorService

logger = logging.getLogger(__name__)


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

    async def process_chat(
        self,
        raw_input: str | bytes,
        system_repo: ISystemRepository,
        key: str = "chat_log",
        filename: str | None = None,
    ) -> ChatHistoryDTO:
        """Dispatch and parse raw conversational input into ChatHistoryDTO.

        Args:
            raw_input: Raw text string or raw file bytes.
            system_repo: System repository for LLM model garden resolution.
            key: Input key identifier (e.g. 'chat_log').
            filename: Optional source filename to assist in routing or logging.

        Returns:
            ChatHistoryDTO containing validated dialogue turns.

        Raises:
            AppException: If input is empty, malformed, or dialogue parsing fails.
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

        # 1. PDF Vector Geometry Channel
        if isinstance(raw_input, bytes) and raw_input.startswith(b"%PDF"):
            logger.info("[MultiChannelIngress] PDF magic bytes detected for %s (filename: %s)", key, filename)
            doc = fitz.open(stream=raw_input, filetype="pdf")
            try:
                if self._pdf_extractor.is_conversation_pdf(doc):
                    logger.info("[MultiChannelIngress] Detected conversation speech bubbles in PDF for %s", key)
                    return self._pdf_extractor.extract_conversation(doc)
                logger.info(
                    "[MultiChannelIngress] PDF is not a speech bubble conversation; extracting markdown prose for %s",
                    key,
                )
                raw_text = str(pymupdf4llm.to_markdown(doc))
            finally:
                doc.close()
        elif isinstance(raw_input, bytes):
            try:
                raw_text = raw_input.decode("utf-8")
            except UnicodeDecodeError as e:
                logger.error("[MultiChannelIngress] Failed to decode raw bytes as UTF-8: %s", e)
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
            return await self._parser.parse_pasted_chat(cleaned_text, system_repo=system_repo)
        except AppException:
            raise
        except Exception as e:
            logger.error(
                "LLM chat parser failed for %s: %s",
                key,
                e,
                extra={"error_code": ErrorCodes.PARSING_FAILED.name, "input_key": key},
            )
            raise AppException(
                message=f"Failed to parse dialogue conversation for {key}: {e}",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.PARSING_FAILED.value, "input_key": key},
            ) from e

"""PDF conversational geometry and speech bubble extraction service.

Provides deterministic extraction of multi-turn dialogues from browser print
PDFs (Chrome Ctrl+P / Skia) and native platform exports (Google Gemini, ChatGPT)
using vector drawings and layout-aware text aggregation without LLM calls.
"""

from __future__ import annotations

from collections.abc import Mapping

import fitz

from backend_v2.models.domain.system_config import ChatHistoryDTO
from backend_v2.models.dtos.ingress import PdfBlockSignatureDTO as PdfBlockSignatureDTO
from backend_v2.models.dtos.ingress import PdfCellCoordinatesDTO as PdfCellCoordinatesDTO
from backend_v2.models.dtos.ingress import PdfTextBlockDTO as PdfTextBlockDTO
from backend_v2.models.dtos.ingress import RawTurnDTO as RawTurnDTO
from backend_v2.services.ingress.pdf_extractor.bubble_geometry import DrawingItemValue as DrawingItemValue
from backend_v2.services.ingress.pdf_extractor.bubble_geometry import (
    dlq_log_extraction_error,
    extract_page_user_bubbles,
    get_page_table_rects,
    is_user_bubble_drawing,
)
from backend_v2.services.ingress.pdf_extractor.bubble_geometry import (
    is_conversation_pdf as _is_conversation_pdf_stage,
)
from backend_v2.services.ingress.pdf_extractor.table_and_card_stage import (
    detect_attachment_cards,
    filter_table_text_blocks,
    reconstruct_tables_as_markdown,
)
from backend_v2.services.ingress.pdf_extractor.turn_assembly_stage import (
    check_truncation,
    extract_conversation_from_doc,
    sort_blocks_visual_order,
)

__all__ = [
    "DrawingItemValue",
    "PdfBlockSignatureDTO",
    "PdfCellCoordinatesDTO",
    "PdfChatExtractorService",
    "PdfTextBlockDTO",
    "RawTurnDTO",
]


class PdfChatExtractorService:
    """Deterministic extractor for browser-printed and exported chat PDFs."""

    # Phase 1, Step 3: Delegate bubble geometry methods to bubble_geometry stage module
    @staticmethod
    def _is_user_bubble_drawing(
        d: Mapping[str, DrawingItemValue],
        page_width: float,
        page_height: float,
        table_rects: list[fitz.Rect] | None = None,
    ) -> bool:
        """Determines if a vector drawing represents a user prompt bubble using relative geometry.

        Note:
            d is an External PyMuPDF API boundary dict from page.get_drawings().
        """
        return is_user_bubble_drawing(d, page_width, page_height, table_rects)

    @staticmethod
    def _dlq_log_extraction_error(context: str, exc: Exception) -> None:
        """Routes non-fatal PDF table extraction exceptions to dead-letter diagnostic logs."""
        dlq_log_extraction_error(context, exc)

    @staticmethod
    def _get_page_table_rects(page: fitz.Page) -> list[fitz.Rect]:
        """Extracts valid table bounding boxes, guarding against outer page containers."""
        return get_page_table_rects(page)

    @staticmethod
    def is_conversation_pdf(doc: fitz.Document) -> bool:
        """Determines whether a PDF document contains structured chat vector speech bubbles.

        Args:
            doc: Loaded PyMuPDF fitz.Document instance.

        Returns:
            True if conversation bubbles are detected, False otherwise.
        """
        return _is_conversation_pdf_stage(doc)

    @staticmethod
    def _extract_page_user_bubbles(page: fitz.Page) -> list[fitz.Rect]:
        """Extracts sanitized user speech bubble rectangles on a page."""
        return extract_page_user_bubbles(page)

    # Phase 3, Step 2: Delegate turn assembly and truncation methods to turn_assembly_stage module
    @staticmethod
    def _check_truncation(text: str) -> None:
        """Checks for ChatGPT overflow buttons outside code fences and raises actionable warning."""
        check_truncation(text)

    @staticmethod
    def _sort_blocks_visual_order(page_blocks: list[PdfTextBlockDTO]) -> list[PdfTextBlockDTO]:
        """Sorts blocks topologically in visual reading order."""
        return sort_blocks_visual_order(page_blocks)

    # Phase 2, Step 2: Delegate table and attachment card stage methods to table_and_card_stage module
    @staticmethod
    def _filter_table_text_blocks(
        page_blocks: list[PdfTextBlockDTO],
        table_rects: list[fitz.Rect],
    ) -> list[PdfTextBlockDTO]:
        """Suppresses raw text blocks that intersect identified table bounding boxes."""
        return filter_table_text_blocks(page_blocks, table_rects)

    @staticmethod
    def _reconstruct_tables_as_markdown(page: fitz.Page, table_rects: list[fitz.Rect]) -> list[tuple[fitz.Rect, str]]:
        """Extracts tables from a page and formats them as Markdown pipe tables."""
        return reconstruct_tables_as_markdown(page, table_rects)

    @staticmethod
    def _detect_attachment_cards(page: fitz.Page) -> list[tuple[fitz.Rect, str]]:
        """Detects 76x76 pt file attachment cards and normalizes them to [Liite: <filename>]."""
        return detect_attachment_cards(page)

    @staticmethod
    def extract_conversation(doc: fitz.Document) -> ChatHistoryDTO:
        """Extracts and segregates conversational turns from a PDF document.

        Args:
            doc: Open PyMuPDF Document instance.

        Returns:
            ChatHistoryDTO containing the ordered chronological conversation.

        Raises:
            AppException: If doc is empty/corrupt or truncation artifacts are detected (ErrorCodes.VALIDATION_FAILED).
        """
        return extract_conversation_from_doc(doc)

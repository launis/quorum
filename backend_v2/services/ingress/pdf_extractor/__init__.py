"""PDF conversational geometry and speech bubble extraction package facade.

Provides deterministic extraction of multi-turn dialogues from browser print
PDFs (Chrome Ctrl+P / Skia) and native platform exports (Google Gemini, ChatGPT)
using vector drawings and layout-aware text aggregation without LLM calls.
"""

from __future__ import annotations

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

    _is_user_bubble_drawing = staticmethod(is_user_bubble_drawing)
    _dlq_log_extraction_error = staticmethod(dlq_log_extraction_error)
    _get_page_table_rects = staticmethod(get_page_table_rects)
    is_conversation_pdf = staticmethod(_is_conversation_pdf_stage)
    _extract_page_user_bubbles = staticmethod(extract_page_user_bubbles)
    _check_truncation = staticmethod(check_truncation)
    _sort_blocks_visual_order = staticmethod(sort_blocks_visual_order)
    _filter_table_text_blocks = staticmethod(filter_table_text_blocks)
    _reconstruct_tables_as_markdown = staticmethod(reconstruct_tables_as_markdown)
    _detect_attachment_cards = staticmethod(detect_attachment_cards)
    extract_conversation = staticmethod(extract_conversation_from_doc)

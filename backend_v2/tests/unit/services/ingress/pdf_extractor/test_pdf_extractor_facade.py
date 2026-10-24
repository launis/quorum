"""Unit tests for PdfChatExtractorService package facade delegation and contract parity.

Verifies static method delegation across bubble geometry, table/attachment card stages,
and turn assembly stages, as well as negative Fail-Fast boundaries.
"""

from __future__ import annotations

import fitz
import pytest

from backend_v2.exceptions import AppException
from backend_v2.services.ingress.pdf_extractor import (
    PdfBlockSignatureDTO,
    PdfCellCoordinatesDTO,
    PdfChatExtractorService,
    PdfTextBlockDTO,
    RawTurnDTO,
)


# Phase 4, Step 1: Add facade delegation and contract parity tests
def test_pdf_extractor_facade_delegation_happy_path() -> None:
    """Verify PdfChatExtractorService delegates all stage methods accurately."""
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    bubble_rect = fitz.Rect(360, 100, 520, 160)
    page.draw_rect(bubble_rect, color=(0.9, 0.9, 0.9), fill=(0.91, 0.93, 0.96))
    page.insert_text((370, 120), "Käyttäjän kehote")
    page.insert_text((59, 220), "Tekoälyn vastaus")

    try:
        assert PdfChatExtractorService.is_conversation_pdf(doc) is True
        bubbles = PdfChatExtractorService._extract_page_user_bubbles(page)
        assert len(bubbles) == 1
        table_rects = PdfChatExtractorService._get_page_table_rects(page)
        assert table_rects == []
        assert PdfChatExtractorService._reconstruct_tables_as_markdown(page, table_rects) == []
        assert PdfChatExtractorService._detect_attachment_cards(page) == []

        drawing = {"rect": bubble_rect, "fill": (0.91, 0.93, 0.96)}
        assert PdfChatExtractorService._is_user_bubble_drawing(drawing, 595.0, 842.0) is True
        PdfChatExtractorService._dlq_log_extraction_error("facade_test", ValueError("minor"))
        PdfChatExtractorService._check_truncation("Valid non-truncated prompt")

        b1 = PdfTextBlockDTO(x0=59.0, y0=220.0, x1=200.0, y1=240.0, text="B", block_no=1, block_type=0)
        b2 = PdfTextBlockDTO(x0=370.0, y0=120.0, x1=500.0, y1=140.0, text="A", block_no=0, block_type=0)
        sorted_blocks = PdfChatExtractorService._sort_blocks_visual_order([b1, b2])
        assert sorted_blocks[0].text == "A"
        assert PdfChatExtractorService._filter_table_text_blocks([b1, b2], []) == [b1, b2]

        chat_dto = PdfChatExtractorService.extract_conversation(doc)
        assert len(chat_dto.conversation) == 2
    finally:
        doc.close()


def test_pdf_extractor_facade_empty_doc_raises_422() -> None:
    """Verify PdfChatExtractorService.extract_conversation fails fast on empty 0-page PDF."""
    doc = fitz.open()
    try:
        assert PdfChatExtractorService.is_conversation_pdf(doc) is False
        with pytest.raises(AppException) as exc_info:
            PdfChatExtractorService.extract_conversation(doc)
        assert exc_info.value.status_code == 422
    finally:
        doc.close()


def test_pdf_extractor_facade_truncation_raises_422() -> None:
    """Verify PdfChatExtractorService._check_truncation raises 422 AppException on overflow indicator."""
    with pytest.raises(AppException) as exc_info:
        PdfChatExtractorService._check_truncation("Kehote katkesi... Näytä lisää")
    assert exc_info.value.status_code == 422
    assert exc_info.value.details is not None
    assert exc_info.value.details["truncation_detected"] is True


def test_pdf_extractor_dto_contracts_instantiation() -> None:
    """Verify relocated DTO contracts instantiate cleanly with strict typing."""
    cell = PdfCellCoordinatesDTO(x0=1.0, y0=2.0, x1=3.0, y1=4.0)
    turn = RawTurnDTO(role="user", content="Hello")
    sig = PdfBlockSignatureDTO(page_idx=0, x0=1.0, y0=2.0, x1=3.0, y1=4.0, text="Hello")
    assert cell.x0 == 1.0
    assert turn.role == "user"
    assert sig.page_idx == 0

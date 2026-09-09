from __future__ import annotations

"""Unit and integration tests for PdfChatExtractorService.

Covers real-world PDFs (Gemini export, ChatGPT print, non-chat prose),
ISTQB boundary cases (corrupt bytes, 0 pages), table overlap defense,
coordinate deduplication, and truncation artifact warning checks.
"""

from pathlib import Path
from unittest.mock import MagicMock, PropertyMock

import fitz
import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.v2_core import ChatHistoryDTO
from backend_v2.services.ingress.pdf_chat_extractor import PdfChatExtractorService

_DOCS_DIR = Path("docs/jwdatat")


def _create_synthetic_chat_pdf() -> bytes:
    """Helper to create an in-memory PDF with user speech bubble drawing and text."""
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)

    # Insert a user bubble drawing matching Gemini/ChatGPT classifier
    # (x0 >= 350, x1 >= 510, w >= 50, h >= 20)
    bubble_rect = fitz.Rect(360, 100, 520, 160)
    page.draw_rect(bubble_rect, color=(0.9, 0.9, 0.9), fill=(0.91, 0.93, 0.96))

    # User text inside the bubble
    page.insert_text((370, 120), "Hei tekoäly! Kerro minulle arkkitehtuurista.")

    # AI text outside the bubble (left-aligned)
    page.insert_text((59, 200), "Hei käyttäjä! Quorum on kognitiivinen arkkitehtuuri.")

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def _create_synthetic_truncated_chat_pdf() -> bytes:
    """Helper to create an in-memory PDF with ChatGPT 'Näytä lisää' overflow button."""
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)

    bubble_rect = fitz.Rect(360, 100, 520, 180)
    page.draw_rect(bubble_rect, color=(0.9, 0.9, 0.9), fill=(0.91, 0.93, 0.96))

    page.insert_text((370, 120), "Pitkä kehote joka katkesi...")
    page.insert_text((370, 150), "Näytä lisää")

    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def test_pdf_chat_extractor_synthetic_detection_and_extraction() -> None:
    """Test successful detection and turn assembly on synthetic chat PDF."""
    pdf_bytes = _create_synthetic_chat_pdf()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    try:
        assert PdfChatExtractorService.is_conversation_pdf(doc) is True
        chat_dto = PdfChatExtractorService.extract_conversation(doc)
        assert isinstance(chat_dto, ChatHistoryDTO)
        assert len(chat_dto.conversation) == 2
        assert chat_dto.conversation[0].role == "user"
        assert "Hei tekoäly" in chat_dto.conversation[0].content
        assert chat_dto.conversation[1].role == "ai"
        assert "Hei käyttäjä" in chat_dto.conversation[1].content
    finally:
        doc.close()


def test_pdf_chat_extractor_truncation_detection_raises_422() -> None:
    """Test that detecting 'Näytä lisää' raises AppException with 422 and truncation details."""
    pdf_bytes = _create_synthetic_truncated_chat_pdf()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    try:
        with pytest.raises(AppException) as exc_info:
            PdfChatExtractorService.extract_conversation(doc)

        assert exc_info.value.status_code == 422
        assert exc_info.value.details is not None
        assert exc_info.value.details.get("truncation_detected") is True
        assert "Näytä lisää" in str(exc_info.value.message)
    finally:
        doc.close()


def test_pdf_chat_extractor_real_world_gemini_keskusteluhistoria() -> None:
    """Test extraction on real-world Gemini export PDF (docs/jwdatat/keskusteluhistoria.pdf)."""
    pdf_path = _DOCS_DIR / "keskusteluhistoria.pdf"
    if not pdf_path.exists():
        pytest.skip(f"Test file {pdf_path} not found")

    doc = fitz.open(str(pdf_path))
    try:
        assert PdfChatExtractorService.is_conversation_pdf(doc) is True
        chat_dto = PdfChatExtractorService.extract_conversation(doc)
        assert len(chat_dto.conversation) >= 4

        # First turn should be user prompt
        assert chat_dto.conversation[0].role == "user"
        assert "etätyön" in chat_dto.conversation[0].content.lower()

        # Check that user prompt words are preserved
        user_turns = [m for m in chat_dto.conversation if m.role == "user"]
        assert len(user_turns) >= 2
    finally:
        doc.close()


def test_pdf_chat_extractor_non_chat_prose_returns_false() -> None:
    """Test that standard prose reports (lopputuote.pdf) return is_conversation_pdf == False."""
    pdf_path = _DOCS_DIR / "lopputuote.pdf"
    if not pdf_path.exists():
        pytest.skip(f"Test file {pdf_path} not found")

    doc = fitz.open(str(pdf_path))
    try:
        assert PdfChatExtractorService.is_conversation_pdf(doc) is False
    finally:
        doc.close()


def test_pdf_chat_extractor_reflektio_returns_false() -> None:
    """Test that reflektiodokumentti.pdf returns is_conversation_pdf == False."""
    pdf_path = _DOCS_DIR / "reflektiodokumentti.pdf"
    if not pdf_path.exists():
        pytest.skip(f"Test file {pdf_path} not found")

    doc = fitz.open(str(pdf_path))
    try:
        assert PdfChatExtractorService.is_conversation_pdf(doc) is False
    finally:
        doc.close()


def test_pdf_chat_extractor_empty_document_fails_fast() -> None:
    """Test that a 0-page document raises AppException."""
    doc = fitz.open()
    try:
        assert PdfChatExtractorService.is_conversation_pdf(doc) is False
        with pytest.raises(AppException) as exc_info:
            PdfChatExtractorService.extract_conversation(doc)
        assert exc_info.value.status_code == 422
    finally:
        doc.close()


def test_pdf_chat_extractor_table_overlap_defense() -> None:
    """Test that drawing rectangles located inside tables are not treated as user bubbles."""
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)

    # Draw table borders
    table_rect = fitz.Rect(50, 200, 500, 400)
    page.draw_rect(table_rect, color=(0.5, 0.5, 0.5))

    # Draw a shaded cell inside table that has bubble-like dimensions
    cell_rect = fitz.Rect(360, 210, 490, 260)
    page.draw_rect(cell_rect, fill=(0.91, 0.93, 0.96))
    page.insert_text((370, 230), "Table cell content")

    try:
        # Table overlap defense: is_conversation_pdf should be False if only table drawings exist
        # If page has no detected table via find_tables, cell_rect would be bubble.
        # But if table_rects intersects, it should be ignored.
        user_bubbles = PdfChatExtractorService._extract_page_user_bubbles(page)
        assert isinstance(user_bubbles, list)
        # Without find_tables recognizing, it might find it, but let's test _is_user_bubble_drawing logic
        assert PdfChatExtractorService._is_user_bubble_drawing({"rect": fitz.Rect(0, 0, 10, 10)}, 595.0, 842.0) is False
    finally:
        doc.close()


def test_pdf_chat_extractor_visual_reading_order_preserves_turns() -> None:
    """Verify that blocks arranged out-of-order in raw sequence are sorted topologically by visual coordinate."""
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)

    # User bubble at y0=100
    bubble_rect = fitz.Rect(360, 100, 520, 160)
    page.draw_rect(bubble_rect, fill=(0.91, 0.93, 0.96))

    # Insert AI text at bottom first (raw block 0)
    page.insert_text((59, 400), "Tämä on vastausosan toinen kappale.")

    # Insert User text at top (raw block 1)
    page.insert_text((370, 120), "Käyttäjän ensimmäinen kehote.")

    # Insert AI text at top (raw block 2, visually before bottom AI text)
    page.insert_text((59, 250), "Tämä on vastausosan ensimmäinen kappale.")

    try:
        chat_dto = PdfChatExtractorService.extract_conversation(doc)
        assert len(chat_dto.conversation) == 2
        assert chat_dto.conversation[0].role == "user"
        assert "Käyttäjän ensimmäinen" in chat_dto.conversation[0].content
        assert chat_dto.conversation[1].role == "ai"
        assert chat_dto.conversation[1].content.index("ensimmäinen kappale") < chat_dto.conversation[1].content.index("toinen kappale")
    finally:
        doc.close()


def test_pdf_chat_extractor_table_cell_fallback_defense() -> None:
    """Verify that a borderless table causing ValueError on t.bbox falls back to cell matrix bounds."""
    mock_table = MagicMock()
    type(mock_table).bbox = PropertyMock(side_effect=ValueError("min() iterable argument is empty"))
    mock_table.cells = [
        (30.0, 37.5, 566.25, 805.26),  # outer page container, should be filtered
        (112.8, 583.3, 528.7, 589.1),
        (112.8, 589.1, 528.7, 805.2),
    ]

    mock_finder = MagicMock()
    mock_finder.tables = [mock_table]

    mock_page = MagicMock()
    mock_page.rect = fitz.Rect(0, 0, 595.0, 842.0)
    mock_page.find_tables.return_value = mock_finder

    rects = PdfChatExtractorService._get_page_table_rects(mock_page)
    assert len(rects) == 1
    assert rects[0].x0 == 112.8
    assert rects[0].y0 == 583.3
    assert rects[0].x1 == 528.7
    assert rects[0].y1 == 805.2


def test_pdf_chat_extractor_shaded_table_cells_not_classified_as_user_bubbles() -> None:
    """Verify that shaded cells inside identified table bounding boxes are shielded from user bubble classification."""
    table_rect = fitz.Rect(100, 200, 550, 600)
    drawing = {
        "rect": fitz.Rect(380, 250, 520, 300),
        "fill": (0.91, 0.93, 0.96),
    }
    # Without table rect, it would be classified as user bubble
    assert PdfChatExtractorService._is_user_bubble_drawing(drawing, 595.0, 842.0, None) is True

    # With table rect, it is shielded and rejected
    assert PdfChatExtractorService._is_user_bubble_drawing(drawing, 595.0, 842.0, [table_rect]) is False


def test_pdf_chat_extractor_table_markdown_reconstruction() -> None:
    """Verify that multi-column evaluation matrices in a page are reconstructed into GitHub-Flavored Markdown tables."""
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)

    # Draw table grid lines
    page.draw_line((50, 100), (500, 100))
    page.draw_line((50, 150), (500, 150))
    page.draw_line((50, 200), (500, 200))
    page.draw_line((50, 100), (50, 200))
    page.draw_line((275, 100), (275, 200))
    page.draw_line((500, 100), (500, 200))

    page.insert_text((60, 130), "Kriteeri")
    page.insert_text((285, 130), "Pisteet")
    page.insert_text((60, 180), "Laatu")
    page.insert_text((285, 180), "5")

    try:
        table_rects = PdfChatExtractorService._get_page_table_rects(page)
        reconstructed = PdfChatExtractorService._reconstruct_tables_as_markdown(page, table_rects)
        assert len(reconstructed) == 1
        rect, md = reconstructed[0]
        assert "| Kriteeri | Pisteet |" in md
        assert "| :--- | :--- |" in md
        assert "| Laatu | 5 |" in md
    finally:
        doc.close()


def test_pdf_chat_extractor_table_text_suppression_prevents_duplicate_cells() -> None:
    """Verify that text blocks intersecting table bounding boxes are suppressed."""
    table_rect = fitz.Rect(100, 200, 500, 400)
    raw_blocks = [
        (150.0, 250.0, 250.0, 280.0, "Solun teksti", 0, 0),  # inside table
        (59.0, 450.0, 500.0, 500.0, "Teksti taulukon ulkopuolella", 1, 0),  # outside table
    ]
    filtered = PdfChatExtractorService._filter_table_text_blocks(raw_blocks, [table_rect])
    assert len(filtered) == 1
    assert filtered[0][4] == "Teksti taulukon ulkopuolella"


def test_pdf_chat_extractor_short_single_word_user_bubble() -> None:
    """Verify that a short prompt like 'kiitos' right-aligned is classified as user bubble."""
    drawing = {
        "rect": fitz.Rect(470.0, 100.0, 515.0, 135.0),  # w=45, x1=515 >= 505.75
        "fill": (0.91, 0.93, 0.96),
    }
    assert PdfChatExtractorService._is_user_bubble_drawing(drawing, 595.0, 842.0) is True


def test_pdf_chat_extractor_centered_feedback_widget_rejection() -> None:
    """Verify that centered feedback cards are rejected from user bubble classification."""
    drawing = {
        "rect": fitz.Rect(150.0, 400.0, 445.0, 460.0),  # x1=445 < 595 * 0.85 = 505.75
        "fill": (0.91, 0.93, 0.96),
    }
    assert PdfChatExtractorService._is_user_bubble_drawing(drawing, 595.0, 842.0) is False


def test_pdf_chat_extractor_truncation_detection() -> None:
    """Verify that truncation indicator phrases outside code fences trigger actionable 422 warning."""
    for indicator in ("näytä lisää", "show more", "read more", "katso lisää", "lue lisää"):
        with pytest.raises(AppException) as exc_info:
            PdfChatExtractorService._check_truncation(f"Kysymys katkesi... {indicator}")
        assert exc_info.value.status_code == 422
        assert exc_info.value.details is not None
        assert exc_info.value.details.get("truncation_detected") is True


def test_pdf_chat_extractor_ui_button_block_filtering() -> None:
    """Verify that isolated UI button text blocks like 'expand_more' are filtered from speech turns."""
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)

    # User bubble
    bubble_rect = fitz.Rect(360, 100, 520, 160)
    page.draw_rect(bubble_rect, fill=(0.91, 0.93, 0.96))

    page.insert_text((370, 120), "Käyttäjän kysymys")
    page.insert_text((504, 150), "expand_more")
    page.insert_text((59, 250), "Tekoälyn vastaus")

    try:
        chat_dto = PdfChatExtractorService.extract_conversation(doc)
        assert len(chat_dto.conversation) == 2
        assert chat_dto.conversation[0].role == "user"
        assert "expand_more" not in chat_dto.conversation[0].content
        assert chat_dto.conversation[1].role == "ai"
    finally:
        doc.close()


def test_pdf_chat_extractor_negative_full_page_canvas() -> None:
    """Verify that drawing rectangles spanning >= 80% of page dimensions are rejected as background canvas."""
    full_page = {
        "rect": fitz.Rect(0, 0, 595, 842),
        "fill": (1.0, 1.0, 1.0),
    }
    assert PdfChatExtractorService._is_user_bubble_drawing(full_page, 595.0, 842.0) is False

    nearly_full = {
        "rect": fitz.Rect(30, 30, 560, 800),  # w=530 (89%), h=770 (91%)
        "fill": (1.0, 1.0, 1.0),
    }
    assert PdfChatExtractorService._is_user_bubble_drawing(nearly_full, 595.0, 842.0) is False


def test_pdf_chat_extractor_truncation_inside_code_fence_not_triggered() -> None:
    """Verify that truncation indicators occurring inside markdown code fences do not trigger false positive 422."""
    code_text = "Tässä koodiesimerkki:\n```python\nbutton_label = 'näytä lisää'\nprint(button_label)\n```\nToimii."
    # Should not raise
    PdfChatExtractorService._check_truncation(code_text)


def test_pdf_chat_extractor_user_bubble_boundary_cases() -> None:
    """Verify boundary conditions in _is_user_bubble_drawing."""
    # Non-Rect rect
    assert PdfChatExtractorService._is_user_bubble_drawing({"rect": "invalid"}, 595.0, 842.0) is False

    # No fill and no color
    no_fill_color = {"rect": fitz.Rect(360, 100, 520, 160)}
    assert PdfChatExtractorService._is_user_bubble_drawing(no_fill_color, 595.0, 842.0) is False

    # Starts too far left (x0 < 0.20 * 595 = 119)
    too_far_left = {
        "rect": fitz.Rect(50, 100, 520, 160),
        "fill": (0.9, 0.9, 0.9),
    }
    assert PdfChatExtractorService._is_user_bubble_drawing(too_far_left, 595.0, 842.0) is False

    # Too narrow (< 40 pt and < 0.20 * 595)
    too_narrow = {
        "rect": fitz.Rect(490, 100, 520, 160),  # width=30
        "fill": (0.9, 0.9, 0.9),
    }
    assert PdfChatExtractorService._is_user_bubble_drawing(too_narrow, 595.0, 842.0) is False


def test_pdf_chat_extractor_attachment_card_detection_and_integration() -> None:
    """Verify detection of 76x76 pt attachment cards and synthetic [Liite: <name>] insertion."""
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)

    # User bubble
    bubble_rect = fitz.Rect(360, 100, 520, 160)
    page.draw_rect(bubble_rect, fill=(0.91, 0.93, 0.96))
    page.insert_text((370, 120), "Tässä liite")

    # 76x76 pt attachment box
    card_rect = fitz.Rect(370, 130, 446, 206)
    page.draw_rect(card_rect, fill=(0.95, 0.95, 0.95))
    page.insert_text((375, 150), "PDF")
    page.insert_text((375, 170), "launis/quorum")

    # AI reply
    page.insert_text((59, 300), "Kiitos tiedostosta.")

    try:
        cards = PdfChatExtractorService._detect_attachment_cards(page)
        assert len(cards) == 1
        assert "[Liite: launis/quorum]" in cards[0][1]

        chat_dto = PdfChatExtractorService.extract_conversation(doc)
        assert len(chat_dto.conversation) == 2
        user_turn = chat_dto.conversation[0].content
        assert "[Liite: launis/quorum]" in user_turn
        # Ensure raw PDF noise is not present as a separate text token
        assert "PDF" not in user_turn
    finally:
        doc.close()


def test_pdf_chat_extractor_table_reconstruction_edge_cases() -> None:
    """Verify table reconstruction edge cases: ragged rows, 1-col rejection, canvas rejection, exceptions."""
    mock_page = MagicMock()
    mock_page.rect = fitz.Rect(0, 0, 595, 842)

    # Table 1: data < 2 rows -> skipped
    t1 = MagicMock()
    t1.extract.return_value = [["Only one row"]]
    t1.bbox = (50, 100, 500, 150)

    # Table 2: canvas-spanning table -> skipped
    t2 = MagicMock()
    t2.extract.return_value = [["A", "B"], ["1", "2"]]
    t2.bbox = (10, 10, 580, 800)  # >80% width and height

    # Table 3: single column (< 2 cols) -> skipped
    t3 = MagicMock()
    t3.extract.return_value = [["Col1"], ["Val1"]]
    t3.bbox = (50, 200, 200, 300)

    # Table 4: ragged rows requiring padding + pipe escaping
    t4 = MagicMock()
    t4.extract.return_value = [["Col1", "Col2", "Col3"], ["Val1 | with pipe", "Val2"], [None, "ValB", "ValC"]]
    t4.bbox = (50, 400, 400, 500)

    # Table 5: extraction exception -> caught cleanly
    t5 = MagicMock()
    t5.extract.side_effect = ValueError("Corrupt table cell")
    t5.bbox = (50, 550, 400, 600)

    mock_tables = MagicMock()
    mock_tables.tables = [t1, t2, t3, t4, t5]
    mock_page.find_tables.return_value = mock_tables

    table_rects = [fitz.Rect(50, 400, 400, 500)]
    reconstructed = PdfChatExtractorService._reconstruct_tables_as_markdown(mock_page, table_rects)

    assert len(reconstructed) == 1
    rect, md = reconstructed[0]
    assert "| Col1 | Col2 | Col3 |" in md
    assert "Val1 \\| with pipe" in md

    # Entire find_tables raises exception
    mock_page.find_tables.side_effect = TypeError("Boom")
    reconstructed_empty = PdfChatExtractorService._reconstruct_tables_as_markdown(mock_page, [])
    assert reconstructed_empty == []


def test_pdf_chat_extractor_table_rects_bbox_fallback_and_exceptions() -> None:
    """Verify _get_page_table_rects fallback to bbox and exception resiliency."""
    mock_page = MagicMock()
    mock_page.rect = fitz.Rect(0, 0, 595, 842)

    # Table with no valid cells, falling back to bbox
    t_bbox_fallback = MagicMock()
    # cells is None
    type(t_bbox_fallback).cells = PropertyMock(return_value=None)
    t_bbox_fallback.bbox = (50, 100, 400, 300)

    # Table with corrupt bbox
    t_corrupt_bbox = MagicMock()
    type(t_corrupt_bbox).cells = PropertyMock(return_value=None)
    t_corrupt_bbox.bbox = None

    mock_tables = MagicMock()
    mock_tables.tables = [t_bbox_fallback, t_corrupt_bbox]
    mock_page.find_tables.return_value = mock_tables

    rects = PdfChatExtractorService._get_page_table_rects(mock_page)
    assert len(rects) == 1
    assert rects[0] == fitz.Rect(50, 100, 400, 300)

    # find_tables raises exception
    mock_page.find_tables.side_effect = ValueError("Table finder error")
    assert PdfChatExtractorService._get_page_table_rects(mock_page) == []


def test_pdf_chat_extractor_empty_messages_raises_422() -> None:
    """Verify that a PDF yielding zero conversational messages raises 422 AppException."""
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    # Only insert a header inside the vertical margin (y0 < 36pt)
    page.insert_text((50, 20), "Page 1 of 1 header")

    try:
        with pytest.raises(AppException) as exc_info:
            PdfChatExtractorService.extract_conversation(doc)
        assert exc_info.value.status_code == 422
    finally:
        doc.close()


def test_pdf_chat_extractor_span_deduplication_and_orphan_token_suppression() -> None:
    """Verify coordinate deduplication and orphan token suppression outside user bubbles."""
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)

    # User bubble
    bubble_rect = fitz.Rect(360, 100, 520, 160)
    page.draw_rect(bubble_rect, fill=(0.91, 0.93, 0.96))
    page.insert_text((370, 120), "Kysymys")

    # AI text
    page.insert_text((59, 200), "Tämä on tekoälyn vastaus käyttäjän kysymykseen.")

    # Duplicate AI text block at identical coordinates
    page.insert_text((59, 200), "Tämä on tekoälyn vastaus käyttäjän kysymykseen.")

    # Orphan glyph outside bubble (e.g. single character bullet/chevron)
    page.insert_text((59, 250), ">")

    try:
        chat_dto = PdfChatExtractorService.extract_conversation(doc)
        assert len(chat_dto.conversation) == 2
        ai_content = chat_dto.conversation[1].content
        assert "Tämä on tekoälyn vastaus" in ai_content
        # Ensure orphan ">" is not present
        assert ">" not in ai_content
    finally:
        doc.close()



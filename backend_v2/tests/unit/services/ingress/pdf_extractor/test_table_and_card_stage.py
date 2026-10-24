"""Unit tests for PDF table Markdown reconstruction and attachment card stage.

Covers table text block suppression, GitHub-Flavored Markdown table reconstruction,
camelCase and whitespace normalization, ragged row padding, and 76x76 pt attachment cards.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import fitz

from backend_v2.models.dtos.ingress import PdfTextBlockDTO
from backend_v2.services.ingress.pdf_extractor.bubble_geometry import get_page_table_rects
from backend_v2.services.ingress.pdf_extractor.table_and_card_stage import (
    detect_attachment_cards,
    filter_table_text_blocks,
    reconstruct_tables_as_markdown,
)
from backend_v2.services.ingress.pdf_extractor.turn_assembly_stage import extract_conversation_from_doc


def test_pdf_chat_extractor_table_markdown_reconstruction() -> None:
    """Verify that multi-column evaluation matrices in a page are reconstructed into GitHub-Flavored Markdown tables."""
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)

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
        table_rects = get_page_table_rects(page)
        reconstructed = reconstruct_tables_as_markdown(page, table_rects)
        assert len(reconstructed) == 1
        _rect, md = reconstructed[0]
        assert "| Kriteeri | Pisteet |" in md
        assert "| :--- | :--- |" in md
        assert "| Laatu | 5 |" in md
    finally:
        doc.close()


def test_pdf_chat_extractor_table_text_suppression_prevents_duplicate_cells() -> None:
    """Verify that text blocks intersecting table bounding boxes are suppressed."""
    table_rect = fitz.Rect(100, 200, 500, 400)
    raw_blocks = [
        PdfTextBlockDTO(x0=150.0, y0=250.0, x1=250.0, y1=280.0, text="Solun teksti", block_no=0, block_type=0),
        PdfTextBlockDTO(
            x0=59.0, y0=450.0, x1=500.0, y1=500.0, text="Teksti taulukon ulkopuolella", block_no=1, block_type=0
        ),
    ]
    assert filter_table_text_blocks(raw_blocks, []) == raw_blocks
    filtered = filter_table_text_blocks(raw_blocks, [table_rect])
    assert len(filtered) == 1
    assert filtered[0].text == "Teksti taulukon ulkopuolella"


def test_pdf_chat_extractor_attachment_card_detection_and_integration() -> None:
    """Verify detection of 76x76 pt attachment cards and synthetic [Liite: <name>] insertion."""
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)

    bubble_rect = fitz.Rect(360, 100, 520, 160)
    page.draw_rect(bubble_rect, fill=(0.91, 0.93, 0.96))
    page.insert_text((370, 120), "Tässä liite")

    card_rect = fitz.Rect(370, 130, 446, 206)
    page.draw_rect(card_rect, fill=(0.95, 0.95, 0.95))
    page.insert_text((375, 150), "PDF")
    page.insert_text((375, 170), "launis/quorum")

    page.insert_text((59, 300), "Kiitos tiedostosta.")

    try:
        cards = detect_attachment_cards(page)
        assert len(cards) == 1
        assert "[Liite: launis/quorum]" in cards[0][1]

        chat_dto = extract_conversation_from_doc(doc)
        assert len(chat_dto.conversation) == 2
        user_turn = chat_dto.conversation[0].content
        assert "[Liite: launis/quorum]" in user_turn
        assert "PDF" not in user_turn
    finally:
        doc.close()


def test_pdf_chat_extractor_table_reconstruction_edge_cases() -> None:
    """Verify table reconstruction edge cases: ragged rows, 1-col rejection, canvas rejection, exceptions."""
    mock_page = MagicMock()
    mock_page.rect = fitz.Rect(0, 0, 595, 842)

    t1 = MagicMock()
    t1.extract.return_value = [["Only one row"]]
    t1.bbox = (50, 100, 500, 150)

    t2 = MagicMock()
    t2.extract.return_value = [["A", "B"], ["1", "2"]]
    t2.bbox = (10, 10, 580, 800)

    t3 = MagicMock()
    t3.extract.return_value = [["Col1"], ["Val1"]]
    t3.bbox = (50, 200, 200, 300)

    t4 = MagicMock()
    t4.extract.return_value = [["Col1", "Col2", "Col3"], ["Val1 | with pipe", "Val2"], [None, "ValB", "ValC"]]
    t4.bbox = (50, 400, 400, 500)

    t5 = MagicMock()
    t5.extract.side_effect = ValueError("Corrupt table cell")
    t5.bbox = (50, 550, 400, 600)

    mock_tables = MagicMock()
    mock_tables.tables = [t1, t2, t3, t4, t5]
    mock_page.find_tables.return_value = mock_tables

    table_rects = [fitz.Rect(50, 400, 400, 500)]
    reconstructed = reconstruct_tables_as_markdown(mock_page, table_rects)

    assert len(reconstructed) == 1
    _rect, md = reconstructed[0]
    assert "| Col1 | Col2 | Col3 |" in md
    assert "Val1 \\| with pipe" in md

    mock_page.find_tables.side_effect = TypeError("Boom")
    reconstructed_empty = reconstruct_tables_as_markdown(mock_page, [fitz.Rect(50, 400, 400, 500)])
    assert reconstructed_empty == []
    assert reconstruct_tables_as_markdown(mock_page, []) == []


def test_reconstruct_tables_as_markdown_whitespace_and_camelcase_normalization() -> None:
    """Verify table cell camelCase splitting and multi-space collapsing."""
    mock_page = MagicMock()
    mock_page.rect.width = 595.0
    mock_page.rect.height = 842.0

    mock_table = MagicMock()
    mock_table.bbox = (50, 50, 300, 200)
    mock_table.extract.return_value = [
        ["SarakeYksi", "SarakeKaksi"],
        ["sopeudutaanRajoihinJaParannetaan", "moni   välilyönti   solussa"],
    ]

    mock_tables = MagicMock()
    mock_tables.tables = [mock_table]
    mock_page.find_tables.return_value = mock_tables

    rects = [fitz.Rect(50, 50, 300, 200)]
    results = reconstruct_tables_as_markdown(mock_page, rects)

    assert len(results) == 1
    _, md_text = results[0]
    assert "Sarake Yksi" in md_text
    assert "Sarake Kaksi" in md_text
    assert "sopeudutaan Rajoihin Ja Parannetaan" in md_text
    assert "moni välilyönti solussa" in md_text
    assert "   " not in md_text


def test_detect_attachment_cards_negative_and_boundary_partitions() -> None:
    """Verify ISTQB boundary partitions (76.0 +/- 6.0 pt) and invalid drawing/label rejections."""
    mock_page = MagicMock()
    mock_page.get_drawings.return_value = [
        {},  # Missing rect key -> skipped
        {"rect": "not_a_rect"},  # Non-Rect value -> skipped
        {"rect": fitz.Rect(0.0, 0.0, 69.9, 76.0)},  # Below min width boundary (70.0 pt) -> rejected
        {"rect": fitz.Rect(0.0, 100.0, 76.0, 182.1)},  # Above max height boundary (82.0 pt) -> rejected
        {"rect": fitz.Rect(0.0, 200.0, 70.0, 270.0)},  # Exact lower boundary (70.0x70.0 pt), only ignored labels
        {"rect": fitz.Rect(0.0, 300.0, 82.0, 382.0)},  # Exact upper boundary (82.0x82.0 pt), valid attachment name
    ]
    mock_page.get_text.return_value = [
        (5.0, 210.0, 60.0, 230.0, "PDF\n", 0, 0),
        (5.0, 235.0, 60.0, 255.0, "Liite\r\n", 1, 0),
        (5.0, 310.0, 75.0, 340.0, "report\n", 2, 0),
        (5.0, 345.0, 75.0, 375.0, "analyysi_v2.pdf\r\n", 3, 0),
    ]

    cards = detect_attachment_cards(mock_page)
    assert len(cards) == 1
    card_rect, card_label = cards[0]
    assert card_rect == fitz.Rect(0.0, 300.0, 82.0, 382.0)
    assert card_label == "[Liite: analyysi_v2.pdf]"

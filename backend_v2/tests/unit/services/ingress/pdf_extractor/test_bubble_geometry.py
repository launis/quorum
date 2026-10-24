"""Unit tests for PDF chat bubble geometry and table bounding-box extraction stage.

Covers conversation PDF detection, user speech bubble geometric classification,
table overlap shielding, cell coordinate fallback, and boundary conditions.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, PropertyMock

import fitz
import pytest

from backend_v2.services.ingress.pdf_extractor.bubble_geometry import (
    dlq_log_extraction_error,
    extract_page_user_bubbles,
    get_page_table_rects,
    is_conversation_pdf,
    is_user_bubble_drawing,
)

_DOCS_DIR = Path("docs/jwdatat")


# Phase 4, Step 1: Migrate conversation detection and bubble geometry unit tests
def test_pdf_chat_extractor_non_chat_prose_returns_false() -> None:
    """Test that standard prose reports (lopputuote.pdf) return is_conversation_pdf == False."""
    pdf_path = _DOCS_DIR / "lopputuote.pdf"
    if not pdf_path.exists():
        pytest.skip(f"Test file {pdf_path} not found")

    doc = fitz.open(str(pdf_path))
    try:
        assert is_conversation_pdf(doc) is False
    finally:
        doc.close()


def test_pdf_chat_extractor_reflektio_returns_false() -> None:
    """Test that reflektiodokumentti.pdf returns is_conversation_pdf == False."""
    pdf_path = _DOCS_DIR / "reflektiodokumentti.pdf"
    if not pdf_path.exists():
        pytest.skip(f"Test file {pdf_path} not found")

    doc = fitz.open(str(pdf_path))
    try:
        assert is_conversation_pdf(doc) is False
    finally:
        doc.close()


def test_pdf_chat_extractor_table_overlap_defense() -> None:
    """Test that drawing rectangles located inside tables are not treated as user bubbles."""
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)

    table_rect = fitz.Rect(50, 200, 500, 400)
    page.draw_rect(table_rect, color=(0.5, 0.5, 0.5))

    cell_rect = fitz.Rect(360, 210, 490, 260)
    page.draw_rect(cell_rect, fill=(0.91, 0.93, 0.96))
    page.insert_text((370, 230), "Table cell content")

    try:
        user_bubbles = extract_page_user_bubbles(page)
        assert isinstance(user_bubbles, list)
        assert is_user_bubble_drawing({"rect": fitz.Rect(0, 0, 10, 10)}, 595.0, 842.0) is False
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

    rects = get_page_table_rects(mock_page)
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
    assert is_user_bubble_drawing(drawing, 595.0, 842.0, None) is True
    assert is_user_bubble_drawing(drawing, 595.0, 842.0, [table_rect]) is False


def test_pdf_chat_extractor_short_single_word_user_bubble() -> None:
    """Verify that a short prompt like 'kiitos' right-aligned is classified as user bubble."""
    drawing = {
        "rect": fitz.Rect(470.0, 100.0, 515.0, 135.0),
        "fill": (0.91, 0.93, 0.96),
    }
    assert is_user_bubble_drawing(drawing, 595.0, 842.0) is True


def test_pdf_chat_extractor_centered_feedback_widget_rejection() -> None:
    """Verify that centered feedback cards are rejected from user bubble classification."""
    drawing = {
        "rect": fitz.Rect(150.0, 400.0, 445.0, 460.0),
        "fill": (0.91, 0.93, 0.96),
    }
    assert is_user_bubble_drawing(drawing, 595.0, 842.0) is False


def test_pdf_chat_extractor_negative_full_page_canvas() -> None:
    """Verify that drawing rectangles spanning >= 80% of page dimensions are rejected as background canvas."""
    full_page = {
        "rect": fitz.Rect(0, 0, 595, 842),
        "fill": (1.0, 1.0, 1.0),
    }
    assert is_user_bubble_drawing(full_page, 595.0, 842.0) is False

    nearly_full = {
        "rect": fitz.Rect(30, 30, 560, 800),
        "fill": (1.0, 1.0, 1.0),
    }
    assert is_user_bubble_drawing(nearly_full, 595.0, 842.0) is False


def test_pdf_chat_extractor_user_bubble_boundary_cases() -> None:
    """Verify boundary conditions in is_user_bubble_drawing."""
    assert is_user_bubble_drawing({"rect": "invalid"}, 595.0, 842.0) is False

    no_fill_color = {"rect": fitz.Rect(360, 100, 520, 160)}
    assert is_user_bubble_drawing(no_fill_color, 595.0, 842.0) is False

    too_far_left = {
        "rect": fitz.Rect(50, 100, 520, 160),
        "fill": (0.9, 0.9, 0.9),
    }
    assert is_user_bubble_drawing(too_far_left, 595.0, 842.0) is False

    too_narrow = {
        "rect": fitz.Rect(490, 100, 520, 160),
        "fill": (0.9, 0.9, 0.9),
    }
    assert is_user_bubble_drawing(too_narrow, 595.0, 842.0) is False


def test_pdf_chat_extractor_table_rects_bbox_fallback_and_exceptions() -> None:
    """Verify get_page_table_rects fallback to bbox, cell errors, and exception resiliency."""
    mock_page = MagicMock()
    mock_page.rect = fitz.Rect(0, 0, 595, 842)

    t_bbox_fallback = MagicMock()
    type(t_bbox_fallback).cells = PropertyMock(return_value=None)
    t_bbox_fallback.bbox = (50, 100, 400, 300)

    t_corrupt_bbox = MagicMock()
    type(t_corrupt_bbox).cells = PropertyMock(return_value=[None])
    type(t_corrupt_bbox).bbox = PropertyMock(side_effect=ValueError("Corrupt bbox"))

    mock_tables = MagicMock()
    mock_tables.tables = [t_bbox_fallback, t_corrupt_bbox]
    mock_page.find_tables.return_value = mock_tables

    rects = get_page_table_rects(mock_page)
    assert len(rects) == 1
    assert rects[0] == fitz.Rect(50, 100, 400, 300)

    dlq_log_extraction_error("unit_test_context", ValueError("sample fault"))

    mock_page.find_tables.side_effect = ValueError("Table finder error")
    assert get_page_table_rects(mock_page) == []

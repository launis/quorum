"""Table text block filtering, Markdown table reconstruction, and attachment card detection.

Provides pure geometric filtering for text blocks overlapping tables, GitHub-Flavored
Markdown table reconstruction from PyMuPDF table objects, and 76x76 pt Gemini attachment
card normalization.
"""

from __future__ import annotations

import re

import fitz

from backend_v2.models.dtos.ingress import PdfTextBlockDTO
from backend_v2.services.ingress.pdf_extractor.bubble_geometry import (
    _CANVAS_MAX_SIZE_RATIO,
    dlq_log_extraction_error,
)

__all__ = [
    "_ATTACHMENT_BOX_DIM_PT",
    "_ATTACHMENT_BOX_TOLERANCE_PT",
    "detect_attachment_cards",
    "filter_table_text_blocks",
    "reconstruct_tables_as_markdown",
]

# Phase 2, Step 1: Relocate attachment card geometry constants
_ATTACHMENT_BOX_DIM_PT: float = 76.0
_ATTACHMENT_BOX_TOLERANCE_PT: float = 6.0


def filter_table_text_blocks(
    page_blocks: list[PdfTextBlockDTO],
    table_rects: list[fitz.Rect],
) -> list[PdfTextBlockDTO]:
    """Suppresses raw text blocks that intersect identified table bounding boxes.

    Args:
        page_blocks: List of candidate text blocks on the page.
        table_rects: List of bounding boxes for recognized tables.

    Returns:
        Filtered list of text blocks not intersecting any table rectangle.
    """
    if not table_rects:
        return page_blocks

    filtered: list[PdfTextBlockDTO] = []
    for b in page_blocks:
        brect = fitz.Rect(b.x0, b.y0, b.x1, b.y1)
        if any(brect.intersects(tr) for tr in table_rects):
            continue
        filtered.append(b)
    return filtered


def reconstruct_tables_as_markdown(
    page: fitz.Page,
    table_rects: list[fitz.Rect],
) -> list[tuple[fitz.Rect, str]]:
    """Extracts tables from a page and formats them as Markdown pipe tables.

    Args:
        page: PyMuPDF Page instance containing tables.
        table_rects: Pre-extracted bounding boxes for identified tables.

    Returns:
        List of tuples pairing each table rectangle with its Markdown representation.
    """
    if not table_rects:
        return []

    reconstructed: list[tuple[fitz.Rect, str]] = []
    page_w = page.rect.width
    page_h = page.rect.height

    try:
        tables = page.find_tables()
        for i, t in enumerate(tables.tables):
            try:
                data = t.extract()
                if not data or len(data) < 2:
                    continue

                # Resolve rectangle for this table
                t_rect = table_rects[i] if i < len(table_rects) else fitz.Rect(t.bbox)

                # Filter out outer container tables spanning entire page
                if t_rect.width >= page_w * _CANVAS_MAX_SIZE_RATIO and t_rect.height >= page_h * _CANVAS_MAX_SIZE_RATIO:
                    continue

                # Sanitize cells and calculate max columns
                sanitized_rows: list[list[str]] = []
                for row in data:
                    cleaned_row: list[str] = []
                    for cell in row:
                        if cell is None:
                            cleaned_row.append("")
                        else:
                            c_text = str(cell).replace("\r\n", " ").replace("\n", " ").replace("|", "\\|").strip()
                            c_text = re.sub(r"([a-zåäö])([A-ZÅÄÖ])", r"\1 \2", c_text)
                            c_text = re.sub(r"\s+", " ", c_text).strip()
                            cleaned_row.append(c_text)
                    sanitized_rows.append(cleaned_row)

                max_cols = max(len(r) for r in sanitized_rows)
                if max_cols < 2:
                    continue

                # Pad rows to uniform column count
                for r in sanitized_rows:
                    if len(r) < max_cols:
                        r.extend([""] * (max_cols - len(r)))

                # Build Markdown pipe table lines
                header = "| " + " | ".join(sanitized_rows[0]) + " |"
                separator = "| " + " | ".join([":---"] * max_cols) + " |"
                data_lines = ["| " + " | ".join(r) + " |" for r in sanitized_rows[1:]]

                md_table = "\n".join([header, separator] + data_lines)
                reconstructed.append((t_rect, md_table))
            except (ValueError, AttributeError, TypeError) as exc:
                dlq_log_extraction_error("table row reconstruction", exc)
                continue
    except (ValueError, AttributeError, TypeError) as exc:
        dlq_log_extraction_error("table extraction in markdown", exc)

    return reconstructed


def detect_attachment_cards(page: fitz.Page) -> list[tuple[fitz.Rect, str]]:
    """Detects 76x76 pt file attachment cards and normalizes them to [Liite: <filename>].

    Args:
        page: PyMuPDF Page instance to scan for attachment cards.

    Returns:
        List of tuples pairing the attachment card rectangle with formatted label text.
    """
    cards: list[tuple[fitz.Rect, str]] = []
    page_blocks = page.get_text("blocks")

    for d in page.get_drawings():
        rect_obj = None
        if "rect" in d:
            rect_obj = d["rect"]
        if not isinstance(rect_obj, fitz.Rect):
            continue
        r: fitz.Rect = rect_obj
        if (
            abs(r.width - _ATTACHMENT_BOX_DIM_PT) <= _ATTACHMENT_BOX_TOLERANCE_PT
            and abs(r.height - _ATTACHMENT_BOX_DIM_PT) <= _ATTACHMENT_BOX_TOLERANCE_PT
        ):
            # Search for text blocks intersecting the attachment box
            box_texts: list[str] = []
            for b in page_blocks:
                brect = fitz.Rect(b[0], b[1], b[2], b[3])
                if r.intersects(brect):
                    b_text = b[4].strip()
                    if b_text and b_text not in ("PDF", "report", "Liite"):
                        clean_name = b_text.replace("\r\n", "").replace("\n", "")
                        box_texts.append(clean_name)

            if box_texts:
                joined_name = " ".join(box_texts)
                cards.append((r, f"[Liite: {joined_name}]"))

    return cards

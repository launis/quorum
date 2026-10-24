"""Vector speech bubble geometry and table bounding-box extraction for PDF chat ingress.

Provides pure geometric classification of user speech bubbles, dead-letter
diagnostic logging for non-fatal PyMuPDF table faults, and conversation PDF detection.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping

import fitz

from backend_v2.models.dtos.ingress import PdfCellCoordinatesDTO

logger = logging.getLogger(__name__)

__all__ = [
    "DrawingItemValue",
    "_CANVAS_MAX_SIZE_RATIO",
    "_SHORT_PROMPT_MIN_WIDTH",
    "_USER_BUBBLE_MIN_WIDTH_RATIO",
    "_USER_BUBBLE_MIN_X0_RATIO",
    "_USER_BUBBLE_MIN_X1_RATIO",
    "dlq_log_extraction_error",
    "extract_page_user_bubbles",
    "get_page_table_rects",
    "is_conversation_pdf",
    "is_user_bubble_drawing",
]

# Phase 1, Step 2: Relative geometry ratio constants for vector speech bubbles
_USER_BUBBLE_MIN_WIDTH_RATIO: float = 0.20
_USER_BUBBLE_MIN_X0_RATIO: float = 0.20
_USER_BUBBLE_MIN_X1_RATIO: float = 0.85
_CANVAS_MAX_SIZE_RATIO: float = 0.80
_SHORT_PROMPT_MIN_WIDTH: float = 40.0

type DrawingItemValue = fitz.Rect | tuple[float, ...] | list[float] | float | int | str | bool | None


def dlq_log_extraction_error(context: str, exc: Exception) -> None:
    """Route non-fatal PDF table extraction exceptions to dead-letter diagnostic logs.

    Args:
        context: Contextual label identifying where extraction encountered a fault.
        exc: Underlying exception caught during parsing.
    """
    logger.debug("[PdfChatExtractorService] DLQ table extraction fault in %s: %s", context, exc)


def is_user_bubble_drawing(
    d: Mapping[str, DrawingItemValue],
    page_width: float,
    page_height: float,
    table_rects: list[fitz.Rect] | None = None,
) -> bool:
    """Determines if a vector drawing represents a user prompt bubble using relative geometry.

    Note:
        d is an External PyMuPDF API boundary dict from page.get_drawings().

    Args:
        d: Raw drawing dictionary from PyMuPDF get_drawings.
        page_width: Page width in points.
        page_height: Page height in points.
        table_rects: Optional list of identified table rectangles for shielding.

    Returns:
        True if the drawing meets all user bubble geometric criteria, False otherwise.
    """
    rect_obj = None
    if "rect" in d:
        rect_obj = d["rect"]
    if not isinstance(rect_obj, fitz.Rect):
        return False
    r: fitz.Rect = rect_obj

    # 1. Full-page canvas rejection: reject large background containers
    if r.width >= page_width * _CANVAS_MAX_SIZE_RATIO and r.height >= page_height * _CANVAS_MAX_SIZE_RATIO:
        return False

    # 2. Minimum dimension boundaries
    if r.height < 15.0 or r.width < _SHORT_PROMPT_MIN_WIDTH:
        return False

    # 3. Vector fill/stroke requirement
    if ("fill" not in d or d["fill"] is None) and ("color" not in d or d["color"] is None):
        return False

    # 4. Table Overlap Defense: Drawings intersecting table bounding boxes
    # are shielded from being misclassified as user bubbles (protects shaded table cells)
    if table_rects and any(r.intersects(tr) for tr in table_rects):
        return False

    # 5. Right-alignment boundary: User bubbles must reach near the right margin
    if r.x1 < page_width * _USER_BUBBLE_MIN_X1_RATIO:
        return False

    # 6. Left margin boundary: User bubbles do not start from the extreme left margin
    if r.x0 < page_width * _USER_BUBBLE_MIN_X0_RATIO:
        return False

    # 7. Minimum width ratio or short prompt min width
    if r.width < page_width * _USER_BUBBLE_MIN_WIDTH_RATIO and r.width < _SHORT_PROMPT_MIN_WIDTH:
        return False

    return True


def get_page_table_rects(page: fitz.Page) -> list[fitz.Rect]:
    """Extracts valid table bounding boxes, guarding against empty cell collections and outer page containers.

    Args:
        page: PyMuPDF Page instance to scan for tabular structures.

    Returns:
        List of valid fitz.Rect bounding boxes representing identified tables.
    """
    table_rects: list[fitz.Rect] = []
    page_w = page.rect.width
    page_h = page.rect.height

    try:
        tables = page.find_tables()
        for t in tables.tables:
            # 1. Compute bounding box from cells, filtering out outer page container cells
            valid_cells: list[PdfCellCoordinatesDTO] = []
            try:
                cells = t.cells
                if cells:
                    for c in cells:
                        if not c:
                            continue
                        c_w = c[2] - c[0]
                        c_h = c[3] - c[1]
                        if c_w >= page_w * _CANVAS_MAX_SIZE_RATIO and c_h >= page_h * _CANVAS_MAX_SIZE_RATIO:
                            continue
                        valid_cells.append(
                            PdfCellCoordinatesDTO(
                                x0=float(c[0]),
                                y0=float(c[1]),
                                x1=float(c[2]),
                                y1=float(c[3]),
                            )
                        )
            except (ValueError, AttributeError, TypeError) as exc:
                dlq_log_extraction_error("cell parsing", exc)

            if valid_cells:
                min_x0 = min(c.x0 for c in valid_cells)
                min_y0 = min(c.y0 for c in valid_cells)
                max_x1 = max(c.x1 for c in valid_cells)
                max_y1 = max(c.y1 for c in valid_cells)
                table_rects.append(fitz.Rect(min_x0, min_y0, max_x1, max_y1))
                continue

            # 2. Fallback to t.bbox if cells were not available or empty
            try:
                bbox = t.bbox
                if bbox:
                    r = fitz.Rect(bbox)
                    if not (r.width >= page_w * _CANVAS_MAX_SIZE_RATIO and r.height >= page_h * _CANVAS_MAX_SIZE_RATIO):
                        table_rects.append(r)
            except (ValueError, AttributeError, TypeError) as exc:
                dlq_log_extraction_error("bbox fallback", exc)
                continue
    except (ValueError, AttributeError, TypeError) as exc:
        dlq_log_extraction_error("page table scan", exc)

    return table_rects


def is_conversation_pdf(doc: fitz.Document) -> bool:
    """Determines whether a PDF document contains structured chat vector speech bubbles.

    Args:
        doc: Loaded PyMuPDF fitz.Document instance.

    Returns:
        True if conversation bubbles are detected, False otherwise.
    """
    if len(doc) == 0:
        return False

    for page in doc:
        page_w = page.rect.width
        page_h = page.rect.height
        table_rects = get_page_table_rects(page)

        for d in page.get_drawings():
            if is_user_bubble_drawing(d, page_w, page_h, table_rects):
                return True

    return False


def extract_page_user_bubbles(page: fitz.Page) -> list[fitz.Rect]:
    """Extracts sanitized user speech bubble rectangles on a page.

    Args:
        page: PyMuPDF Page instance to inspect for user bubble drawings.

    Returns:
        List of fitz.Rect rectangles identified as user speech bubbles.
    """
    page_w = page.rect.width
    page_h = page.rect.height
    table_rects = get_page_table_rects(page)

    user_bubbles: list[fitz.Rect] = []
    for d in page.get_drawings():
        if is_user_bubble_drawing(d, page_w, page_h, table_rects):
            r_obj = None
            if "rect" in d:
                r_obj = d["rect"]
            if isinstance(r_obj, fitz.Rect):
                user_bubbles.append(r_obj)

    return user_bubbles

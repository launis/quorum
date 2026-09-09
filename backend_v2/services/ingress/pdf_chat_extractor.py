"""PDF conversational geometry and speech bubble extraction service.

Provides deterministic extraction of multi-turn dialogues from browser print
PDFs (Chrome Ctrl+P / Skia) and native platform exports (Google Gemini, ChatGPT)
using vector drawings and layout-aware text aggregation without LLM calls.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import fitz

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.v2_core import ChatHistoryDTO, ChatMessageDTO

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ["PdfChatExtractorService"]
# Relative geometry ratio constants for vector speech bubbles
_USER_BUBBLE_MIN_WIDTH_RATIO: float = 0.20
_USER_BUBBLE_MIN_X0_RATIO: float = 0.20
_USER_BUBBLE_MIN_X1_RATIO: float = 0.85
_CANVAS_MAX_SIZE_RATIO: float = 0.80
_SHORT_PROMPT_MIN_WIDTH: float = 40.0
_ORPHAN_TOKEN_MAX_WIDTH: float = 60.0
_ORPHAN_TOKEN_MAX_CHARS: int = 20

_PRINT_MARGIN_VERTICAL_PT: float = 36.0
_PAGE_ZERO_TITLE_MAX_Y0: float = 80.0
_ATTACHMENT_BOX_DIM_PT: float = 76.0
_ATTACHMENT_BOX_TOLERANCE_PT: float = 6.0

# Truncation indicators indicating truncated user prompt
_TRUNCATION_INDICATORS: tuple[str, ...] = (
    "näytä lisää",
    "näytä lisää ⌵",
    "näytä lisää v",
    "show more",
    "show more ⌵",
    "show more v",
    "read more",
    "katso lisää",
    "lue lisää",
)


class PdfChatExtractorService:
    """Deterministic extractor for browser-printed and exported chat PDFs."""

    @staticmethod
    def _is_user_bubble_drawing(
        d: dict[str, object],
        page_width: float,
        page_height: float,
        table_rects: list[fitz.Rect] | None = None,
    ) -> bool:
        """Determines if a vector drawing represents a user prompt bubble using relative geometry.

        Note:
            d is an External PyMuPDF API boundary dict from page.get_drawings().
        """
        rect_obj = d.get("rect")
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
        if d.get("fill") is None and d.get("color") is None:
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

    @staticmethod
    def _get_page_table_rects(page: fitz.Page) -> list[fitz.Rect]:
        """Extracts valid table bounding boxes, guarding against empty cell collections and outer page containers."""
        table_rects: list[fitz.Rect] = []
        page_w = page.rect.width
        page_h = page.rect.height

        try:
            tables = page.find_tables()
            for t in tables.tables:
                # 1. Compute bounding box from cells, filtering out outer page container cells
                valid_cells: list[tuple[float, float, float, float]] = []
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
                            valid_cells.append(c)
                except (ValueError, AttributeError, TypeError) as exc:
                    logger.debug("[PdfChatExtractorService] Skipping malformed table cells: %s", exc)

                if valid_cells:
                    min_x0 = min(c[0] for c in valid_cells)
                    min_y0 = min(c[1] for c in valid_cells)
                    max_x1 = max(c[2] for c in valid_cells)
                    max_y1 = max(c[3] for c in valid_cells)
                    table_rects.append(fitz.Rect(min_x0, min_y0, max_x1, max_y1))
                    continue

                # 2. Fallback to t.bbox if cells were not available or empty
                try:
                    bbox = t.bbox
                    if bbox:
                        r = fitz.Rect(bbox)
                        if not (
                            r.width >= page_w * _CANVAS_MAX_SIZE_RATIO and r.height >= page_h * _CANVAS_MAX_SIZE_RATIO
                        ):
                            table_rects.append(r)
                except (ValueError, AttributeError, TypeError) as exc:
                    logger.debug("[PdfChatExtractorService] Skipping malformed table bbox: %s", exc)
                    continue
        except (ValueError, AttributeError, TypeError) as exc:
            logger.debug("[PdfChatExtractorService] Failed to extract page table rects: %s", exc)

        return table_rects

    @staticmethod
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
            table_rects = PdfChatExtractorService._get_page_table_rects(page)

            for d in page.get_drawings():
                if PdfChatExtractorService._is_user_bubble_drawing(d, page_w, page_h, table_rects):
                    return True

        return False

    @staticmethod
    def _extract_page_user_bubbles(page: fitz.Page) -> list[fitz.Rect]:
        """Extracts sanitized user speech bubble rectangles on a page."""
        page_w = page.rect.width
        page_h = page.rect.height
        table_rects = PdfChatExtractorService._get_page_table_rects(page)

        user_bubbles: list[fitz.Rect] = []
        for d in page.get_drawings():
            if PdfChatExtractorService._is_user_bubble_drawing(d, page_w, page_h, table_rects):
                r_obj = d.get("rect")
                if isinstance(r_obj, fitz.Rect):
                    user_bubbles.append(r_obj)

        return user_bubbles

    @staticmethod
    def _check_truncation(text: str) -> None:
        """Checks for ChatGPT overflow buttons outside code fences and raises actionable warning."""
        lines = text.split("\n")
        in_code_fence = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code_fence = not in_code_fence
                continue
            if in_code_fence:
                continue

            line_lower = stripped.lower()
            for indicator in _TRUNCATION_INDICATORS:
                if indicator in line_lower:
                    logger.warning(
                        "[Ingress] PROMPT_TRUNCATION_WARNING: Detected browser print truncation artifact '%s' "
                        "in chat input. User prompt was truncated by Chrome print. Recommend Clipboard Paste.",
                        indicator,
                        extra={"error_code": "PROMPT_TRUNCATION_WARNING", "token": indicator},
                    )
                    raise AppException(
                        message=(
                            "Keskusteluhistoria on puutteellinen: Selaimen PDF-tulostus on leikannut käyttäjän "
                            "kehotteen poikki ('Näytä lisää' -painike havaittu). Tuo keskustelu leikepöydältä: "
                            "Valitse 'Liitä teksti', kopioi ChatGPT:stä koko keskustelu (Ctrl+A -> Ctrl+C) "
                            "ja liitä ruutuun (Ctrl+V)."
                        ),
                        status_code=422,
                        details={
                            "error_code": ErrorCodes.VALIDATION_FAILED.value,
                            "truncation_detected": True,
                        },
                    )

    @staticmethod
    def _sort_blocks_visual_order(
        page_blocks: list[tuple[float, float, float, float, str, int, int]],
    ) -> list[tuple[float, float, float, float, str, int, int]]:
        """Sorts blocks topologically in visual reading order.

        Quantizes vertical coordinate into 10pt bands to group inline elements,
        then orders left-to-right by x0.
        """
        return sorted(page_blocks, key=lambda b: (round(b[1] / 10.0), b[0]))

    @staticmethod
    def _filter_table_text_blocks(
        page_blocks: list[tuple[float, float, float, float, str, int, int]],
        table_rects: list[fitz.Rect],
    ) -> list[tuple[float, float, float, float, str, int, int]]:
        """Suppresses raw text blocks that intersect identified table bounding boxes."""
        if not table_rects:
            return page_blocks

        filtered: list[tuple[float, float, float, float, str, int, int]] = []
        for b in page_blocks:
            brect = fitz.Rect(b[0], b[1], b[2], b[3])
            if any(brect.intersects(tr) for tr in table_rects):
                continue
            filtered.append(b)
        return filtered

    @staticmethod
    def _reconstruct_tables_as_markdown(
        page: fitz.Page,
        table_rects: list[fitz.Rect],
    ) -> list[tuple[fitz.Rect, str]]:
        """Extracts tables from a page and formats them as Markdown pipe tables."""
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
                    if (
                        t_rect.width >= page_w * _CANVAS_MAX_SIZE_RATIO
                        and t_rect.height >= page_h * _CANVAS_MAX_SIZE_RATIO
                    ):
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
                    logger.debug("[PdfChatExtractorService] Failed to reconstruct table: %s", exc)
                    continue
        except (ValueError, AttributeError, TypeError) as exc:
            logger.debug("[PdfChatExtractorService] find_tables failed in reconstruct: %s", exc)

        return reconstructed

    @staticmethod
    def _detect_attachment_cards(page: fitz.Page) -> list[tuple[fitz.Rect, str]]:
        """Detects 76x76 pt file attachment cards and normalizes them to [Liite: <filename>]."""
        cards: list[tuple[fitz.Rect, str]] = []
        page_blocks = page.get_text("blocks")

        for d in page.get_drawings():
            rect_obj = d.get("rect")
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

    @staticmethod
    def extract_conversation(doc: fitz.Document) -> ChatHistoryDTO:
        """Extracts and segregates conversational turns from a PDF document.

        Processes vector geometry, applies print margin filtering (y0 >= 36pt,
        y1 <= page_height - 36pt), deduplicates identical coordinate text blocks,
        detects overflow truncation, and merges contiguous blocks of identical role
        across page breaks into strongly typed ChatMessageDTOs.

        Args:
            doc: Open PyMuPDF Document instance.

        Returns:
            ChatHistoryDTO containing the ordered chronological conversation.

        Raises:
            AppException: If doc is empty/corrupt or truncation artifacts are detected.
        """
        if len(doc) == 0:
            logger.error("[PdfChatExtractorService] Document has 0 pages.")
            raise AppException(
                message="PDF document contains no pages.",
                status_code=422,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        raw_turns: list[tuple[str, str]] = []
        current_role: str | None = None
        current_content: list[str] = []

        seen_blocks: set[tuple[int, float, float, float, float, str]] = set()

        for page_idx, page in enumerate(doc):
            page_h = page.rect.height
            table_rects = PdfChatExtractorService._get_page_table_rects(page)
            user_bubbles = PdfChatExtractorService._extract_page_user_bubbles(page)

            # 1. Detect tables and attachment cards
            reconstructed_tables = PdfChatExtractorService._reconstruct_tables_as_markdown(page, table_rects)
            attachment_cards = PdfChatExtractorService._detect_attachment_cards(page)
            card_rects = [c[0] for c in attachment_cards]

            # 2. Extract and filter text blocks
            raw_page_blocks = page.get_text("blocks")
            filtered_blocks = PdfChatExtractorService._filter_table_text_blocks(raw_page_blocks, table_rects)

            # 3. Integrate synthetic blocks for tables and attachment cards
            combined_blocks: list[tuple[float, float, float, float, str, int, int]] = []
            for b in filtered_blocks:
                brect = fitz.Rect(b[0], b[1], b[2], b[3])
                if any(brect.intersects(cr) for cr in card_rects):
                    continue
                combined_blocks.append((b[0], b[1], b[2], b[3], b[4], b[5], b[6]))

            for trect, md_table in reconstructed_tables:
                combined_blocks.append((trect.x0, trect.y0, trect.x1, trect.y1, md_table, -1, 0))

            for crect, card_text in attachment_cards:
                combined_blocks.append((crect.x0, crect.y0, crect.x1, crect.y1, card_text, -1, 0))

            # 4. Visual topological sort
            sorted_blocks = PdfChatExtractorService._sort_blocks_visual_order(combined_blocks)

            for b in sorted_blocks:
                x0, y0, x1, y1, text = b[0], b[1], b[2], b[3], b[4].strip()
                if not text:
                    continue

                # Margin filtering (eliminate browser headers/footers)
                if y0 < _PRINT_MARGIN_VERTICAL_PT or y1 > page_h - _PRINT_MARGIN_VERTICAL_PT:
                    continue

                # Coordinate-level span deduplication
                sig = (page_idx, round(x0, 1), round(y0, 1), round(x1, 1), round(y1, 1), text)
                if sig in seen_blocks:
                    continue
                seen_blocks.add(sig)

                # Page 0 top title filtering
                if (
                    page_idx == 0
                    and y0 < _PAGE_ZERO_TITLE_MAX_Y0
                    and (
                        text.lower() in ("keskusteluhistoria", "conversation history")
                        or (len(text.split()) <= 3 and text.lower().startswith("keskustelu"))
                    )
                ):
                    continue

                # UI button filtering
                text_clean = text.strip()
                if text_clean in ("expand_more", "expand_less", "expand_more ⌵", "expand_less ⌵", "PDF", "report"):
                    continue

                brect = fitz.Rect(x0, y0, x1, y1)

                # Bubble intersection classifier
                is_user = any(brect.intersects(bub) for bub in user_bubbles)

                # Truncation check for user blocks
                if is_user:
                    PdfChatExtractorService._check_truncation(text)

                # Orphan token filtering outside user speech bubbles
                if not is_user:
                    if (
                        (x1 - x0) < _ORPHAN_TOKEN_MAX_WIDTH
                        and len(text) < _ORPHAN_TOKEN_MAX_CHARS
                        and not any(ch.isalpha() and len(text.split()) > 2 for ch in text)
                    ):
                        continue

                role = "user" if is_user else "ai"

                if role == current_role:
                    current_content.append(text)
                else:
                    if current_role is not None and current_content:
                        raw_turns.append((current_role, "\n\n".join(current_content)))
                    current_role = role
                    current_content = [text]

        if current_role is not None and current_content:
            raw_turns.append((current_role, "\n\n".join(current_content)))

        # Build ChatMessageDTO list
        messages = [ChatMessageDTO(role=role, content=content) for role, content in raw_turns if content.strip()]

        if not messages:
            logger.error("[PdfChatExtractorService] No conversational messages extracted from PDF.")
            raise AppException(
                message="No conversational messages could be extracted from the PDF document.",
                status_code=422,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        return ChatHistoryDTO(conversation=messages)

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

# Overflow button indicators indicating truncated user prompt
_TRUNCATION_INDICATORS: tuple[str, ...] = (
    "näytä lisää",
    "näytä lisää ⌵",
    "näytä lisää v",
    "show more",
    "show more ⌵",
    "show more v",
)


class PdfChatExtractorService:
    """Deterministic extractor for browser-printed and exported chat PDFs."""

    @staticmethod
    def _is_user_bubble_drawing(d: dict[str, object], page_width: float) -> bool:
        """Determines if a vector drawing represents a user prompt bubble."""
        rect_obj = d.get("rect")
        if not isinstance(rect_obj, fitz.Rect):
            return False
        r: fitz.Rect = rect_obj

        # Ignore full-page background boxes or extremely tall/thin borders
        if r.width >= page_width - 40.0:
            return False
        if r.height < 20.0 or r.width < 50.0:
            return False

        # 1. Google Gemini Native Export / Gemini Light-Blue Tint Bubble
        fill = d.get("fill")
        if fill is not None and isinstance(fill, (list, tuple)) and len(fill) >= 3:
            # Light blue/gray tint (approx rgb 0.91, 0.93, 0.96)
            if 130.0 <= r.x0 <= 260.0 and r.x1 >= 500.0 and abs(float(fill[0]) - 0.91) < 0.08:
                return True

        # 2. Google Gemini Ctrl+P / Skia Print Right-Aligned Bubble
        # Right aligned box: x0 >= 180, x1 >= 500, width < 500, height >= 20
        if r.x0 >= 180.0 and r.x1 >= 500.0 and 50.0 <= r.width < 500.0 and r.height >= 20.0:
            return True

        # 3. ChatGPT Wide Bubble Classifier
        if r.x0 >= 190.0 and r.x1 >= 500.0 and r.width >= 250.0 and r.height >= 40.0:
            return True

        return False

    @staticmethod
    def _get_page_table_rects(page: fitz.Page) -> list[fitz.Rect]:
        """Extracts valid table bounding boxes, guarding against empty cell collections in PyMuPDF."""
        table_rects: list[fitz.Rect] = []
        try:
            tables = page.find_tables()
            for t in tables.tables:
                try:
                    table_rects.append(fitz.Rect(t.bbox))
                except ValueError, AttributeError, TypeError:
                    continue
        except ValueError, AttributeError, TypeError:
            pass
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

        user_bubble_count = 0
        for page in doc:
            page_w = page.rect.width
            table_rects = PdfChatExtractorService._get_page_table_rects(page)

            for d in page.get_drawings():
                if PdfChatExtractorService._is_user_bubble_drawing(d, page_w):
                    r_obj = d.get("rect")
                    if isinstance(r_obj, fitz.Rect):
                        # Table overlap defense: skip drawings inside table bboxes
                        if any(r_obj.intersects(tr) for tr in table_rects):
                            continue
                        user_bubble_count += 1
                        if user_bubble_count >= 1:
                            return True

        return False

    @staticmethod
    def _extract_page_user_bubbles(page: fitz.Page) -> list[fitz.Rect]:
        """Extracts sanitized user speech bubble rectangles on a page."""
        page_w = page.rect.width
        table_rects = PdfChatExtractorService._get_page_table_rects(page)

        user_bubbles: list[fitz.Rect] = []
        for d in page.get_drawings():
            if PdfChatExtractorService._is_user_bubble_drawing(d, page_w):
                r_obj = d.get("rect")
                if isinstance(r_obj, fitz.Rect):
                    # Table overlap defense: ignore drawing rects inside tables
                    if any(r_obj.intersects(tr) for tr in table_rects):
                        continue
                    user_bubbles.append(r_obj)

        return user_bubbles

    @staticmethod
    def _check_truncation(text: str) -> None:
        """Checks for ChatGPT overflow buttons and raises actionable warning."""
        text_lower = text.lower()
        for indicator in _TRUNCATION_INDICATORS:
            if indicator in text_lower:
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
            user_bubbles = PdfChatExtractorService._extract_page_user_bubbles(page)

            # Extract text blocks: (x0, y0, x1, y1, text, block_no, block_type)
            page_blocks = page.get_text("blocks")

            for b in page_blocks:
                x0, y0, x1, y1, text = b[0], b[1], b[2], b[3], b[4].strip()
                if not text:
                    continue

                # 1. Margin filtering (eliminate browser headers/footers)
                if y0 < 36.0 or y1 > page_h - 36.0:
                    continue

                # 2. Coordinate-level span deduplication
                sig = (page_idx, round(x0, 1), round(y0, 1), round(x1, 1), round(y1, 1), text)
                if sig in seen_blocks:
                    continue
                seen_blocks.add(sig)

                # 3. Citation pill and top title filtering (e.g. left-aligned small pills "PDF", "report",
                # or page 0 "Keskusteluhistoria" document title)
                if x0 < 350.0 and (x1 - x0) < 200.0 and text in ("PDF", "report", "expand_more"):
                    continue
                if page_idx == 0 and y0 < 80.0 and text.lower() in ("keskusteluhistoria", "conversation history"):
                    continue

                brect = fitz.Rect(x0, y0, x1, y1)

                # 4. Bubble intersection classifier
                is_user = any(brect.intersects(bub) for bub in user_bubbles)

                # 5. Truncation detection in user blocks or turn boundaries
                if is_user:
                    PdfChatExtractorService._check_truncation(text)

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

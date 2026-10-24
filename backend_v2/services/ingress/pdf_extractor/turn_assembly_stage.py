"""Turn segmentation, visual reading-order block sorting, and truncation detection stage.

Provides overflow button detection outside Markdown code fences, topological visual
block ordering, margin/header/orphan filtering, and multi-turn conversation assembly.
"""

from __future__ import annotations

import logging

import fitz

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.system_config import ChatHistoryDTO, ChatMessageDTO
from backend_v2.models.dtos.ingress import PdfBlockSignatureDTO, PdfTextBlockDTO, RawTurnDTO
from backend_v2.services.ingress.pdf_extractor.bubble_geometry import extract_page_user_bubbles, get_page_table_rects
from backend_v2.services.ingress.pdf_extractor.table_and_card_stage import (
    detect_attachment_cards,
    filter_table_text_blocks,
    reconstruct_tables_as_markdown,
)

logger = logging.getLogger(__name__)

__all__ = [
    "check_truncation",
    "extract_conversation_from_doc",
    "sort_blocks_visual_order",
]

# Enforce physical point thresholds for print margins, title headers, and orphan tokens
_ORPHAN_TOKEN_MAX_WIDTH: float = 60.0
_ORPHAN_TOKEN_MAX_CHARS: int = 20
_PRINT_MARGIN_VERTICAL_PT: float = 36.0
_PAGE_ZERO_TITLE_MAX_Y0: float = 80.0

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


def check_truncation(text: str) -> None:
    """Checks for ChatGPT overflow buttons outside code fences and raises actionable warning.

    Args:
        text: Extracted text content to scan for truncation buttons.

    Raises:
        AppException: If truncation artifacts are detected (ErrorCodes.VALIDATION_FAILED).
    """
    in_code_fence = False
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_fence = not in_code_fence
            continue
        if in_code_fence:
            continue

        line_lower = stripped.lower()
        for indicator in _TRUNCATION_INDICATORS:
            if indicator in line_lower:
                logger.error(
                    "[Ingress] PROMPT_TRUNCATION_WARNING: Detected browser print truncation artifact '%s' "
                    "in chat input. User prompt was truncated by Chrome print. Recommend Clipboard Paste.",
                    indicator,
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "token": indicator},
                )
                raise AppException(
                    message=(
                        "Keskusteluhistoria on puutteellinen: Selaimen PDF-tulostus on leikannut käyttäjän "
                        "kehotteen poikki ('Näytä lisää' -painike havaittu). Tuo keskustelu leikepöydältä: "
                        "Valitse 'Liitä teksti', kopioi ChatGPT:stä koko keskustelu (Ctrl+A -> Ctrl+C) "
                        "ja liitä ruutuun (Ctrl+V)."
                    ),
                    status_code=422,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "truncation_detected": True},
                )


def sort_blocks_visual_order(page_blocks: list[PdfTextBlockDTO]) -> list[PdfTextBlockDTO]:
    """Sorts blocks topologically in visual reading order (10pt vertical bands, then left-to-right x0).

    Args:
        page_blocks: List of text blocks to sort.

    Returns:
        Sorted list of text blocks in reading order.
    """
    return sorted(page_blocks, key=lambda b: (round(b.y0 / 10.0), b.x0))


def _collect_sorted_page_blocks(
    page: fitz.Page,
    table_rects: list[fitz.Rect],
) -> list[PdfTextBlockDTO]:
    """Collects raw text, Markdown table, and attachment card blocks sorted in visual reading order.

    Args:
        page: Open PyMuPDF Page instance.
        table_rects: Bounding rectangles for tables detected on the page.

    Returns:
        Visually sorted list of merged page text blocks.
    """
    reconstructed_tables = reconstruct_tables_as_markdown(page, table_rects)
    attachment_cards = detect_attachment_cards(page)
    card_rects = [crect for crect, _ in attachment_cards]

    wrapped_blocks = [
        PdfTextBlockDTO(
            x0=float(b[0]),
            y0=float(b[1]),
            x1=float(b[2]),
            y1=float(b[3]),
            text=str(b[4]),
            block_no=int(b[5]),
            block_type=int(b[6]),
        )
        for b in page.get_text("blocks")
    ]
    filtered_blocks = filter_table_text_blocks(wrapped_blocks, table_rects)

    combined_blocks: list[PdfTextBlockDTO] = [
        b for b in filtered_blocks if not any(fitz.Rect(b.x0, b.y0, b.x1, b.y1).intersects(cr) for cr in card_rects)
    ]

    for trect, md_table in reconstructed_tables:
        combined_blocks.append(
            PdfTextBlockDTO(
                x0=trect.x0, y0=trect.y0, x1=trect.x1, y1=trect.y1, text=md_table, block_no=-1, block_type=0
            )
        )

    for crect, card_text in attachment_cards:
        combined_blocks.append(
            PdfTextBlockDTO(
                x0=crect.x0, y0=crect.y0, x1=crect.x1, y1=crect.y1, text=card_text, block_no=-1, block_type=0
            )
        )

    return sort_blocks_visual_order(combined_blocks)


def _is_filtered_noise_block(
    block: PdfTextBlockDTO,
    text: str,
    page_idx: int,
    is_user: bool,
) -> bool:
    """Determines whether a non-margin text block is a title header, UI control label, or AI orphan token.

    Args:
        block: Candidate PDF text block DTO.
        text: Stripped text content of the block.
        page_idx: Zero-based page index in the document.
        is_user: Whether the block intersects a user prompt bubble.

    Returns:
        True if the block should be suppressed as non-conversational noise, False otherwise.
    """
    if (
        page_idx == 0
        and block.y0 < _PAGE_ZERO_TITLE_MAX_Y0
        and (
            text.lower() in ("keskusteluhistoria", "conversation history")
            or (len(text.split()) <= 3 and text.lower().startswith("keskustelu"))
        )
    ):
        return True

    if text in ("expand_more", "expand_less", "expand_more ⌵", "expand_less ⌵", "PDF", "report"):
        return True

    if not is_user and (
        (block.x1 - block.x0) < _ORPHAN_TOKEN_MAX_WIDTH
        and len(text) < _ORPHAN_TOKEN_MAX_CHARS
        and not any(ch.isalpha() and len(text.split()) > 2 for ch in text)
    ):
        return True

    return False


def extract_conversation_from_doc(doc: fitz.Document) -> ChatHistoryDTO:
    """Extracts and segregates conversational turns from a PDF document into ChatMessageDTOs.

    Args:
        doc: Open PyMuPDF Document instance.

    Returns:
        ChatHistoryDTO containing the ordered chronological conversation.

    Raises:
        AppException: If doc is empty/corrupt or truncation artifacts are detected (ErrorCodes.VALIDATION_FAILED).
    """
    if len(doc) == 0:
        logger.error(
            "[PdfChatExtractorService] Document has 0 pages.",
            extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )
        raise AppException(
            message="PDF document contains no pages.",
            status_code=422,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    raw_turns: list[RawTurnDTO] = []
    current_role: str | None = None
    current_content: list[str] = []
    seen_blocks: set[PdfBlockSignatureDTO] = set()

    for page_idx, page in enumerate(doc):
        page_h = page.rect.height
        table_rects = get_page_table_rects(page)
        user_bubbles = extract_page_user_bubbles(page)

        for b in _collect_sorted_page_blocks(page, table_rects):
            text = b.text.strip()
            if not text or b.y0 < _PRINT_MARGIN_VERTICAL_PT or b.y1 > page_h - _PRINT_MARGIN_VERTICAL_PT:
                continue

            sig = PdfBlockSignatureDTO(
                page_idx=page_idx,
                x0=round(b.x0, 1),
                y0=round(b.y0, 1),
                x1=round(b.x1, 1),
                y1=round(b.y1, 1),
                text=text,
            )
            if sig in seen_blocks:
                continue
            seen_blocks.add(sig)

            brect = fitz.Rect(b.x0, b.y0, b.x1, b.y1)
            is_user = any(brect.intersects(bub) for bub in user_bubbles)
            if _is_filtered_noise_block(b, text, page_idx, is_user):
                continue

            if is_user:
                check_truncation(text)

            role = "user" if is_user else "ai"
            if role == current_role:
                current_content.append(text)
            else:
                if current_role is not None and current_content:
                    raw_turns.append(RawTurnDTO(role=current_role, content="\n\n".join(current_content)))
                current_role = role
                current_content = [text]

    if current_role is not None and current_content:
        raw_turns.append(RawTurnDTO(role=current_role, content="\n\n".join(current_content)))

    messages = [ChatMessageDTO(role=turn.role, content=turn.content) for turn in raw_turns if turn.content.strip()]
    if not messages:
        logger.error(
            "[PdfChatExtractorService] No conversational messages extracted from PDF.",
            extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )
        raise AppException(
            message="No conversational messages could be extracted from the PDF document.",
            status_code=422,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    return ChatHistoryDTO(conversation=messages)

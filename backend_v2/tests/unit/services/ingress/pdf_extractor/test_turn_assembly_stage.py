"""Unit tests for PDF turn segmentation, visual ordering, and truncation stage.

Covers chronological turn assembly, real-world Gemini PDF extraction, visual reading-order
topological sorting, overflow button truncation checks, and header/margin/orphan filtering.
"""

from __future__ import annotations

from pathlib import Path

import fitz
import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.domain.system_config import ChatHistoryDTO
from backend_v2.services.ingress.pdf_extractor.bubble_geometry import is_conversation_pdf
from backend_v2.services.ingress.pdf_extractor.turn_assembly_stage import (
    check_truncation,
    extract_conversation_from_doc,
)

_DOCS_DIR = Path("docs/jwdatat")


def _create_synthetic_chat_pdf() -> bytes:
    """Create an in-memory PDF with user speech bubble drawing and text.

    Returns:
        Raw PDF document bytes containing a two-turn conversation.
    """
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)

    bubble_rect = fitz.Rect(360, 100, 520, 160)
    page.draw_rect(bubble_rect, color=(0.9, 0.9, 0.9), fill=(0.91, 0.93, 0.96))

    page.insert_text((370, 120), "Hei tekoäly! Kerro minulle arkkitehtuurista.")
    page.insert_text((59, 200), "Hei käyttäjä! Quorum on kognitiivinen arkkitehtuuri.")

    raw = doc.tobytes()
    pdf_bytes = bytes(raw)
    doc.close()
    return pdf_bytes


def _create_synthetic_truncated_chat_pdf() -> bytes:
    """Create an in-memory PDF with ChatGPT 'Näytä lisää' overflow button.

    Returns:
        Raw PDF document bytes containing a truncated user bubble.
    """
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)

    bubble_rect = fitz.Rect(360, 100, 520, 180)
    page.draw_rect(bubble_rect, color=(0.9, 0.9, 0.9), fill=(0.91, 0.93, 0.96))

    page.insert_text((370, 120), "Pitkä kehote joka katkesi...")
    page.insert_text((370, 150), "Näytä lisää")

    raw = doc.tobytes()
    pdf_bytes = bytes(raw)
    doc.close()
    return pdf_bytes


# Phase 4, Step 1: Migrate turn segmentation, visual ordering, and truncation tests
def test_pdf_chat_extractor_synthetic_detection_and_extraction() -> None:
    """Test successful detection and turn assembly on synthetic chat PDF."""
    pdf_bytes = _create_synthetic_chat_pdf()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    try:
        assert is_conversation_pdf(doc) is True
        chat_dto = extract_conversation_from_doc(doc)
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
            extract_conversation_from_doc(doc)

        assert exc_info.value.status_code == 422
        assert exc_info.value.details is not None
        assert exc_info.value.details["truncation_detected"] is True
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
        assert is_conversation_pdf(doc) is True
        chat_dto = extract_conversation_from_doc(doc)
        assert len(chat_dto.conversation) >= 4
        assert chat_dto.conversation[0].role == "user"
        assert "etätyön" in chat_dto.conversation[0].content.lower()

        user_turns = [m for m in chat_dto.conversation if m.role == "user"]
        assert len(user_turns) >= 2
    finally:
        doc.close()


def test_pdf_chat_extractor_empty_document_fails_fast() -> None:
    """Test that a 0-page document raises AppException."""
    doc = fitz.open()
    try:
        assert is_conversation_pdf(doc) is False
        with pytest.raises(AppException) as exc_info:
            extract_conversation_from_doc(doc)
        assert exc_info.value.status_code == 422
    finally:
        doc.close()


def test_pdf_chat_extractor_visual_reading_order_preserves_turns() -> None:
    """Verify that blocks arranged out-of-order in raw sequence are sorted topologically by visual coordinate."""
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)

    bubble_rect = fitz.Rect(360, 100, 520, 160)
    page.draw_rect(bubble_rect, fill=(0.91, 0.93, 0.96))

    page.insert_text((59, 400), "Tämä on vastausosan toinen kappale.")
    page.insert_text((370, 120), "Käyttäjän ensimmäinen kehote.")
    page.insert_text((59, 250), "Tämä on vastausosan ensimmäinen kappale.")

    try:
        chat_dto = extract_conversation_from_doc(doc)
        assert len(chat_dto.conversation) == 2
        assert chat_dto.conversation[0].role == "user"
        assert "Käyttäjän ensimmäinen" in chat_dto.conversation[0].content
        assert chat_dto.conversation[1].role == "ai"
        assert chat_dto.conversation[1].content.index("ensimmäinen kappale") < chat_dto.conversation[1].content.index(
            "toinen kappale"
        )
    finally:
        doc.close()


def test_pdf_chat_extractor_truncation_detection() -> None:
    """Verify that truncation indicator phrases outside code fences trigger actionable 422 warning."""
    for indicator in ("näytä lisää", "show more", "read more", "katso lisää", "lue lisää"):
        with pytest.raises(AppException) as exc_info:
            check_truncation(f"Kysymys katkesi... {indicator}")
        assert exc_info.value.status_code == 422
        assert exc_info.value.details is not None
        assert exc_info.value.details["truncation_detected"] is True


def test_pdf_chat_extractor_ui_button_block_filtering() -> None:
    """Verify that isolated UI button text blocks like 'expand_more' are filtered from speech turns."""
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)

    bubble_rect = fitz.Rect(360, 100, 520, 160)
    page.draw_rect(bubble_rect, fill=(0.91, 0.93, 0.96))

    page.insert_text((370, 120), "Käyttäjän kysymys")
    page.insert_text((504, 150), "expand_more")
    page.insert_text((59, 250), "Tekoälyn vastaus")

    try:
        chat_dto = extract_conversation_from_doc(doc)
        assert len(chat_dto.conversation) == 2
        assert chat_dto.conversation[0].role == "user"
        assert "expand_more" not in chat_dto.conversation[0].content
        assert chat_dto.conversation[1].role == "ai"
    finally:
        doc.close()


def test_pdf_chat_extractor_truncation_inside_code_fence_not_triggered() -> None:
    """Verify that truncation indicators occurring inside markdown code fences do not trigger false positive 422."""
    code_text = "Tässä koodiesimerkki:\n```python\nbutton_label = 'näytä lisää'\nprint(button_label)\n```\nToimii."
    check_truncation(code_text)


def test_pdf_chat_extractor_empty_messages_raises_422() -> None:
    """Verify that a PDF yielding zero conversational messages raises 422 AppException."""
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((50, 20), "Page 1 of 1 header")

    try:
        with pytest.raises(AppException) as exc_info:
            extract_conversation_from_doc(doc)
        assert exc_info.value.status_code == 422
    finally:
        doc.close()


def test_pdf_chat_extractor_span_deduplication_and_orphan_token_suppression() -> None:
    """Verify coordinate deduplication and orphan token suppression outside user bubbles."""
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)

    bubble_rect = fitz.Rect(360, 100, 520, 160)
    page.draw_rect(bubble_rect, fill=(0.91, 0.93, 0.96))
    page.insert_text((370, 120), "Kysymys")

    page.insert_text((59, 200), "Tämä on tekoälyn vastaus käyttäjän kysymykseen.")
    page.insert_text((59, 200), "Tämä on tekoälyn vastaus käyttäjän kysymykseen.")
    page.insert_text((59, 250), ">")

    try:
        chat_dto = extract_conversation_from_doc(doc)
        assert len(chat_dto.conversation) == 2
        ai_content = chat_dto.conversation[1].content
        assert "Tämä on tekoälyn vastaus" in ai_content
        assert ">" not in ai_content
    finally:
        doc.close()

"""Unit tests for DocumentExtractionService covering eager extraction, PDF dates, and ISTQB negative boundaries."""

from __future__ import annotations

import base64
from pathlib import Path
from unittest.mock import patch

import fitz
import pytest
from fastapi import status
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.inputs import Base64Attachment, WorkflowInputsIngress
from backend_v2.models.domain.system_config import ChatHistoryDTO, ChatMessageDTO
from backend_v2.services.document_extraction import DocumentExtractionService

_SITRA_FIXTURE_PATH = Path("data/test_inputs_sitra/keskusteluhistoria SITRA.pdf")


class Base64AttachmentFactory(ModelFactory[Base64Attachment]):
    """Polyfactory model factory for Base64Attachment ingress payloads."""

    __model__ = Base64Attachment
    __set_as_default_factory_for_type__ = True


class WorkflowInputsIngressFactory(ModelFactory[WorkflowInputsIngress]):
    """Polyfactory model factory for WorkflowInputsIngress models."""

    __model__ = WorkflowInputsIngress
    __set_as_default_factory_for_type__ = True


class ChatMessageDTOFactory(ModelFactory[ChatMessageDTO]):
    """Polyfactory model factory for ChatMessageDTO turns."""

    __model__ = ChatMessageDTO
    __set_as_default_factory_for_type__ = True


class ChatHistoryDTOFactory(ModelFactory[ChatHistoryDTO]):
    """Polyfactory model factory for ChatHistoryDTO transcripts."""

    __model__ = ChatHistoryDTO
    __set_as_default_factory_for_type__ = True


def _build_pdf_bytes(
    text: str,
    mod_date: str = "",
    creation_date: str = "",
) -> bytes:
    """Create deterministic in-memory PDF binary bytes with optional metadata dates.

    Args:
        text: Body text to render onto the first PDF page.
        mod_date: Optional PDF modDate metadata string.
        creation_date: Optional PDF creationDate metadata string.

    Returns:
        Serialized PDF bytes.
    """
    doc = fitz.open()
    try:
        page = doc.new_page()
        page.insert_text((50, 50), text)
        if mod_date or creation_date:
            doc.set_metadata({"modDate": mod_date, "creationDate": creation_date})
        return bytes(doc.tobytes())
    finally:
        doc.close()


@pytest.mark.asyncio
async def test_process_ingress_payload_empty() -> None:
    """Verify empty dynamic_inputs pass through without mutation."""
    service = DocumentExtractionService()
    ingress = WorkflowInputsIngressFactory.build(dynamic_inputs={})

    result = await service.process_ingress_payload(ingress)
    assert result.dynamic_inputs == {}


def test_process_ingress_payload_strict_hydration_failure() -> None:
    """Verify missing required Base64Attachment fields fail fast with ValidationError at ingress."""
    with pytest.raises(ValidationError):
        WorkflowInputsIngress.model_validate(
            {"dynamic_inputs": {"file_1": {"content_base64": base64.b64encode(b"dummy data").decode("utf-8")}}}
        )


@pytest.mark.asyncio
async def test_process_ingress_payload_text_decoding_and_multiline_base64() -> None:
    """Verify UTF-8 text attachments decode cleanly including RFC 2045 line-wrapped base64."""
    service = DocumentExtractionService()

    original_text = "Hello, strict Pydantic world! Explicit multi-line base64 verification."
    raw_b64 = base64.b64encode(original_text.encode("utf-8")).decode("utf-8")
    wrapped_b64 = f"{raw_b64[:16]}\r\n{raw_b64[16:]}"

    attachment = Base64AttachmentFactory.build(filename="notes.txt", content_base64=wrapped_b64)
    ingress = WorkflowInputsIngressFactory.build(dynamic_inputs={"file_1": attachment, "plain_key": "unchanged"})

    result = await service.process_ingress_payload(ingress)

    assert result.dynamic_inputs["file_1"] == original_text
    assert result.dynamic_inputs["plain_key"] == "unchanged"


@pytest.mark.asyncio
async def test_process_ingress_payload_pdf_extraction_real_bytes() -> None:
    """Verify binary PDF attachments extract text through threadpool execution without partial mocks."""
    service = DocumentExtractionService()
    expected_phrase = (
        "Deterministic PDF prose body exceeding one hundred characters so markdown extraction "
        "is verified end-to-end through the real PyMuPDF pipeline without partial mocking."
    )
    pdf_bytes = _build_pdf_bytes(expected_phrase)
    b64_content = base64.b64encode(pdf_bytes).decode("utf-8")

    attachment = Base64AttachmentFactory.build(filename="document.PDF", content_base64=b64_content)
    ingress = WorkflowInputsIngressFactory.build(dynamic_inputs={"file_1": attachment})

    result = await service.process_ingress_payload(ingress)

    extracted_val = result.dynamic_inputs["file_1"]
    assert isinstance(extracted_val, str)
    assert "Deterministic PDF prose body" in extracted_val
    assert "document_date" not in result.dynamic_inputs


def test_pdf_date_parser_formats_and_bva_boundaries() -> None:
    """Verify parse_pdf_date handles valid formats and ISTQB BVA min-1/min/max/max+1 boundaries."""
    # Valid UTC and offset formats
    assert DocumentExtractionService.parse_pdf_date("D:20230117123000Z") == "2023-01-17T12:30:00Z"
    assert DocumentExtractionService.parse_pdf_date("D:20260526064500+03'00'") == "2026-05-26T06:45:00+03:00"
    assert DocumentExtractionService.parse_pdf_date("D:20260526064500-05'00'") == "2026-05-26T06:45:00-05:00"
    assert DocumentExtractionService.parse_pdf_date("D:20260526064500+0200") == "2026-05-26T06:45:00+02:00"
    assert DocumentExtractionService.parse_pdf_date("D:20260526064500+03") == "2026-05-26T06:45:00+03:00"
    assert DocumentExtractionService.parse_pdf_date("D:20260526064500-05") == "2026-05-26T06:45:00-05:00"
    assert DocumentExtractionService.parse_pdf_date("D:20230117") == "2023-01-17T00:00:00Z"

    # ISTQB Boundary Value Analysis: exact valid min/max bounds
    assert DocumentExtractionService.parse_pdf_date("D:20260101000000Z") == "2026-01-01T00:00:00Z"
    assert DocumentExtractionService.parse_pdf_date("D:20261231235959Z") == "2026-12-31T23:59:59Z"

    # ISTQB Boundary Value Analysis: out-of-range min-1 / max+1 components clamp to defaults
    assert DocumentExtractionService.parse_pdf_date("D:20260032246060X") == "2026-01-01T00:00:00Z"
    assert DocumentExtractionService.parse_pdf_date("D:20261300999999+ab") == "2026-01-01T00:00:00Z"

    # Invalid prefix, short year, empty, and None inputs
    assert DocumentExtractionService.parse_pdf_date("20230117123000Z") is None
    assert DocumentExtractionService.parse_pdf_date("D:202") is None
    assert DocumentExtractionService.parse_pdf_date("D:abcd") is None
    assert DocumentExtractionService.parse_pdf_date("") is None
    assert DocumentExtractionService.parse_pdf_date(None) is None


@pytest.mark.asyncio
async def test_pdf_metadata_date_propagation_and_chronological_precedence() -> None:
    """Verify multiple PDF attachments propagate the most recent modDate unless document_date is preset."""
    service = DocumentExtractionService()

    older_pdf = _build_pdf_bytes("Older document content", mod_date="D:20250115080000Z")
    newer_pdf = _build_pdf_bytes("Newer document content", mod_date="D:20260526064500+03'00'")

    ingress = WorkflowInputsIngressFactory.build(
        dynamic_inputs={
            "older_doc": Base64AttachmentFactory.build(
                filename="older.pdf",
                content_base64=base64.b64encode(older_pdf).decode("utf-8"),
            ),
            "newer_doc": Base64AttachmentFactory.build(
                filename="newer.pdf",
                content_base64=base64.b64encode(newer_pdf).decode("utf-8"),
            ),
        }
    )

    result = await service.process_ingress_payload(ingress)
    assert result.dynamic_inputs["document_date"] == "2026-05-26T06:45:00+03:00"

    # Existing non-empty document_date must not be overwritten
    preset_ingress = WorkflowInputsIngressFactory.build(
        dynamic_inputs={
            "newer_doc": Base64AttachmentFactory.build(
                filename="newer.pdf",
                content_base64=base64.b64encode(newer_pdf).decode("utf-8"),
            ),
            "document_date": "2024-12-31T00:00:00Z",
        }
    )
    preset_result = await service.process_ingress_payload(preset_ingress)
    assert preset_result.dynamic_inputs["document_date"] == "2024-12-31T00:00:00Z"


def test_pdf_fallback_when_picture_comment_detected() -> None:
    """Verify _extract_pdf_sync falls back to plain text when pymupdf4llm outputs picture comments."""
    service = DocumentExtractionService()
    pdf_bytes = _build_pdf_bytes("User Question: Hello AI\nAI Answer: Hello User! This is full dialogue.")

    with patch(
        "pymupdf4llm.to_markdown",
        return_value="<!-- Start of picture text -->\nUser Question: Hello AI<br><!-- End of picture text -->",
    ):
        extracted_text, _ = service._extract_pdf_sync(pdf_bytes)

    assert "Hello User! This is full dialogue." in extracted_text


def test_pdf_extraction_routes_to_conversation_extractor() -> None:
    """Verify _extract_pdf_sync routes to PdfChatExtractorService when conversation bubbles are detected."""
    service = DocumentExtractionService()

    doc = fitz.open()
    try:
        page = doc.new_page(width=595, height=842)
        page.draw_rect(fitz.Rect(360, 100, 520, 160), color=(0.9, 0.9, 0.9), fill=(0.91, 0.93, 0.96))
        page.insert_text((370, 120), "User prompt inside bubble")
        page.insert_text((59, 200), "AI response text")
        pdf_bytes = bytes(doc.tobytes())
    finally:
        doc.close()

    mock_chat = ChatHistoryDTOFactory.build(
        conversation=[
            ChatMessageDTOFactory.build(role="user", content="User prompt inside bubble"),
            ChatMessageDTOFactory.build(role="ai", content="AI response text"),
        ]
    )

    with patch(
        "backend_v2.services.document_extraction.PdfChatExtractorService.extract_conversation",
        return_value=mock_chat,
    ):
        extracted_text, _ = service._extract_pdf_sync(pdf_bytes)

    assert '"role":"user"' in extracted_text or '"role": "user"' in extracted_text
    assert "User prompt inside bubble" in extracted_text


@pytest.mark.skipif(
    not _SITRA_FIXTURE_PATH.exists(),
    reason="Local fixture data/test_inputs_sitra/keskusteluhistoria SITRA.pdf not present",
)
def test_extract_pdf_sync_sitra_conversation_no_segfault() -> None:
    """Verify real conversation PDF extracts cleanly without C++ layout engine segfaults."""
    file_bytes = _SITRA_FIXTURE_PATH.read_bytes()
    extracted_text, parsed_date = DocumentExtractionService._extract_pdf_sync(file_bytes)

    assert len(extracted_text) > 1000
    assert '"role": "user"' in extracted_text or '"role":"user"' in extracted_text
    assert "Sitra" in extracted_text or "sitra" in extracted_text
    assert parsed_date is not None


@pytest.mark.asyncio
async def test_process_ingress_payload_corrupt_pdf_raises_app_exception() -> None:
    """Negative test: corrupt non-PDF binary bytes raise AppException(VALIDATION_FAILED)."""
    service = DocumentExtractionService()
    ingress = WorkflowInputsIngressFactory.build(
        dynamic_inputs={
            "broken_pdf": Base64AttachmentFactory.build(
                filename="broken.pdf",
                content_base64=base64.b64encode(b"not a valid pdf stream").decode("utf-8"),
            )
        }
    )

    with pytest.raises(AppException) as exc_info:
        await service.process_ingress_payload(ingress)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.details == {"error_code": ErrorCodes.VALIDATION_FAILED.value}


@pytest.mark.asyncio
@pytest.mark.parametrize("invalid_b64", ["!@#$", "abc", "   \n\t  "])
async def test_process_ingress_payload_invalid_base64_raises_app_exception(invalid_b64: str) -> None:
    """Negative test: non-base64 characters, bad padding, or whitespace-only payloads raise AppException."""
    service = DocumentExtractionService()
    ingress = WorkflowInputsIngressFactory.build(
        dynamic_inputs={
            "bad_attachment": Base64AttachmentFactory.build(
                filename="notes.txt",
                content_base64=invalid_b64,
            )
        }
    )

    with pytest.raises(AppException) as exc_info:
        await service.process_ingress_payload(ingress)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.details == {"error_code": ErrorCodes.VALIDATION_FAILED.value}


@pytest.mark.asyncio
async def test_process_ingress_payload_reraises_downstream_app_exception() -> None:
    """Negative test: downstream AppException is preserved without re-wrapping."""
    service = DocumentExtractionService()
    doc = fitz.open()
    try:
        page = doc.new_page(width=595, height=842)
        page.draw_rect(fitz.Rect(360, 100, 520, 160), color=(0.9, 0.9, 0.9), fill=(0.91, 0.93, 0.96))
        page.insert_text((370, 120), "User prompt")
        pdf_bytes = bytes(doc.tobytes())
    finally:
        doc.close()

    ingress = WorkflowInputsIngressFactory.build(
        dynamic_inputs={
            "chat_pdf": Base64AttachmentFactory.build(
                filename="chat.pdf",
                content_base64=base64.b64encode(pdf_bytes).decode("utf-8"),
            )
        }
    )
    downstream_exc = AppException(
        message="Downstream conversation fault",
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        details={"error_code": ErrorCodes.EMPTY_INPUT.value},
    )

    with (
        patch(
            "backend_v2.services.document_extraction.PdfChatExtractorService.extract_conversation",
            side_effect=downstream_exc,
        ),
        pytest.raises(AppException) as exc_info,
    ):
        await service.process_ingress_payload(ingress)

    assert exc_info.value is downstream_exc


def test_pdf_metadata_creation_date_fallback() -> None:
    """Verify _extract_pdf_sync falls back to creationDate when modDate is empty."""
    service = DocumentExtractionService()
    pdf_bytes = _build_pdf_bytes("Test document text", mod_date="", creation_date="D:20260101120000Z")

    text, parsed_date = service._extract_pdf_sync(pdf_bytes)
    assert "Test document text" in text
    assert parsed_date == "2026-01-01T12:00:00Z"

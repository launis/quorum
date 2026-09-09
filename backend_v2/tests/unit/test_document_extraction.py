import base64
from unittest.mock import patch

import pytest
from fastapi import status

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.inputs import WorkflowInputsIngress
from backend_v2.services.document_extraction import DocumentExtractionService


@pytest.mark.asyncio
async def test_process_ingress_payload_empty() -> None:
    """Test that empty dynamic_inputs are bypassed securely."""
    service = DocumentExtractionService()
    ingress = WorkflowInputsIngress()

    result = await service.process_ingress_payload(ingress)
    assert result.dynamic_inputs == {}


@pytest.mark.asyncio
async def test_process_ingress_payload_strict_hydration_failure() -> None:
    """Test that Duck Typing is prevented and missing filename raises 422 AppException."""
    service = DocumentExtractionService()

    # Payload missing 'filename', but has 'content_base64'
    ingress = WorkflowInputsIngress(
        dynamic_inputs={"file_1": {"content_base64": base64.b64encode(b"dummy data").decode("utf-8")}}
    )

    with pytest.raises(AppException) as exc_info:
        await service.process_ingress_payload(ingress)

    assert exc_info.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_process_ingress_payload_text_decoding() -> None:
    """Test successful decoding of a text file from Base64."""
    service = DocumentExtractionService()

    original_text = "Hello, strict Pydantic world!"
    b64_content = base64.b64encode(original_text.encode("utf-8")).decode("utf-8")

    ingress = WorkflowInputsIngress(dynamic_inputs={"file_1": {"filename": "notes.txt", "content_base64": b64_content}})

    result = await service.process_ingress_payload(ingress)

    # The base64 blob should be destroyed and replaced with decoded text
    assert result.dynamic_inputs["file_1"] == original_text


@pytest.mark.asyncio
async def test_process_ingress_payload_pdf_extraction() -> None:
    """Test successful routing of PDF extraction to threadpool."""
    service = DocumentExtractionService()

    # We mock _extract_pdf_sync so we don't need actual fitz/pymupdf running in the test
    b64_content = base64.b64encode(b"fake pdf bytes").decode("utf-8")

    ingress = WorkflowInputsIngress(
        dynamic_inputs={"file_1": {"filename": "document.pdf", "content_base64": b64_content}}
    )

    with patch.object(service, "_extract_pdf_sync", return_value=("# Extracted PDF Content", None)):
        result = await service.process_ingress_payload(ingress)

    # The base64 blob should be replaced by the mocked extracted string
    assert result.dynamic_inputs["file_1"] == "# Extracted PDF Content"


def test_pdf_date_parser_formats() -> None:
    """Test that parse_pdf_date correctly parses a range of standard PDF date/timezone formats."""
    # Test valid UTC format
    assert DocumentExtractionService.parse_pdf_date("D:20230117123000Z") == "2023-01-17T12:30:00Z"

    # Test valid offset with single quotes (+03'00')
    assert DocumentExtractionService.parse_pdf_date("D:20260526064500+03'00'") == "2026-05-26T06:45:00+03:00"

    # Test valid offset with single quotes and negative sign (-05'00')
    assert DocumentExtractionService.parse_pdf_date("D:20260526064500-05'00'") == "2026-05-26T06:45:00-05:00"

    # Test valid offset without quotes (+0200)
    assert DocumentExtractionService.parse_pdf_date("D:20260526064500+0200") == "2026-05-26T06:45:00+02:00"

    # Test incomplete date/time (defaulting sub-components)
    assert DocumentExtractionService.parse_pdf_date("D:20230117") == "2023-01-17T00:00:00Z"

    # Test invalid format (missing D: prefix)
    assert DocumentExtractionService.parse_pdf_date("20230117123000Z") is None

    # Test short invalid string
    assert DocumentExtractionService.parse_pdf_date("D:202") is None

    # Test empty/None values
    assert DocumentExtractionService.parse_pdf_date("") is None
    assert DocumentExtractionService.parse_pdf_date(None) is None  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_pdf_metadata_date_propagation() -> None:
    """Test that parsed PDF dates are successfully injected into raw_inputs dynamic_inputs."""
    service = DocumentExtractionService()

    b64_content = base64.b64encode(b"fake pdf bytes").decode("utf-8")

    # PDF date metadata mock: returns text + valid parsed date string
    mock_pdf_extracted_date = "2026-05-26T06:45:00+03:00"

    ingress = WorkflowInputsIngress(
        dynamic_inputs={"chat_log": {"filename": "keskusteluhistoria SITRA.pdf", "content_base64": b64_content}}
    )

    with patch.object(service, "_extract_pdf_sync", return_value=("# Chat Log Text", mock_pdf_extracted_date)):
        result = await service.process_ingress_payload(ingress)

    # Check that text got extracted
    assert result.dynamic_inputs["chat_log"] == "# Chat Log Text"

    # Check that document_date was propagated to dynamic_inputs
    assert result.dynamic_inputs["document_date"] == mock_pdf_extracted_date


def test_pdf_fallback_when_picture_comment_detected() -> None:
    """Test that _extract_pdf_sync falls back to plain text when pymupdf4llm outputs picture comments."""
    service = DocumentExtractionService()
    # Create minimal valid PDF bytes with fitz
    import fitz

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "User Question: Hello AI\nAI Answer: Hello User! This is full dialogue.")
    pdf_bytes = doc.tobytes()
    doc.close()

    # When pymupdf4llm returns picture text comment, fallback should activate
    with patch(
        "pymupdf4llm.to_markdown",
        return_value="<!-- Start of picture text -->\nUser Question: Hello AI<br><!-- End of picture text -->",
    ):
        extracted_text, _ = service._extract_pdf_sync(pdf_bytes)

    assert "Hello User! This is full dialogue." in extracted_text


def test_pdf_extraction_routes_to_conversation_extractor() -> None:
    """Test that _extract_pdf_sync routes to PdfChatExtractorService when conversation is detected."""
    service = DocumentExtractionService()
    import fitz
    from backend_v2.models.v2_core import ChatHistoryDTO, ChatMessageDTO

    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    # Draw bubble to trigger is_conversation_pdf
    page.draw_rect(fitz.Rect(360, 100, 520, 160), color=(0.9, 0.9, 0.9), fill=(0.91, 0.93, 0.96))
    page.insert_text((370, 120), "User prompt inside bubble")
    page.insert_text((59, 200), "AI response text")
    pdf_bytes = doc.tobytes()
    doc.close()

    mock_chat = ChatHistoryDTO(
        conversation=[
            ChatMessageDTO(role="user", content="User prompt inside bubble"),
            ChatMessageDTO(role="ai", content="AI response text"),
        ]
    )

    with patch(
        "backend_v2.services.ingress.pdf_chat_extractor.PdfChatExtractorService.extract_conversation",
        return_value=mock_chat,
    ):
        extracted_text, _ = service._extract_pdf_sync(pdf_bytes)

    assert '"role":"user"' in extracted_text or '"role": "user"' in extracted_text
    assert "User prompt inside bubble" in extracted_text


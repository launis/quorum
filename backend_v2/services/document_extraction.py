"""Document extraction service for decoding base64 attachments and extracting text.

Provides CPU-bound extraction helpers for PDF, DOCX, TXT, and conversation PDFs.
"""

from __future__ import annotations

import base64
import logging
import sys

import fitz
from fastapi import status
from fastapi.concurrency import run_in_threadpool

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.inputs import Base64Attachment, WorkflowInputsIngress
from backend_v2.services.ingress.pdf_extractor import PdfChatExtractorService

logger = logging.getLogger(__name__)

_PICTURE_TEXT_COMMENT_MARKER: str = "<!-- Start of picture text -->"
_MIN_MARKDOWN_EXTRACTION_CHARS: int = 100

__all__ = [
    "DocumentExtractionService",
]


def _decode_base64_payload(content_base64: str) -> bytes:
    """Strictly decode a non-empty Base64 string while permitting RFC 2045 whitespace wrapping.

    Args:
        content_base64: Encoded Base64 string from an ingress attachment.

    Returns:
        Decoded raw binary bytes.

    Raises:
        ValueError: If content_base64 is empty, whitespace-only, or contains non-Base64 characters.
    """
    normalized = "".join(content_base64.split())
    if not normalized:
        raise ValueError("Base64 attachment payload cannot be empty.")
    return base64.b64decode(normalized, validate=True)


def _parse_bounded_date_component(
    raw: str,
    start: int,
    min_val: int,
    max_val: int,
    default_val: str,
) -> str:
    """Extract a 2-digit bounded integer component from a raw PDF date string.

    Args:
        raw: PDF date body string with leading 'D:' stripped.
        start: Zero-based start offset of the 2-character slice.
        min_val: Inclusive minimum valid integer value.
        max_val: Inclusive maximum valid integer value.
        default_val: Fallback 2-character string when absent or out of range.

    Returns:
        Validated 2-character numeric component string or default_val.
    """
    end = start + 2
    if len(raw) >= end:
        candidate = raw[start:end]
        if len(candidate) == 2 and candidate.isdigit() and min_val <= int(candidate) <= max_val:
            return candidate
    return default_val


def _parse_pdf_timezone(tz_part: str) -> str:
    """Normalize a PDF date timezone suffix into ISO-8601 offset notation.

    Args:
        tz_part: Raw timezone substring starting at offset 14 of the PDF date body.

    Returns:
        ISO-8601 timezone designator ('Z' or '+HH:MM' / '-HH:MM').
    """
    if not tz_part or tz_part.startswith("Z"):
        return "Z"
    if tz_part[0] in ("+", "-"):
        sign = tz_part[0]
        tz_val = tz_part[1:].replace("'", "")
        if len(tz_val) >= 4 and tz_val[:4].isdigit():
            return f"{sign}{tz_val[0:2]}:{tz_val[2:4]}"
        if len(tz_val) >= 2 and tz_val[:2].isdigit():
            return f"{sign}{tz_val[0:2]}:00"
    return "Z"


def _extract_prose_markdown(doc: fitz.Document) -> str:
    """Extract markdown prose from a non-conversation PDF with plain-text fallback.

    Args:
        doc: Open PyMuPDF Document instance.

    Returns:
        Extracted markdown or plain text content.
    """
    import pymupdf4llm

    try:
        md_text = str(pymupdf4llm.to_markdown(doc))
    finally:
        pymupdf4llm.use_layout(False)

    # Fallback when PyMuPDF4LLM converts text into HTML picture comments or truncates dialogue
    if _PICTURE_TEXT_COMMENT_MARKER in md_text or len(md_text.strip()) < _MIN_MARKDOWN_EXTRACTION_CHARS:
        plain_pages = [str(page.get_text("text")) for page in doc]
        plain_text = "\n\n".join(plain_pages).strip()
        if plain_text and (_PICTURE_TEXT_COMMENT_MARKER in md_text or len(plain_text) > len(md_text.strip())):
            return plain_text
    return md_text


def _extract_pdf_metadata_date(doc: fitz.Document) -> str | None:
    """Resolve ISO-8601 document date from PyMuPDF metadata dictionary.

    Prefers modDate when populated, otherwise inspects creationDate.

    Args:
        doc: Open PyMuPDF Document instance.

    Returns:
        Parsed ISO-8601 timestamp string or None if absent or unparseable.
    """
    metadata = doc.metadata
    pdf_date: str | None = None
    if metadata is not None:
        if "modDate" in metadata and metadata["modDate"]:
            pdf_date = str(metadata["modDate"])
        elif "creationDate" in metadata and metadata["creationDate"]:
            pdf_date = str(metadata["creationDate"])

    if pdf_date is not None:
        return DocumentExtractionService.parse_pdf_date(pdf_date)
    return None


class DocumentExtractionService:
    """Service for handling CPU-bound document extraction tasks."""

    @staticmethod
    def parse_pdf_date(pdf_date_str: str | None) -> str | None:
        """Parse a standard PDF date string into ISO-8601 format.

        Standard PDF date format: D:YYYYMMDDHHmmSS[OHH'mm']
        For example: 'D:20230117123000Z' or 'D:20260526064500+03'00''

        Args:
            pdf_date_str: Raw PDF date string from metadata.

        Returns:
            ISO-8601 formatted date string or None if unparseable.
        """
        if not pdf_date_str or not isinstance(pdf_date_str, str) or not pdf_date_str.startswith("D:"):
            return None

        raw = pdf_date_str[2:]
        if len(raw) < 4 or not raw[:4].isdigit():
            return None

        year = raw[0:4]
        month = _parse_bounded_date_component(raw, 4, 1, 12, "01")
        day = _parse_bounded_date_component(raw, 6, 1, 31, "01")
        hour = _parse_bounded_date_component(raw, 8, 0, 23, "00")
        minute = _parse_bounded_date_component(raw, 10, 0, 59, "00")
        second = _parse_bounded_date_component(raw, 12, 0, 59, "00")
        tz_str = _parse_pdf_timezone(raw[14:])

        return f"{year}-{month}-{day}T{hour}:{minute}:{second}{tz_str}"

    @staticmethod
    def _extract_pdf_sync(file_bytes: bytes) -> tuple[str, str | None]:
        """Execute isolated CPU-bound PyMuPDF extraction on raw PDF bytes.

        Args:
            file_bytes: Raw binary bytes of the PDF document.

        Returns:
            A 2-tuple of (extracted_markdown_text, parsed_pdf_date_iso_str).
        """
        # Ensure layout engine is not active if pymupdf4llm was previously loaded
        if "pymupdf4llm" in sys.modules:
            import pymupdf4llm

            pymupdf4llm.use_layout(False)

        doc = fitz.open(stream=file_bytes, filetype="pdf")
        try:
            if PdfChatExtractorService.is_conversation_pdf(doc):
                chat_dto = PdfChatExtractorService.extract_conversation(doc)
                md_text = chat_dto.model_dump_json()
            else:
                md_text = _extract_prose_markdown(doc)

            return md_text.strip(), _extract_pdf_metadata_date(doc)
        finally:
            if "pymupdf4llm" in sys.modules:
                import pymupdf4llm

                pymupdf4llm.use_layout(False)
            doc.close()

    async def process_ingress_payload(self, ingress: WorkflowInputsIngress) -> WorkflowInputsIngress:
        """Eagerly extract binary PDF and text content from an ingress payload.

        Args:
            ingress: Ingress workflow inputs containing potential binary attachments.

        Returns:
            WorkflowInputsIngress with all attachments converted to extracted string content.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED (HTTP 400) if base64 decoding
                or PDF/text extraction fails, or re-raises downstream AppException instances.
        """
        extracted_dates: list[str] = []

        # Rebuild dynamic_inputs because V2CoreBase is frozen=True
        new_dynamic_inputs = dict(ingress.dynamic_inputs)

        for key, val in list(ingress.dynamic_inputs.items()):
            if isinstance(val, Base64Attachment):
                attachment = val
                filename_lower = attachment.filename.lower()
                try:
                    file_bytes = _decode_base64_payload(attachment.content_base64)
                    if filename_lower.endswith(".pdf"):
                        logger.info(
                            "[DocumentExtractionService] Found binary PDF %s. Extracting synchronously.",
                            attachment.filename,
                        )
                        extracted, parsed_date = await run_in_threadpool(self._extract_pdf_sync, file_bytes)
                        new_dynamic_inputs[key] = extracted
                        if parsed_date:
                            extracted_dates.append(parsed_date)
                    else:
                        logger.info("[DocumentExtractionService] Found text file %s. Decoding.", attachment.filename)
                        decoded_text = file_bytes.decode("utf-8", errors="replace")
                        new_dynamic_inputs[key] = decoded_text
                except AppException:
                    raise
                except Exception as e:
                    logger.error(
                        "[DocumentExtractionService] Failed to extract %s: %s",
                        attachment.filename,
                        str(e),
                        exc_info=True,
                        extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    )
                    raise AppException(
                        message=f"Failed to extract text from {attachment.filename}",
                        status_code=status.HTTP_400_BAD_REQUEST,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    ) from e

        if extracted_dates:
            # Sort chronologically to prefer the most recent date
            valid_dates = sorted(extracted_dates, reverse=True)

            if "document_date" not in new_dynamic_inputs or not new_dynamic_inputs["document_date"]:
                new_dynamic_inputs["document_date"] = valid_dates[0]
                logger.info(
                    "[DocumentExtractionService] Dynamically extracted original PDF date "
                    "and injected as document_date: %s",
                    valid_dates[0],
                )

        return ingress.model_copy(update={"dynamic_inputs": new_dynamic_inputs})

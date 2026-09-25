"""Document extraction service for decoding base64 attachments and extracting text.

Provides CPU-bound extraction helpers for PDF, DOCX, TXT, and conversation PDFs.
"""

from __future__ import annotations

import base64
import logging

from fastapi import status
from fastapi.concurrency import run_in_threadpool

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.inputs import Base64Attachment, WorkflowInputsIngress

logger = logging.getLogger(__name__)


class DocumentExtractionService:
    """Service for handling CPU-bound document extraction tasks."""

    @staticmethod
    def parse_pdf_date(pdf_date_str: str | None) -> str | None:
        """Parses a standard PDF date string into ISO-8601 format.

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
        raw_month = raw[4:6] if len(raw) >= 6 else ""
        month = raw_month if len(raw_month) == 2 and raw_month.isdigit() and 1 <= int(raw_month) <= 12 else "01"

        raw_day = raw[6:8] if len(raw) >= 8 else ""
        day = raw_day if len(raw_day) == 2 and raw_day.isdigit() and 1 <= int(raw_day) <= 31 else "01"

        raw_hour = raw[8:10] if len(raw) >= 10 else ""
        hour = raw_hour if len(raw_hour) == 2 and raw_hour.isdigit() and 0 <= int(raw_hour) <= 23 else "00"

        raw_min = raw[10:12] if len(raw) >= 12 else ""
        minute = raw_min if len(raw_min) == 2 and raw_min.isdigit() and 0 <= int(raw_min) <= 59 else "00"

        raw_sec = raw[12:14] if len(raw) >= 14 else ""
        second = raw_sec if len(raw_sec) == 2 and raw_sec.isdigit() and 0 <= int(raw_sec) <= 59 else "00"

        tz_str = "Z"
        if len(raw) > 14:
            tz_part = raw[14:]
            if tz_part.startswith("Z"):
                tz_str = "Z"
            elif tz_part[0] in ["+", "-"]:
                sign = tz_part[0]
                tz_val = tz_part[1:].replace("'", "")
                if len(tz_val) >= 4 and tz_val[:4].isdigit():
                    tz_str = f"{sign}{tz_val[0:2]}:{tz_val[2:4]}"
                elif len(tz_val) >= 2 and tz_val[:2].isdigit():
                    tz_str = f"{sign}{tz_val[0:2]}:00"

        return f"{year}-{month}-{day}T{hour}:{minute}:{second}{tz_str}"

    @staticmethod
    def _extract_pdf_sync(file_bytes: bytes) -> tuple[str, str | None]:
        """Isolated CPU-bound PyMuPDF extraction.

        Returns:
            A tuple of (extracted_markdown_text, parsed_pdf_date_iso_str)
        """
        import sys

        import fitz

        # Ensure layout engine is not active if pymupdf4llm was previously loaded
        if "pymupdf4llm" in sys.modules:
            import pymupdf4llm

            pymupdf4llm.use_layout(False)

        doc = fitz.open(stream=file_bytes, filetype="pdf")
        try:
            from backend_v2.services.ingress.pdf_chat_extractor import PdfChatExtractorService

            if PdfChatExtractorService.is_conversation_pdf(doc):
                chat_dto = PdfChatExtractorService.extract_conversation(doc)
                md_text = chat_dto.model_dump_json()
            else:
                import pymupdf4llm

                try:
                    md_text = str(pymupdf4llm.to_markdown(doc))
                finally:
                    pymupdf4llm.use_layout(False)

                # Robustness Fallback: If PyMuPDF4LLM converted text into HTML picture comments or truncated dialogue
                if "<!-- Start of picture text -->" in md_text or len(md_text.strip()) < 100:
                    plain_pages = [page.get_text("text") for page in doc]
                    plain_text = "\n\n".join(plain_pages).strip()
                    if plain_text and (
                        "<!-- Start of picture text -->" in md_text or len(plain_text) > len(md_text.strip())
                    ):
                        md_text = plain_text

            # Read modDate first, fallback to creationDate
            metadata = doc.metadata
            pdf_date: str | None = None
            if metadata is not None:
                if "modDate" in metadata and metadata["modDate"]:
                    pdf_date = str(metadata["modDate"])
                elif "creationDate" in metadata and metadata["creationDate"]:
                    pdf_date = str(metadata["creationDate"])

            parsed_date = None
            if pdf_date is not None:
                parsed_date = DocumentExtractionService.parse_pdf_date(pdf_date)

            return md_text.strip(), parsed_date
        finally:
            if "pymupdf4llm" in sys.modules:
                import pymupdf4llm

                pymupdf4llm.use_layout(False)
            doc.close()

    async def process_ingress_payload(self, ingress: WorkflowInputsIngress) -> WorkflowInputsIngress:
        """Eagerly extracts binary PDF/Text content from an ingress payload in a strictly typed manner.

        Args:
            ingress: Ingress workflow inputs containing potential binary attachments.

        Returns:
            WorkflowInputsIngress with all attachments converted to extracted string content.

        Raises:
            AppException: If file extraction or decoding fails.
        """
        extracted_dates = []

        # Rebuild dynamic_inputs because V2CoreBase is frozen=True
        new_dynamic_inputs = dict(ingress.dynamic_inputs)

        for key, val in list(ingress.dynamic_inputs.items()):
            if isinstance(val, Base64Attachment):
                attachment = val
                filename_lower = attachment.filename.lower()
                try:
                    file_bytes = base64.b64decode(attachment.content_base64)
                    if filename_lower.endswith(".pdf"):
                        logger.info(
                            "[DocumentExtractionService] Found binary PDF %s. Extracting synchronously.",
                            attachment.filename,
                        )
                        extracted, parsed_date = await run_in_threadpool(self._extract_pdf_sync, file_bytes)
                        # Destroy base64 blob, replace with string
                        new_dynamic_inputs[key] = extracted
                        if parsed_date:
                            extracted_dates.append(parsed_date)
                    else:
                        logger.info("[DocumentExtractionService] Found text file %s. Decoding.", attachment.filename)
                        decoded_text = file_bytes.decode("utf-8", errors="replace")
                        new_dynamic_inputs[key] = decoded_text
                except Exception as e:
                    logger.error("[DocumentExtractionService] Failed to extract %s", attachment.filename, exc_info=True)
                    raise AppException(
                        message=f"Failed to extract text from {attachment.filename}",
                        status_code=status.HTTP_400_BAD_REQUEST,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    ) from e

        if extracted_dates:
            # Sort chronologically to prefer the most recent date
            valid_dates = sorted(extracted_dates, reverse=True)

            # Phase 1, Step 4: Inject only if not already explicitly populated by the user
            if "document_date" not in new_dynamic_inputs or not new_dynamic_inputs["document_date"]:
                new_dynamic_inputs["document_date"] = valid_dates[0]
                logger.info(
                    "[DocumentExtractionService] Dynamically extracted original PDF date "
                    "and injected as document_date: %s",
                    valid_dates[0],
                )

        return ingress.model_copy(update={"dynamic_inputs": new_dynamic_inputs})

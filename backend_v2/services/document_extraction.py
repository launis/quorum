import base64
import datetime
import logging

from fastapi import status
from fastapi.concurrency import run_in_threadpool
from pydantic import ValidationError

from backend_v2.exceptions import AppException
from backend_v2.models.domain.inputs import Base64Attachment, WorkflowInputsIngress

logger = logging.getLogger(__name__)


class DocumentExtractionService:
    """Service for handling CPU-bound document extraction tasks."""

    @staticmethod
    def parse_pdf_date(pdf_date_str: str) -> str | None:
        """Parses a standard PDF date string into ISO-8601 format.

        Standard PDF date format: D:YYYYMMDDHHmmSS[OHH'mm']
        For example: 'D:20230117123000Z' or 'D:20260526064500+03'00''
        """
        if not pdf_date_str or not pdf_date_str.startswith("D:"):
            return None

        s = pdf_date_str[2:]
        if len(s) < 8:
            return None

        try:
            year = s[0:4]
            month = s[4:6]
            day = s[6:8]

            hour = s[8:10] if len(s) >= 10 else "00"
            minute = s[10:12] if len(s) >= 12 else "00"
            second = s[12:14] if len(s) >= 14 else "00"

            tz_part = s[14:] if len(s) > 14 else ""
            tz_str = "Z"
            if tz_part:
                if tz_part.startswith("Z"):
                    tz_str = "Z"
                elif tz_part[0] in ("+", "-"):
                    sign = tz_part[0]
                    # Strip single quotes if present (e.g. +03'00')
                    tz_val = tz_part[1:].replace("'", "")
                    if len(tz_val) >= 4:
                        tz_str = f"{sign}{tz_val[0:2]}:{tz_val[2:4]}"
                    elif len(tz_val) >= 2:
                        tz_str = f"{sign}{tz_val[0:2]}:00"

            iso_str = f"{year}-{month}-{day}T{hour}:{minute}:{second}{tz_str}"
            # Validate ISO-8601 string parsing natively to ensure compatibility
            clean_iso = iso_str.replace("Z", "+00:00")
            datetime.datetime.fromisoformat(clean_iso)
            return iso_str
        except Exception:
            logger.warning("[DocumentExtractionService] Failed to parse PDF date metadata: %s", pdf_date_str)
            return None

    @staticmethod
    def _extract_pdf_sync(file_bytes: bytes) -> tuple[str, str | None]:
        """Isolated CPU-bound PyMuPDF extraction.

        Returns:
            A tuple of (extracted_markdown_text, parsed_pdf_date_iso_str)
        """
        import fitz
        import pymupdf4llm

        doc = fitz.open(stream=file_bytes, filetype="pdf")
        try:
            import ftfy

            md_text = str(pymupdf4llm.to_markdown(doc))
            md_text = ftfy.fix_text(md_text)

            # Robustness Fallback: If PyMuPDF4LLM converted text into HTML picture comments or truncated dialogue
            if "<!-- Start of picture text -->" in md_text or len(md_text.strip()) < 100:
                plain_pages = [page.get_text("text") for page in doc]
                plain_text = ftfy.fix_text("\n\n".join(plain_pages)).strip()
                if plain_text and (
                    "<!-- Start of picture text -->" in md_text or len(plain_text) > len(md_text.strip())
                ):
                    md_text = plain_text

            # Read modDate first, fallback to creationDate
            metadata = doc.metadata or {}
            pdf_date = metadata.get("modDate") or metadata.get("creationDate")
            parsed_date = None
            if pdf_date:
                parsed_date = DocumentExtractionService.parse_pdf_date(pdf_date)

            return md_text.strip(), parsed_date
        finally:
            doc.close()

    async def process_ingress_payload(self, ingress: WorkflowInputsIngress) -> WorkflowInputsIngress:
        """Eagerly extracts binary PDF/Text content from an ingress payload in a strictly typed manner."""
        extracted_dates = []

        # Rebuild dynamic_inputs because V2CoreBase is frozen=True
        new_dynamic_inputs = dict(ingress.dynamic_inputs)

        for key, val in list(ingress.dynamic_inputs.items()):
            if isinstance(val, dict) and "content_base64" in val:
                try:
                    # STRICT PHASE 9: Fail-fast hydration instead of Duck Typing
                    attachment = Base64Attachment.model_validate(val)
                except ValidationError as e:
                    logger.error("[DocumentExtractionService] Strict hydration failed for attachment in key %s", key)
                    raise AppException(
                        message=f"Invalid file attachment payload in key '{key}'",
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        details={"error_code": "INVALID_ATTACHMENT_SCHEMA"},
                    ) from e

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
                        import ftfy

                        decoded_text = file_bytes.decode("utf-8", errors="ignore")
                        new_dynamic_inputs[key] = ftfy.fix_text(decoded_text)
                except Exception as e:
                    logger.error("[DocumentExtractionService] Failed to extract %s", attachment.filename, exc_info=True)
                    raise AppException(
                        message=f"Failed to extract text from {attachment.filename}",
                        status_code=status.HTTP_400_BAD_REQUEST,
                        details={"error_code": "FILE_EXTRACTION_FAILED"},
                    ) from e

        if extracted_dates:
            # Sort chronologically to prefer the most recent date
            valid_dates = sorted(extracted_dates, reverse=True)

            # Phase 1, Step 4: Inject only if not already explicitly populated by the user
            if not new_dynamic_inputs.get("document_date"):
                new_dynamic_inputs["document_date"] = valid_dates[0]
                logger.info(
                    "[DocumentExtractionService] Dynamically extracted original PDF date "
                    "and injected as document_date: %s",
                    valid_dates[0],
                )

        return ingress.model_copy(update={"dynamic_inputs": new_dynamic_inputs})

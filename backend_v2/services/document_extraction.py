import base64
import logging
from typing import Any

import fitz
import pymupdf4llm
from fastapi import status
from fastapi.concurrency import run_in_threadpool

from backend_v2.exceptions import AppException

logger = logging.getLogger(__name__)

class DocumentExtractionService:
    """Service for handling CPU-bound document extraction tasks."""

    @staticmethod
    def _extract_pdf_sync(file_bytes: bytes) -> str:
        """Isolated CPU-bound PyMuPDF extraction."""
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        md_text = str(pymupdf4llm.to_markdown(doc))
        doc.close()
        return md_text.strip()

    async def process_raw_inputs(self, raw_inputs: dict[str, Any]) -> None:
        """Eagerly extracts binary PDF/Text content from raw_inputs in place."""
        if not isinstance(raw_inputs, dict):
            return

        for key, val in raw_inputs.items():
            if isinstance(val, dict) and "content_base64" in val:
                filename = val.get("filename", "unknown.pdf").lower()
                try:
                    file_bytes = base64.b64decode(val["content_base64"])
                    if filename.endswith(".pdf"):
                        logger.info(
                            "[DocumentExtractionService] Found binary PDF %s. Extracting synchronously.", filename
                        )
                        extracted = await run_in_threadpool(self._extract_pdf_sync, file_bytes)
                        # Destroy base64 blob, replace with string
                        raw_inputs[key] = extracted
                    else:
                        logger.info("[DocumentExtractionService] Found text file %s. Decoding.", filename)
                        raw_inputs[key] = file_bytes.decode("utf-8", errors="ignore")
                except Exception as e:
                    logger.error("[DocumentExtractionService] Failed to extract %s", filename, exc_info=True)
                    raise AppException(
                        message=f"Failed to extract text from {filename}",
                        status_code=status.HTTP_400_BAD_REQUEST,
                        details={"error_code": "FILE_EXTRACTION_FAILED"},
                    ) from e

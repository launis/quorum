"""Deterministic presentation sanitizer for MCP external tool findings and audit traces.

Extracts substantive empirical evidence from raw tool response payloads (CDATA-wrapped
JSON, markdown code fences, or structured text), strips technical noise, applies
sentence-boundary character budgeting, and ensures Dumb Painter presentation parity.
"""

from __future__ import annotations

import logging
import re
from typing import Annotated

from pydantic import ConfigDict, Field, ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.dtos.mcp import MCPStructuredContentDTO
from backend_v2.services.length_budget_enforcer import enforce_sentence_boundary_budget
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

__all__ = ["McpExtractionResult", "McpPresentationSanitizer"]


class McpExtractionResult(V2CoreBase):
    """Result container for structured MCP finding extraction.

    Attributes:
        text: Extracted finding text if structured parsing succeeded.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    text: Annotated[str | None, Field(default=None, description="Extracted substantive finding text.")] = None


class McpPresentationSanitizer:
    """Service for deterministic presentation sanitization of external tool findings."""

    @staticmethod
    def _try_extract_structured_json(candidate: str) -> McpExtractionResult:
        """Attempt to extract substantive finding text from JSON payload.

        Args:
            candidate: Candidate JSON string.

        Returns:
            McpExtractionResult containing extracted text or None if invalid.
        """
        try:
            parsed = MCPStructuredContentDTO.model_validate_json(candidate, strict=False)
            if parsed.results:
                for item in parsed.results:
                    for field_val in (item.content, item.snippet, item.text, item.summary):
                        if field_val is not None and field_val.strip():
                            return McpExtractionResult(text=field_val.strip())
            for top_val in (
                parsed.answer,
                parsed.summary,
                parsed.description,
                parsed.text,
                parsed.message,
                parsed.finding,
            ):
                if top_val is not None and top_val.strip():
                    return McpExtractionResult(text=top_val.strip())
            return McpExtractionResult(text=None)
        except ValidationError:
            return McpExtractionResult(text=None)

    @staticmethod
    def _strip_envelopes(candidate: str) -> str:
        """Strip outer CDATA envelopes and Markdown code fences from raw tool text.

        Args:
            candidate: Trimmed raw tool response string.

        Returns:
            Inner payload string with CDATA and Markdown code fences removed.
        """
        if candidate.startswith("<![CDATA["):
            candidate = candidate[9:]
        if candidate.endswith("]]>"):
            candidate = candidate[:-3]
        candidate = candidate.strip()
        if not candidate:
            return ""

        if candidate.startswith("```json"):
            candidate = candidate[7:]
        elif candidate.startswith("```"):
            candidate = candidate[3:]
        if candidate.endswith("```"):
            candidate = candidate[:-3]
        return candidate.strip()

    @staticmethod
    def sanitize_finding(raw_summary: str | None, max_chars: int | None = None) -> str | None:
        """Sanitize an external tool finding or audit response summary for presentation.

        Strips CDATA wrappers, markdown code fences, extracts substantive text from
        structured MCP JSON representations via Pydantic V2 without naked dictionary
        parsing, strips HTML tags and non-text delimiters, normalizes whitespace,
        applies sentence-boundary character budgeting, and guarantees terminal punctuation.

        Args:
            raw_summary: Raw tool response string or audit summary.
            max_chars: Optional override for maximum character budget. If not provided,
                defaults to settings.mcp_presentation_max_chars.

        Returns:
            Sanitized, sentence-budgeted text concluding on terminal punctuation,
            or None if input is empty, whitespace-only, or contains no extractable text.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if the resolved max_chars budget is <= 0.
        """
        budget = max_chars if max_chars is not None else get_settings().mcp_presentation_max_chars
        if budget <= 0:
            msg = f"max_chars must be a positive integer, but received {budget}."
            logger.error(
                "[McpPresentationSanitizer] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        if raw_summary is None:
            return None

        candidate = McpPresentationSanitizer._strip_envelopes(raw_summary.strip())
        if not candidate:
            return None

        extracted_text: str | None = None

        # Attempt structured Rust JSON hydration via Pydantic V2 DTO
        if candidate.startswith("{") and candidate.endswith("}"):
            extraction_res = McpPresentationSanitizer._try_extract_structured_json(candidate)
            extracted_text = extraction_res.text

        candidate_text = extracted_text if extracted_text is not None else candidate

        # Strip HTML tags
        candidate_text = re.sub(r"<[^>]+>", " ", candidate_text)

        # Strip surrounding structural brackets and whole-string wrapping quotes
        candidate_text = candidate_text.strip(" \t\r\n{}[]")
        if (candidate_text.startswith('"') and candidate_text.endswith('"')) or (
            candidate_text.startswith("'") and candidate_text.endswith("'")
        ):
            candidate_text = candidate_text[1:-1].strip()

        candidate_text = re.sub(r"\s+", " ", candidate_text).strip()
        if not candidate_text:
            return None

        # Apply sentence-boundary character budgeting
        if len(candidate_text) > budget:
            candidate_text = enforce_sentence_boundary_budget(candidate_text, budget)

        # Enforce terminal sentence punctuation
        if not candidate_text.endswith((".", "!", "?")):
            candidate_text = f"{candidate_text}."

        return candidate_text

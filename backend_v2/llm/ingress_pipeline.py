"""Universal Ingress Pipeline for LLM execution outputs.

Provides a unified entry point for parsing LLM output strings into dictionaries
before they are hydrated by Pydantic models. Relies entirely on Native Structured
Outputs, stripping basic Markdown formatting if present.
The legacy Hybrid XML Protocol has been deprecated.
"""

import json
from typing import Any, cast

from backend_v2.exceptions import AppException, ErrorCodes


class UniversalIngress:
    """Handles parsing for LLM outputs."""

    @classmethod
    def parse_llm_output(cls, raw_text: str) -> dict[str, Any]:
        """Parses the raw LLM output into a dictionary.

        Expects the LLM API (via Native Structured Outputs) to have generated
        valid JSON. Handles basic Markdown code block stripping just in case.

        Args:
            raw_text: The raw string output from the LLM.

        Returns:
            A dictionary containing the parsed JSON payload.

        Raises:
            AppException: If parsing fails.
        """
        raw_stripped = raw_text.strip()

        # Clean up markdown formatting if present
        if raw_stripped.startswith("```json"):
            raw_stripped = raw_stripped[7:]
        elif raw_stripped.startswith("```"):
            raw_stripped = raw_stripped[3:]

        if raw_stripped.endswith("```"):
            raw_stripped = raw_stripped[:-3]

        raw_stripped = raw_stripped.strip()

        try:
            parsed_data = cast(dict[str, Any], json.loads(raw_stripped))

            # If it's a list, wrap it in a root object if necessary, or just return it.
            # Our schemas usually expect a dict.
            if isinstance(parsed_data, list):
                return {"data": parsed_data}

            return parsed_data

        except json.JSONDecodeError as e:
            raise AppException(
                status_code=500,
                message="Malformed JSON in LLM output.",
                details={"error_code": ErrorCodes.PARSING_FAILED.value, "json_error": str(e), "raw_payload": raw_text},
            ) from e

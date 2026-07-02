"""Universal Ingress Pipeline for LLM execution outputs.

Provides a unified entry point for parsing LLM output strings into dictionaries
before they are hydrated by Pydantic models. Relies entirely on Native Structured
Outputs, stripping basic Markdown formatting if present.
The legacy Hybrid XML Protocol has been deprecated.
"""

import json
import logging
from typing import Any, cast

from json_repair import repair_json
from pydantic import BaseModel

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)


class UniversalIngress:
    """Handles parsing for LLM outputs."""

    @classmethod
    def clean_dict_against_model(cls, data: Any, model_class: type[BaseModel]) -> Any:
        """Acts as an Anti-Corruption Layer (ACL) for the LLM boundary.

        Recursively cleans the parsed JSON dictionary against the target Pydantic model.
        1. Strips any hallucinated keys not present in the Pydantic schema (extra_forbidden).
        2. Converts null to "" for strictly string fields to prevent string_type null crashes.

        Args:
            data: The raw dictionary from json.loads.
            model_class: The target Pydantic BaseModel class.

        Returns:
            The cleaned dictionary, ready for strict model_validate().
        """
        if not isinstance(data, dict):
            return data

        cleaned = {}
        fields = model_class.model_fields

        for key, field_info in fields.items():
            if key in data:
                val = data[key]
                target_key = key
            elif field_info.alias and field_info.alias in data:
                val = data[field_info.alias]
                target_key = field_info.alias
            else:
                continue

            annotation = field_info.annotation

            # Handle Nested Models
            if isinstance(val, dict) and isinstance(annotation, type) and issubclass(annotation, BaseModel):
                cleaned[target_key] = cls.clean_dict_against_model(val, annotation)
            # Handle Lists of Models
            elif isinstance(val, list) and annotation:
                # Very basic check for list[BaseModel]
                inner_type = None
                # Simplistic extraction of inner type
                if hasattr(annotation, "__args__") and len(annotation.__args__) > 0:
                    inner_type = annotation.__args__[0]

                if isinstance(inner_type, type) and issubclass(inner_type, BaseModel):
                    cleaned[target_key] = [
                        cls.clean_dict_against_model(item, inner_type) if isinstance(item, dict) else item
                        for item in val
                    ]
                else:
                    cleaned[target_key] = val
            else:
                # Handle null -> "" for strict string fields (NOT Optional[str])
                # If annotation is exactly 'str', convert None to ""
                if val is None and annotation is str:
                    cleaned[target_key] = ""
                else:
                    cleaned[target_key] = val

        return cleaned

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
            AppException: If parsing fails (ErrorCodes.PARSING_FAILED).
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
        except json.JSONDecodeError as e:
            original_error = str(e)
            try:
                repaired_obj = repair_json(raw_stripped, return_objects=True)
                if not isinstance(repaired_obj, (dict, list)):
                    raise ValueError(f"json_repair returned unexpected type: {type(repaired_obj)}")
                parsed_data = cast(dict[str, Any], repaired_obj)
                logger.warning(f"[UniversalIngress] Self-healing successful for JSONDecodeError: {original_error}")
            except Exception as repair_e:
                raise AppException(
                    status_code=500,
                    message="Malformed JSON in LLM output. Self-healing failed.",
                    details={
                        "error_code": ErrorCodes.PARSING_FAILED.value,
                        "json_error": original_error,
                        "repair_error": str(repair_e),
                        "raw_payload": raw_text,
                    },
                ) from e

        # If it's a list, wrap it in a root object if necessary, or just return it.
        # Our schemas usually expect a dict.
        if isinstance(parsed_data, list):
            return {"data": parsed_data}

        return parsed_data

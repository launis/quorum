"""Universal Ingress Pipeline for LLM execution outputs.

Provides a unified entry point for parsing LLM output strings into dictionaries
before they are hydrated by Pydantic models. Relies entirely on Native Structured
Outputs, stripping basic Markdown formatting if present.
The legacy Hybrid XML Protocol has been deprecated.
"""

import json
import logging
import re
import types
from typing import Annotated, Any, Union, cast, get_args, get_origin

from json_repair import repair_json
from pydantic import BaseModel, Discriminator
from pydantic.fields import FieldInfo

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)

_CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


class UniversalIngress:
    """Handles parsing for LLM outputs."""

    @classmethod
    def sanitize_control_chars(cls, text: str) -> str:
        r"""Sanitize non-printable ASCII control characters from strings.

        Preserves standard whitespace characters (\n, \r, \t) while stripping
        low-level control codes (e.g. U+0000-U+0008, U+000B, U+000C, U+000E-U+001F, U+007F)
        such as EOT (0x04) or ACK (0x06).
        """
        return _CONTROL_CHAR_RE.sub("", text)

    @classmethod
    def _extract_discriminator_info(cls, annotation: Any) -> tuple[str | None, list[type[BaseModel]]]:
        """Extract discriminator field name and candidate model types from an annotation.

        Args:
            annotation: Type annotation (may be Annotated[Union[...], Field(discriminator=...)], Union, etc.).

        Returns:
            Tuple of (discriminator_field_name or None, list of BaseModel variant classes).
        """
        if annotation is None:
            return None, []

        origin = get_origin(annotation)
        discriminator_field: str | None = None
        target_union: Any = None
        union_types = (Union, getattr(types, "UnionType", Union))

        if origin is Annotated:
            args = get_args(annotation)
            if args:
                target_union = args[0]
                for meta in args[1:]:
                    if isinstance(meta, Discriminator) and isinstance(meta.discriminator, str):
                        discriminator_field = meta.discriminator
                    elif isinstance(meta, FieldInfo) and meta.discriminator:
                        if isinstance(meta.discriminator, str):
                            discriminator_field = meta.discriminator
                        elif isinstance(meta.discriminator, Discriminator) and isinstance(
                            meta.discriminator.discriminator, str
                        ):
                            discriminator_field = meta.discriminator.discriminator
        elif origin in union_types:
            target_union = annotation
        elif isinstance(annotation, type) and issubclass(annotation, BaseModel):
            return None, [annotation]

        candidate_models: list[type[BaseModel]] = []
        if target_union is not None:
            union_origin = get_origin(target_union)
            if union_origin in union_types:
                union_args = get_args(target_union)
            else:
                union_args = (target_union,)

            for u_arg in union_args:
                u_origin = get_origin(u_arg)
                if u_origin is Annotated:
                    sub_args = get_args(u_arg)
                    if sub_args and isinstance(sub_args[0], type) and issubclass(sub_args[0], BaseModel):
                        candidate_models.append(sub_args[0])
                elif isinstance(u_arg, type) and issubclass(u_arg, BaseModel):
                    candidate_models.append(u_arg)

        return discriminator_field, candidate_models

    @classmethod
    def _infer_and_heal_discriminator(
        cls,
        item: dict[str, Any],
        discriminator_field: str,
        candidate_models: list[type[BaseModel]],
    ) -> type[BaseModel] | None:
        """Infer matching variant model and heal missing discriminator tag in-place.

        Args:
            item: The raw dictionary item to inspect and heal.
            discriminator_field: The name of the discriminator property (e.g. 'block_type').
            candidate_models: List of possible variant Pydantic models.

        Returns:
            The matched BaseModel class, or None if no match found.
        """
        # If discriminator is already present, match directly by literal tag
        current_tag = item.get(discriminator_field)
        if current_tag is not None:
            for model in candidate_models:
                f_info = model.model_fields.get(discriminator_field)
                if f_info:
                    # Check default value
                    if f_info.default == current_tag:
                        return model
                    # Check literal annotation
                    lit_args = get_args(f_info.annotation)
                    if current_tag in lit_args:
                        return model
            # Fallback to first matching model with that field
            for model in candidate_models:
                if discriminator_field in model.model_fields:
                    return model
            return None

        # Heuristic inference when discriminator tag was omitted by LLM
        # 1. AlertBlock / warning / error signatures
        if "severity" in item:
            for model in candidate_models:
                if "severity" in model.model_fields and discriminator_field in model.model_fields:
                    disc_info = model.model_fields[discriminator_field]
                    tag = disc_info.default or (
                        get_args(disc_info.annotation)[0] if get_args(disc_info.annotation) else None
                    )
                    if tag:
                        item[discriminator_field] = tag
                        return model

        # 2. BulletListBlock signature
        if "items" in item and isinstance(item.get("items"), list):
            for model in candidate_models:
                if "items" in model.model_fields and discriminator_field in model.model_fields:
                    disc_info = model.model_fields[discriminator_field]
                    tag = disc_info.default or (
                        get_args(disc_info.annotation)[0] if get_args(disc_info.annotation) else None
                    )
                    if tag:
                        item[discriminator_field] = tag
                        return model

        # 3. SduiQuoteCard / quote signature
        if ("quote" in item or "source_aliases" in item) and "quote" in item:
            for model in candidate_models:
                if "quote" in model.model_fields and discriminator_field in model.model_fields:
                    disc_info = model.model_fields[discriminator_field]
                    tag = disc_info.default or (
                        get_args(disc_info.annotation)[0] if get_args(disc_info.annotation) else None
                    )
                    if tag:
                        item[discriminator_field] = tag
                        return model

        # 4. SduiWarningCard signature (has message and optionally quote_text, but not text)
        if "message" in item and "text" not in item:
            for model in candidate_models:
                if "message" in model.model_fields and discriminator_field in model.model_fields:
                    disc_info = model.model_fields[discriminator_field]
                    tag = disc_info.default or (
                        get_args(disc_info.annotation)[0] if get_args(disc_info.annotation) else None
                    )
                    if tag:
                        item[discriminator_field] = tag
                        return model

        # 5. ParagraphBlock signature (has text)
        if "text" in item:
            for model in candidate_models:
                if (
                    "text" in model.model_fields
                    and discriminator_field in model.model_fields
                    and "severity" not in model.model_fields
                ):
                    disc_info = model.model_fields[discriminator_field]
                    tag = disc_info.default or (
                        get_args(disc_info.annotation)[0] if get_args(disc_info.annotation) else None
                    )
                    if tag:
                        item[discriminator_field] = tag
                        return model

        # 6. Best-effort match based on key overlap
        best_model: type[BaseModel] | None = None
        best_score = -1
        for model in candidate_models:
            model_keys = set(model.model_fields.keys())
            overlap = len(set(item.keys()) & model_keys)
            if overlap > best_score:
                best_score = overlap
                best_model = model

        if best_model and discriminator_field in best_model.model_fields:
            disc_info = best_model.model_fields[discriminator_field]
            tag = disc_info.default or (get_args(disc_info.annotation)[0] if get_args(disc_info.annotation) else None)
            if tag:
                item[discriminator_field] = tag
            return best_model

        return None

    @classmethod
    def _clean_value_against_annotation(cls, val: Any, annotation: Any, discriminator: Any = None) -> Any:
        """Clean a single value or collection against its type annotation."""
        if val is None:
            if annotation is str:
                return ""
            return None

        origin = get_origin(annotation)

        # Handle list[...]
        if isinstance(val, list):
            if origin is list or annotation is list:
                args = get_args(annotation)
                inner_annotation = args[0] if args else None
                if inner_annotation:
                    disc_name, candidate_models = cls._extract_discriminator_info(inner_annotation)
                    if not disc_name and isinstance(discriminator, str):
                        disc_name = discriminator
                    cleaned_list = []
                    for item in val:
                        if isinstance(item, dict):
                            item_copy = dict(item)
                            if disc_name and candidate_models:
                                matched_model = cls._infer_and_heal_discriminator(
                                    item_copy, disc_name, candidate_models
                                )
                                if matched_model:
                                    cleaned_sub = cls.clean_dict_against_model(item_copy, matched_model)
                                    if disc_name in item_copy and disc_name not in cleaned_sub:
                                        cleaned_sub[disc_name] = item_copy[disc_name]
                                    cleaned_list.append(cleaned_sub)
                                else:
                                    cleaned_list.append(item_copy)
                            elif candidate_models and len(candidate_models) == 1:
                                cleaned_list.append(cls.clean_dict_against_model(item_copy, candidate_models[0]))
                            else:
                                cleaned_list.append(item_copy)
                        else:
                            cleaned_list.append(cls.sanitize_control_chars(item) if isinstance(item, str) else item)
                    return cleaned_list
            return val

        # Handle nested dict
        if isinstance(val, dict):
            val_copy = dict(val)
            disc_name, candidate_models = cls._extract_discriminator_info(annotation)
            if not disc_name and isinstance(discriminator, str):
                disc_name = discriminator
            elif (
                not disc_name
                and isinstance(discriminator, Discriminator)
                and isinstance(discriminator.discriminator, str)
            ):
                disc_name = discriminator.discriminator

            if disc_name and candidate_models:
                matched_model = cls._infer_and_heal_discriminator(val_copy, disc_name, candidate_models)
                if matched_model:
                    cleaned_sub = cls.clean_dict_against_model(val_copy, matched_model)
                    if disc_name in val_copy and disc_name not in cleaned_sub:
                        cleaned_sub[disc_name] = val_copy[disc_name]
                    return cleaned_sub
            elif candidate_models and len(candidate_models) == 1:
                return cls.clean_dict_against_model(val_copy, candidate_models[0])
            return val

        # Handle primitive types
        if val is None and annotation is str:
            return ""
        if isinstance(val, str):
            return cls.sanitize_control_chars(val)

        return val

    @classmethod
    def clean_dict_against_model(cls, data: Any, model_class: type[BaseModel]) -> Any:
        """Acts as an Anti-Corruption Layer (ACL) for the LLM boundary.

        Recursively cleans the parsed JSON dictionary against the target Pydantic model.
        1. Strips any hallucinated keys not present in the Pydantic schema (extra_forbidden).
        2. Converts null to "" for strictly string fields to prevent string_type null crashes.
        3. Supports discriminated unions (e.g. AnySduiBlock, LlmSduiBlock) by identifying
           and validating against the appropriate variant model.

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

            cleaned[target_key] = cls._clean_value_against_annotation(
                val, field_info.annotation, discriminator=field_info.discriminator
            )

        # Retain any discriminator tag that was injected or present in data
        for k, v in data.items():
            if k not in cleaned and k in fields:
                cleaned[k] = v

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
        raw_stripped = cls.sanitize_control_chars(raw_text).strip()

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

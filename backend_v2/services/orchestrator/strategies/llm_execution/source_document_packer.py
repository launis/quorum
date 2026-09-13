"""Source document packer for TDA and LLM evaluation strategies."""

import logging
from typing import Any

from pydantic import TypeAdapter, ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.state import StepOutputDTO
from backend_v2.models.v2_core import ExpectedInput

logger = logging.getLogger(__name__)


class SourceDocumentPacker:
    """Utility for packing heterogeneous input documents and prior step outputs.

    Emits inline `<ai_context_directive>` paragraph headers preceding document content,
    and `<step_output step_id="...">` blocks for prior execution step outputs.
    These headers survive TDAEngine paragraph splitting by remaining self-contained within
    their own paragraph blocks rather than enclosing child paragraphs in multiline XML wrappers.
    Distinct from `<ai_context_mandate>`, which is reserved for prompt compiler system prompts.
    """

    @staticmethod
    def resolve_allowed_keys(input_mappings: dict[str, str] | None) -> set[str]:
        """Resolve explicitly mapped input and step keys from step input mappings.

        Parses canonical '$inputs.<key>' values to identify input documents
        targeted for ingestion by the step, and '$steps' or '$steps.<step_id>'
        references to target prior step execution outputs.

        Args:
            input_mappings: Mapping dictionary from step definition,
                e.g. {'doc': '$inputs.product_text', 'prior': '$steps'}.

        Returns:
            Set of resolved input and step document keys.
            Returns an empty set if input_mappings is None or empty.
        """
        if not input_mappings:
            return set()

        allowed: set[str] = set()
        for value in input_mappings.values():
            if not isinstance(value, str):
                continue
            val = value.strip()
            if val.startswith("$inputs."):
                key = val[len("$inputs.") :].strip()
                if key:
                    allowed.add(key)
            elif val == "$steps" or val.startswith("$steps."):
                allowed.add(val)
        return allowed

    @staticmethod
    def pack(
        inputs_payload: Any = None,
        expected_inputs: list[ExpectedInput] | None = None,
        allowed_keys: set[str] | None = None,
        step_outputs: list[StepOutputDTO] | list[Any] | None = None,
    ) -> str:
        """Pack input documents and prior step outputs with inline context directives.

        Args:
            inputs_payload: Raw payload containing a string or key-value dictionary of documents.
            expected_inputs: Optional workflow definitions containing input keys and ai_descriptions.
            allowed_keys: Optional set of allowed input/step keys. If provided and empty, returns empty string.
                When populated, filters dictionary payload and prior step outputs to include only matching keys.
            step_outputs: Optional collection of prior StepOutputDTO objects from execution snapshot.

        Returns:
            Formatted document string with inline directives, or an empty string if empty.

        Raises:
            AppException: If inputs_payload fails validation or a specifically mapped step is missing.
        """
        if not inputs_payload and not step_outputs:
            return ""

        if allowed_keys is not None and len(allowed_keys) == 0:
            return ""

        sections: list[str] = []

        # 1. Process inputs_payload if present and not exclusively step-scoped
        has_input_keys = allowed_keys is None or any(not k.startswith("$steps") for k in allowed_keys)

        if inputs_payload and has_input_keys:
            meta_map: dict[str, str] = {}
            if expected_inputs:
                for ei in expected_inputs:
                    if ei.ai_description and ei.ai_description.strip():
                        meta_map[ei.input_key] = ei.ai_description.strip()

            if isinstance(inputs_payload, str):
                clean_str = inputs_payload.strip()
                if clean_str:
                    sections.append(clean_str)
            else:
                try:
                    dict_payload = TypeAdapter(dict[str, Any]).validate_python(inputs_payload)
                except ValidationError as e:
                    logger.error("[SourceDocumentPacker] Inputs payload validation failed: %s", e)
                    raise AppException(
                        message=f"Inputs payload validation failed: {e}",
                        status_code=500,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    ) from e

                for key, value in dict_payload.items():
                    if allowed_keys is not None and key not in allowed_keys:
                        continue
                    if not isinstance(value, str) or not value.strip():
                        continue
                    clean_value = value.strip()
                    if key in meta_map:
                        directive = meta_map[key]
                        dir_tag = f'<ai_context_directive document="{key}">{directive}</ai_context_directive>'
                        sections.append(f"{dir_tag}\n\n{clean_value}")
                    else:
                        sections.append(clean_value)

        # 2. Process step_outputs if present and step-scoped
        wants_steps = allowed_keys is None or any(k == "$steps" or k.startswith("$steps.") for k in allowed_keys)

        if wants_steps and (step_outputs or (allowed_keys and any(k.startswith("$steps.") for k in allowed_keys))):
            specific_step_targets: set[str] = set()
            wildcard_steps = allowed_keys is None or "$steps" in allowed_keys
            if allowed_keys is not None:
                for k in allowed_keys:
                    if k.startswith("$steps."):
                        target = k[len("$steps.") :].strip()
                        if target:
                            specific_step_targets.add(target)

            available_step_ids: set[str] = set()
            prior_steps_list: list[tuple[str, str]] = []

            if step_outputs:
                for item in step_outputs:
                    try:
                        dto = (
                            item
                            if isinstance(item, StepOutputDTO)
                            else TypeAdapter(StepOutputDTO).validate_python(item)
                        )
                        s_id = dto.step_id
                        payload = dto.payload
                    except ValidationError as e:
                        logger.error("[SourceDocumentPacker] Invalid StepOutputDTO item: %s", e)
                        raise AppException(
                            message=f"Invalid StepOutputDTO item: {e}",
                            status_code=500,
                            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                        ) from e

                    if s_id in ("inputs", "raw_inputs"):
                        continue

                    available_step_ids.add(s_id)

                    text_content = ""
                    if isinstance(payload, str):
                        text_content = payload.strip()
                    else:
                        try:
                            dict_data = TypeAdapter(dict[str, Any]).validate_python(payload)
                            for field in ("text", "markdown", "content"):
                                if field in dict_data:
                                    field_val = dict_data[field]
                                    if isinstance(field_val, str):
                                        text_content = field_val.strip()
                                        break
                        except ValidationError:
                            text_content = ""

                    if text_content:
                        prior_steps_list.append((s_id, text_content))

            # Fail-fast check: if specific step targets were requested, all must exist in available_step_ids
            if specific_step_targets:
                missing_targets = specific_step_targets - available_step_ids
                if missing_targets:
                    missing_sorted = sorted(list(missing_targets))
                    msg = f"Strict Fail-Fast: Mapped step(s) {missing_sorted} not found in prior step outputs."
                    logger.error("[SourceDocumentPacker] %s", msg)
                    raise AppException(
                        message=msg,
                        status_code=400,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    )

            for s_id, text in prior_steps_list:
                if wildcard_steps or s_id in specific_step_targets:
                    sections.append(f'<step_output step_id="{s_id}">\n\n{text}\n\n</step_output>')

        return "\n\n".join(sections)

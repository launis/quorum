"""Source document packer for TDA and LLM evaluation strategies."""

import json
import logging
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, TypeAdapter, ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.state import StepOutputDTO
from backend_v2.models.v2_core import ExpectedInput

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PriorStepOutput:
    """Internal container for resolved prior step outputs."""

    step_id: str
    block_id: str
    text_content: str


_dict_adapter: TypeAdapter[dict[str, Any]] = TypeAdapter(dict[str, Any])


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
    def _is_step_target_matched(
        step_id: str,
        compound_target: str,
        specific_targets: set[str],
        is_wildcard: bool,
    ) -> bool:
        """Determines if a prior step output matches the requested target specification.

        Args:
            step_id: Base step identifier.
            compound_target: Formatted step and block identifier (e.g. 'step_id.block_id').
            specific_targets: Set of specifically targeted step references.
            is_wildcard: Whether all steps are requested via wildcard.

        Returns:
            True if the step output should be included in prompt context.
        """
        if is_wildcard:
            return True
        if step_id in specific_targets:
            return True
        if compound_target and compound_target in specific_targets:
            return True
        return False

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
                    dict_payload = _dict_adapter.validate_python(inputs_payload)
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
            available_compound_targets: set[str] = set()
            prior_steps_list: list[PriorStepOutput] = []

            if step_outputs:
                for item in step_outputs:
                    try:
                        dto = (
                            item
                            if isinstance(item, StepOutputDTO)
                            else TypeAdapter(StepOutputDTO).validate_python(item)
                        )
                        s_id = dto.step_id
                        b_id = dto.block_id
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
                    if b_id:
                        available_compound_targets.add(f"{s_id}.{b_id}")

                    text_content = ""
                    if isinstance(payload, str):
                        text_content = payload.strip()
                    else:
                        step_dict_payload: dict[str, Any] | None = None
                        try:
                            raw_data = payload.model_dump(mode="json") if isinstance(payload, BaseModel) else payload
                            step_dict_payload = _dict_adapter.validate_python(raw_data)
                            for field in ("text", "markdown", "content"):
                                if field in step_dict_payload:
                                    field_val = step_dict_payload[field]
                                    if isinstance(field_val, str):
                                        text_content = field_val.strip()
                                        break
                        except ValidationError:
                            step_dict_payload = None

                        if not text_content:
                            should_serialize = isinstance(payload, list)
                            if step_dict_payload is not None and dto.data_type != "text":
                                should_serialize = True

                            if should_serialize and payload:
                                try:
                                    data_to_dump = step_dict_payload if step_dict_payload is not None else payload
                                    text_content = json.dumps(data_to_dump, indent=2, ensure_ascii=False, default=str)
                                except TypeError, ValueError:
                                    text_content = ""

                    if text_content:
                        prior_steps_list.append(PriorStepOutput(step_id=s_id, block_id=b_id, text_content=text_content))

            # Fail-fast check: if specific step targets were requested, all must exist
            if specific_step_targets:
                missing_targets: set[str] = set()
                for target in specific_step_targets:
                    if target not in available_step_ids and target not in available_compound_targets:
                        missing_targets.add(target)

                if missing_targets:
                    missing_sorted = sorted(list(missing_targets))
                    msg = f"Strict Fail-Fast: Mapped step(s) {missing_sorted} not found in prior step outputs."
                    logger.error("[SourceDocumentPacker] %s", msg)
                    raise AppException(
                        message=msg,
                        status_code=400,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    )

            for item in prior_steps_list:
                s_id = item.step_id
                compound = ""
                if b_id:
                    compound = f"{s_id}.{b_id}"
                if SourceDocumentPacker._is_step_target_matched(
                    step_id=s_id,
                    compound_target=compound,
                    specific_targets=specific_step_targets,
                    is_wildcard=wildcard_steps,
                ):
                    sections.append(f'<step_output step_id="{s_id}">\n\n{item.text_content}\n\n</step_output>')

        return "\n\n".join(sections)

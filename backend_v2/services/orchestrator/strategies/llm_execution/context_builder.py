"""Context builder for extracting, sanitizing, and filtering LLM execution context."""

from __future__ import annotations

import copy
import json
import logging
import re
from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel

from backend_v2.core.hook_registry import HookState
from backend_v2.exceptions import AppException, ErrorCodes, TokenLimitExceededError
from backend_v2.models.domain.prompt_blocks import (
    MatrixPromptBlock,
    PersonaPromptBlock,
    ProtocolPromptBlock,
    SystemRulePromptBlock,
)
from backend_v2.models.dtos.prompt import ContextInputValue, LLMContextDataDTO, PromptMappingDTO
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.services.orchestrator.context_router import ContextRouter
from backend_v2.settings import get_settings
from backend_v2.utils.math_utils import resolve_dot_notation

__all__ = ["ContextBuilder"]

logger = logging.getLogger(__name__)


class ContextBuilder:
    """Builds and sanitizes the LLM context data based on input mappings in Phase 9.

    Attributes:
        None
    """

    @staticmethod
    def _process_trace_dtos(
        dtos: list[Any],
        output_profile: Any,
        schema_type: str = "MATRIX",
        schema_map: dict[str, str] | None = None,
    ) -> Any:
        """Strictly validates and prunes a list of StepOutputDTOs based on its database schema type.

        Args:
            dtos: List of dynamic StepOutputDTOs.
            output_profile: The target output presentation profile for filtering.
            schema_type: String representing schema model shape (e.g., 'MATRIX', 'TEXT').
            schema_map: Optional mapping dictionary of step IDs to schema structures.

        Returns:
            The filtered or pruned output structure.

        Raises:
            AppException: Triggered if matrix validation fails or serialization crashes.
        """
        match schema_type:
            case "MATRIX":
                pass
            case _:
                raw = {d.block_id: d.payload for d in dtos}
                return {k: ContextBuilder._project_compressed(v) for k, v in raw.items()}

        pruned_step_output = {}
        for dto in dtos:
            key: str = dto.block_id
            value: Any = dto.payload

            if not key or (schema_map is None) or (key not in schema_map):
                continue

            block_type = schema_map[key]

            match block_type:
                case "MATRIX":
                    if isinstance(value, (str, int, float, bool)) or value is None:
                        logger.error(
                            "Matrix value validation failed. Key: %s is not a dict.",
                            key,
                            exc_info=True,
                        )
                        raise AppException(
                            message=f"Matrix value for '{key}' must be a dict.",
                            status_code=400,
                            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                        )
                    try:
                        pruned = ContextRouter.route_and_prune(value, output_profile)
                        if not pruned:
                            continue

                        pruned_dict = pruned.model_dump()

                        if "evaluated_atoms" in pruned_dict:
                            del pruned_dict["evaluated_atoms"]

                        pruned_step_output[key] = pruned_dict
                    except Exception as e:
                        msg = f"ContextRouter trace pruning failed for block {key}: {e}"
                        logger.error(msg, exc_info=True)
                        raise AppException(
                            message=msg,
                            status_code=500,
                            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                        ) from e
                case _:
                    if value is not None:
                        pruned_step_output[key] = value

        return pruned_step_output

    @staticmethod
    def _project_compressed(obj: Any) -> Any:
        """Build a compressed projection without deep copying.

        Uses Immutable Projection pattern: creates new containers only at
        modified nodes, shares immutable leaf values (str, int, float, bool, None)
        by reference. Original payload is never mutated. No GIL-blocking deepcopy.

        NOTE: obj.model_dump(mode="json") at line 133 is a documented Terminal
        Rendering Boundary for prompt assembly and text serialization, NOT an
        intermediate pipeline data transit handoff.

        Args:
            obj: Dictionary, list, or primitive to project.

        Returns:
            New compressed structure sharing immutable leaves with original.
        """
        if isinstance(obj, list):
            return [ContextBuilder._project_compressed(item) for item in obj]
        elif isinstance(obj, BaseModel):
            return ContextBuilder._project_compressed(obj.model_dump(mode="json"))
        elif isinstance(obj, (str, int, float, bool)) or obj is None:
            return obj
        elif isinstance(obj, Mapping):
            result = {}
            for k, v in obj.items():
                if k in ("shuffled_atoms", "original_text", "raw_content"):
                    continue
                result[k] = ContextBuilder._project_compressed(v)
            return result
        else:
            return obj

    @staticmethod
    def _collect_rule_descriptions(criteria_blocks: list[Any]) -> list[str]:
        """Collect all rule descriptions from criteria blocks for spatial analysis.

        Traverses the PromptBlock hierarchy (block → scales → claims → tda_assertions)
        to extract ai_description and ai_rule_description strings.

        Args:
            criteria_blocks: List of PromptBlock definitions to inspect.

        Returns:
            List of non-empty rule description strings.
        """
        rule_descriptions: list[str] = []
        for block in criteria_blocks:
            match block:
                case MatrixPromptBlock(ai_description=desc) if desc:
                    rule_descriptions.append(desc)
                case SystemRulePromptBlock(instruction_text=text) if text:
                    rule_descriptions.append(text)
                case PersonaPromptBlock(role_enforcement=text) if text:
                    rule_descriptions.append(text)
                case ProtocolPromptBlock(protocol_instructions=text) if text:
                    rule_descriptions.append(text)
            if isinstance(block, MatrixPromptBlock):
                if block.scales:
                    for scale in block.scales:
                        if scale.claims:
                            for claim in scale.claims:
                                if claim.tda_assertions:
                                    for tda in claim.tda_assertions:
                                        rule_desc: str | None = tda.concept_description
                                        if rule_desc:
                                            rule_descriptions.append(rule_desc)
        return rule_descriptions

    @staticmethod
    def apply_spatial_slicing(text: str, criteria_blocks: list[Any] | None) -> str:
        """Applies physical spatial slicing to document text if chronological rules are detected.

        Args:
            text: The raw input string payload to evaluate.
            criteria_blocks: The validation prompt criteria blocks list.

        Returns:
            Slicing trimmed string based on spatial metadata parsing.
        """
        if not criteria_blocks or not isinstance(text, str):
            return text

        rule_descriptions = ContextBuilder._collect_rule_descriptions(criteria_blocks)

        for desc in rule_descriptions:
            desc_lower = desc.lower()
            match = re.search(r"(?:ennen vaihetta|before phase|before stage)\s+([a-zA-Z0-9_]+)", desc_lower)
            if match:
                phase_id = match.group(1)
                patterns = [
                    f"[VAIHE {phase_id}]",
                    f"[PHASE {phase_id}]",
                    f"[STAGE {phase_id}]",
                    f"VAIHE {phase_id}",
                    f"PHASE {phase_id}",
                    f"STAGE {phase_id}",
                ]
                for pat in patterns:
                    idx = text.upper().find(pat.upper())
                    if idx != -1:
                        truncated_chars = len(text) - idx
                        logger.warning(
                            "[SpatialSlicing] Chronology rule detected: '%s'. "
                            "Physically slicing context at delimiter '%s' (index %d). Truncated %d characters.",
                            desc,
                            pat,
                            idx,
                            truncated_chars,
                            extra={"truncated_chars": truncated_chars, "slice_index": idx},
                        )
                        return text[:idx].strip()
        return text

    @classmethod
    def build(
        cls,
        input_mappings: PromptMappingDTO,
        state_data: HookState | Mapping[str, Any],
        output_profile: Any | None = None,
        schema_map: dict[str, str] | None = None,
        criteria_blocks: list[Any] | None = None,
        blueprint_labels: dict[str, str] | None = None,
    ) -> tuple[LLMContextDataDTO, PromptMappingDTO]:
        """Extracts values based on mappings, prunes traces, and enforces token limits.

        Args:
            input_mappings: The PromptMappingDTO defining what to extract.
            state_data: The HookState or Mapping holding execution context and inputs.
            output_profile: Optional output profile to filter matrix extensions.
            schema_map: Optional map of step IDs to 'MATRIX' or 'TEXT' to dictate parsing logic.
            criteria_blocks: Optional list of PromptBlocks for spatial slicing.
            blueprint_labels: Optional dictionary of localized step and input labels.

        Returns:
            A tuple of (llm_context_data, sanitized_input_mappings).

        Raises:
            TokenLimitExceededError: Triggered when token limit is violated.
            AppException: Raised if validation or context parsing fails.
        """
        extracted_raw_inputs: dict[str, ContextInputValue] = {}
        extracted_inputs: dict[str, ContextInputValue] = {}
        extracted_metadata: ExecutionMetadata | None = None
        new_input_mappings: dict[str, str] = {}
        if schema_map is None:
            schema_map = {}

        if isinstance(state_data, HookState):
            extracted_metadata = state_data.metadata
            extracted_raw_inputs = dict(state_data.inputs.raw_inputs)
            if state_data.inputs.dynamic_inputs:
                extracted_raw_inputs["dynamic_inputs"] = copy.deepcopy(dict(state_data.inputs.dynamic_inputs))
        elif isinstance(state_data, Mapping):
            if "metadata" in state_data and isinstance(state_data["metadata"], ExecutionMetadata):
                extracted_metadata = state_data["metadata"]
            if "raw_inputs" in state_data and isinstance(state_data["raw_inputs"], Mapping):
                state_raw = state_data["raw_inputs"]
                if "dynamic_inputs" in state_raw and isinstance(state_raw["dynamic_inputs"], Mapping):
                    extracted_raw_inputs["dynamic_inputs"] = copy.deepcopy(dict(state_raw["dynamic_inputs"]))

        raw_mappings = input_mappings.mappings if isinstance(input_mappings, PromptMappingDTO) else input_mappings

        for _logical_name, path in raw_mappings.items():
            if not isinstance(path, str):
                continue

            clean_path = path[1:] if path.startswith("$") else path

            try:
                if clean_path == "steps" or clean_path.startswith("steps."):
                    resolved_value = None
                else:
                    resolved_value = resolve_dot_notation(state_data, clean_path)

                if isinstance(resolved_value, str):
                    resolved_value = ContextBuilder.apply_spatial_slicing(resolved_value, criteria_blocks)

                def _prune_step_dtos(dtos_list: list[Any]) -> str:
                    steps_group: dict[str, list[Any]] = {}
                    for d in dtos_list:
                        s_id = d.step_id
                        if s_id:
                            steps_group.setdefault(s_id, []).append(d)

                    xml_blocks: list[str] = []
                    for s_id, step_dtos in steps_group.items():
                        if s_id not in schema_map:
                            logger.error(
                                "Fail-Fast: Missing schema mapping for step '%s'.",
                                s_id,
                                exc_info=True,
                            )
                            raise AppException(
                                message=f"Fail-Fast: Missing schema mapping for step '{s_id}'.",
                                status_code=500,
                                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                            )
                        step_type = schema_map[s_id]
                        pruned_data = ContextBuilder._process_trace_dtos(
                            step_dtos, output_profile, step_type, schema_map
                        )
                        source_name = "System"
                        if blueprint_labels and s_id in blueprint_labels:
                            source_name = blueprint_labels[s_id]
                        data_str = json.dumps(pruned_data, ensure_ascii=False)
                        xml_blocks.append(
                            f'<step_result source="{source_name}" step_id="{s_id}">\n{data_str}\n</step_result>'
                        )
                    return "\n".join(xml_blocks)

                if clean_path == "steps":
                    dto_list: list[Any] = []
                    if isinstance(state_data, HookState):
                        if "steps" in state_data.inputs.dynamic_inputs:
                            steps_val = state_data.inputs.dynamic_inputs["steps"]
                            if isinstance(steps_val, list):
                                dto_list = steps_val
                    elif isinstance(state_data, Mapping) and "steps" in state_data:
                        dto_list = state_data["steps"]
                    resolved_value = _prune_step_dtos(dto_list)
                elif (
                    clean_path == "global_context_vars"
                    and not isinstance(resolved_value, (str, int, float, bool, list))
                    and resolved_value is not None
                ):
                    if isinstance(resolved_value, Mapping) and "steps" in resolved_value:
                        resolved_dict = dict(resolved_value)
                        resolved_dict["steps"] = _prune_step_dtos(resolved_value["steps"])
                        resolved_value = resolved_dict

                elif clean_path.startswith("steps."):
                    parts = clean_path.split(".")
                    step_key = parts[1]
                    if step_key not in schema_map:
                        logger.error(
                            "Fail-Fast: Missing schema mapping for step '%s'.",
                            step_key,
                            exc_info=True,
                        )
                        raise AppException(
                            message=f"Fail-Fast: Missing schema mapping for step '{step_key}'.",
                            status_code=500,
                            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                        )
                    step_type = schema_map[step_key]
                    all_steps: list[Any] = []
                    if isinstance(state_data, HookState):
                        if "steps" in state_data.inputs.dynamic_inputs:
                            steps_val = state_data.inputs.dynamic_inputs["steps"]
                            if isinstance(steps_val, list):
                                all_steps = steps_val
                    elif isinstance(state_data, Mapping) and "steps" in state_data:
                        all_steps = state_data["steps"]
                    dtos = [d for d in all_steps if d.step_id == step_key]

                    if len(parts) == 2:
                        pruned_dict = ContextBuilder._process_trace_dtos(dtos, output_profile, step_type, schema_map)
                        source_name = "System"
                        if blueprint_labels and step_key in blueprint_labels:
                            source_name = blueprint_labels[step_key]
                        data_str = json.dumps(pruned_dict, ensure_ascii=False)
                        resolved_value = (
                            f'<step_result source="{source_name}" step_id="{step_key}">\n{data_str}\n</step_result>'
                        )
                    elif len(parts) == 3:
                        block_key = parts[2]
                        matched_dto = next((d for d in dtos if d.block_id == block_key), None)
                        if not matched_dto:
                            logger.error(
                                "Fail-Fast: Block '%s' not found in step '%s'.",
                                block_key,
                                step_key,
                                exc_info=True,
                            )
                            raise AppException(
                                message=f"Fail-Fast: Block '{block_key}' not found in step '{step_key}'.",
                                status_code=500,
                                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                            )
                        resolved_value = matched_dto.payload
                    else:
                        logger.error(
                            "Fail-Fast: Invalid legacy path '%s'.",
                            clean_path,
                            exc_info=True,
                        )
                        raise AppException(
                            message=f"Fail-Fast: Invalid legacy path '{clean_path}'.",
                            status_code=500,
                            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                        )

                val_str = str(resolved_value)
                try:
                    import litellm

                    tokens = litellm.token_counter(model="gpt-4o", text=val_str)
                    limit = get_settings().max_safe_tokens
                    if tokens > limit:
                        msg = f"Mapping '{_logical_name}' exceeded token limit ({tokens} > {limit})."
                        raise TokenLimitExceededError(message=msg)
                except TokenLimitExceededError:
                    raise
                except Exception as e:
                    msg = f"Token counting failed for {_logical_name}: {e}"
                    logger.error(msg, exc_info=True)
                    raise AppException(
                        message=msg,
                        status_code=500,
                        details={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL},
                    ) from e

                if clean_path == "steps" or clean_path.startswith("steps."):
                    extracted_inputs[_logical_name] = copy.deepcopy(resolved_value)
                    new_input_mappings[_logical_name] = f"${_logical_name}"
                else:
                    parts = clean_path.split(".")
                    curr_node: Any = extracted_inputs
                    for i, part in enumerate(parts):
                        if i == len(parts) - 1:
                            curr_node[part] = copy.deepcopy(resolved_value)
                        else:
                            if part not in curr_node or not isinstance(curr_node[part], Mapping):
                                curr_node[part] = {}
                            curr_node = curr_node[part]
                    extracted_inputs[_logical_name] = copy.deepcopy(resolved_value)
                    new_input_mappings[_logical_name] = path
            except Exception as e:
                if isinstance(e, (TokenLimitExceededError, AppException)):
                    raise
                msg = f"Failed to resolve input mapping {path}: {e}"
                logger.error(msg, exc_info=True)
                raise AppException(
                    message=msg,
                    status_code=400,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from e

        final_raw_inputs = None
        if extracted_raw_inputs:
            final_raw_inputs = extracted_raw_inputs

        final_inputs = None
        if extracted_inputs:
            final_inputs = extracted_inputs

        return (
            LLMContextDataDTO(
                raw_inputs=final_raw_inputs,
                metadata=extracted_metadata,
                inputs=final_inputs,
            ),
            PromptMappingDTO(mappings=new_input_mappings),
        )

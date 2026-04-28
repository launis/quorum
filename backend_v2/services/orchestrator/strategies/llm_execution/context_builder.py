import copy
import json
import logging
from typing import Any

import litellm

from backend_v2.exceptions import AppException, ErrorCodes, TokenLimitExceededError
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
from backend_v2.models.enums import SystemConcurrency
from backend_v2.services.orchestrator.context_router import ContextRouter
from backend_v2.utils.dict_utils import resolve_dot_notation

logger = logging.getLogger(__name__)


class ContextBuilder:
    """Builds and sanitizes the LLM context data based on input mappings."""

    @staticmethod
    def _process_trace_dtos(
        dtos: list[Any], output_profile: Any, schema_type: str = "MATRIX", schema_map: dict[str, str] | None = None
    ) -> Any:
        """Strictly validates and prunes a list of StepOutputDTOs based on its database schema type.

        If schema_type is 'MATRIX', it strictly validates against LightweightMatrixOutput.
        If schema_type is 'TEXT' or anything else, it reconstructs a flat dictionary.
        Raises AppException if a MATRIX trace is invalid.
        """
        match schema_type:
            case "MATRIX":
                pass
            case _:
                return {d.block_id: d.payload for d in dtos}

        pruned_step_output = {}
        for dto in dtos:
            key = getattr(dto, "block_id", None)
            value = getattr(dto, "payload", None)

            if not key or (schema_map is None) or (key not in schema_map):
                continue

            block_type = schema_map[key]

            match block_type:
                case "MATRIX":
                    if not isinstance(value, dict):
                        raise AppException(
                            message=f"Matrix value for '{key}' must be a dict.",
                            status_code=400,
                            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                        )
                    try:
                        matrix_dto = LightweightMatrixOutput.model_validate(value)
                        pruned = ContextRouter.route_and_prune(value, output_profile)
                        if not pruned:
                            continue

                        pruned_dump = pruned.model_dump()
                        if not isinstance(pruned_dump, dict):
                            continue
                        pruned_dict: dict[str, Any] = pruned_dump

                        if "evaluated_atoms" in pruned_dict:
                            del pruned_dict["evaluated_atoms"]

                        pruned_dict["raw_result"] = f"{matrix_dto.raw_score} / {len(matrix_dto.evaluated_atoms)}"
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

    @classmethod
    def build(
        cls,
        input_mappings: dict[str, Any],
        state_data: dict[str, Any],
        output_profile: Any | None = None,
        schema_map: dict[str, str] | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Extracts values based on mappings, prunes traces, and enforces token limits.

        Args:
            input_mappings: The mapping dictionary defining what to extract.
            state_data: The state dictionary.
            output_profile: Optional output profile to filter matrix extensions.
            schema_map: Optional map of step IDs to 'MATRIX' or 'TEXT' to dictate parsing logic.

        Returns:
            A tuple of (llm_context_data, sanitized_input_mappings).
        """
        llm_context_data: dict[str, Any] = {}
        new_input_mappings: dict[str, Any] = {}

        schema_map = schema_map or {}

        for _logical_name, path in input_mappings.items():
            if not isinstance(path, str):
                continue

            clean_path = path[1:] if path.startswith("$") else path

            try:
                if clean_path == "steps" or clean_path.startswith("steps."):
                    resolved_value = None
                else:
                    resolved_value = resolve_dot_notation(state_data, clean_path)

                # Epic 43 Phase 3: Strict List Filtering
                def _prune_step_dtos(dtos_list: list[Any]) -> str:
                    pruned_steps = {}
                    steps_group: dict[str, list[Any]] = {}
                    for d in dtos_list:
                        s_id = getattr(d, "step_id", None)
                        if s_id:
                            steps_group.setdefault(s_id, []).append(d)

                    for s_id, step_dtos in steps_group.items():
                        if s_id not in schema_map:
                            raise AppException(
                                message=f"Fail-Fast: Missing schema mapping for step '{s_id}'.",
                                status_code=500,
                                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                            )
                        step_type = schema_map[s_id]
                        pruned_steps[s_id] = ContextBuilder._process_trace_dtos(
                            step_dtos, output_profile, step_type, schema_map
                        )
                    return f"<matrix_data>\n{json.dumps(pruned_steps)}\n</matrix_data>"

                if clean_path == "steps":
                    dto_list = state_data.get("steps", [])
                    resolved_value = _prune_step_dtos(dto_list)
                elif clean_path == "global_context_vars" and isinstance(resolved_value, dict):
                    resolved_value = copy.copy(resolved_value)
                    if "steps" in resolved_value:
                        resolved_value["steps"] = _prune_step_dtos(resolved_value["steps"])
                elif clean_path.startswith("steps."):
                    parts = clean_path.split(".")
                    step_key = parts[1]
                    if step_key not in schema_map:
                        raise AppException(
                            message=f"Fail-Fast: Missing schema mapping for step '{step_key}'.",
                            status_code=500,
                            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                        )
                    step_type = schema_map[step_key]
                    dtos = [d for d in state_data.get("steps", []) if getattr(d, "step_id", None) == step_key]

                    if len(parts) == 2:
                        pruned_dict = ContextBuilder._process_trace_dtos(dtos, output_profile, step_type, schema_map)
                        resolved_value = f"<matrix_data>\n{json.dumps(pruned_dict)}\n</matrix_data>"
                    elif len(parts) == 3:
                        # Exact block match
                        block_key = parts[2]
                        matched_dto = next((d for d in dtos if getattr(d, "block_id", None) == block_key), None)
                        if not matched_dto:
                            raise AppException(
                                message=f"Fail-Fast: Block '{block_key}' not found in step '{step_key}'.",
                                status_code=500,
                                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                            )
                        resolved_value = getattr(matched_dto, "payload", None)
                    else:
                        raise AppException(
                            message=f"Fail-Fast: Invalid legacy path '{clean_path}'.",
                            status_code=500,
                            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                        )

                val_str = str(resolved_value)
                # Task 2: Rigorous token checks
                try:
                    tokens = litellm.token_counter(model="gpt-4o", text=val_str)
                    limit = SystemConcurrency.MAX_SAFE_TOKENS.value
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
                        details={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.value},
                    ) from e

                # Map back to llm_context_data in its original path structure so _extract_value_from_state works
                parts = clean_path.split(".")
                if clean_path.startswith("steps."):
                    parts = clean_path[len("steps.") :].split(".")

                curr = llm_context_data
                for i, part in enumerate(parts):
                    if i == len(parts) - 1:
                        curr[part] = copy.deepcopy(resolved_value)
                    else:
                        if part not in curr:
                            curr[part] = {}
                        curr = curr[part]

                new_input_mappings[_logical_name] = path
            except Exception as e:
                if isinstance(e, TokenLimitExceededError) or isinstance(e, AppException):
                    raise
                msg = f"Failed to resolve input mapping {path}: {e}"
                logger.error(msg, exc_info=True)
                raise AppException(
                    message=msg,
                    status_code=400,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from e

        return llm_context_data, new_input_mappings

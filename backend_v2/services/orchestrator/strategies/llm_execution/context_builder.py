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
    def _process_trace_event(trace_data: Any, output_profile: Any) -> dict[str, Any]:
        """Strictly validates and prunes a single trace event. Raises AppException if invalid."""
        if not isinstance(trace_data, dict):
            raise AppException(
                message="Trace data must be a strictly typed dictionary.",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        matrix_dto = LightweightMatrixOutput.model_validate(trace_data)
        try:
            pruned = ContextRouter.route_and_prune(trace_data, output_profile)
            pruned_dict = pruned.model_dump()
            pruned_dict["evaluations_bool_only"] = list(matrix_dto.evaluated_atoms.values())
            return pruned_dict
        except Exception as e:
            msg = f"ContextRouter trace pruning failed: {e}"
            logger.error(msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from e

    @classmethod
    def build(
        cls,
        input_mappings: dict[str, Any],
        state_data: dict[str, Any],
        output_profile: Any | None = None,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Extracts values based on mappings, prunes traces, and enforces token limits.

        Returns:
            A tuple of (llm_context_data, sanitized_input_mappings).
        """
        llm_context_data: dict[str, Any] = {}
        new_input_mappings: dict[str, Any] = {}

        for _logical_name, path in input_mappings.items():
            if not isinstance(path, str):
                continue

            clean_path = path[1:] if path.startswith("$") else path

            try:
                resolved_value = resolve_dot_notation(state_data, clean_path)

                # Task 3: ContextRouter integration for trace data
                def _prune_steps_dict(steps_dict: dict[str, Any]) -> str:
                    pruned_steps = {}
                    for s_id, s_val in steps_dict.items():
                        pruned_steps[s_id] = ContextBuilder._process_trace_event(s_val, output_profile)
                    return f"<matrix_data>\n{json.dumps(pruned_steps)}\n</matrix_data>"

                if clean_path == "steps" and isinstance(resolved_value, dict):
                    resolved_value = _prune_steps_dict(resolved_value)
                elif clean_path == "global_context_vars" and isinstance(resolved_value, dict):
                    resolved_value = copy.copy(resolved_value)
                    if "steps" in resolved_value and isinstance(resolved_value["steps"], dict):
                        resolved_value["steps"] = _prune_steps_dict(resolved_value["steps"])
                elif clean_path.startswith("steps."):
                    pruned_dict = ContextBuilder._process_trace_event(resolved_value, output_profile)
                    resolved_value = f"<matrix_data>\n{json.dumps(pruned_dict)}\n</matrix_data>"

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
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
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

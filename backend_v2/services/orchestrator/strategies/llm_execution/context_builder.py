import copy
import logging
from typing import Any

import litellm

from backend_v2.exceptions import AppException, ErrorCodes, TokenLimitExceededError
from backend_v2.services.orchestrator.context_router import ContextRouter
from backend_v2.utils.dict_utils import resolve_dot_notation

logger = logging.getLogger(__name__)


class ContextBuilder:
    """Builds and sanitizes the LLM context data based on input mappings."""

    MAX_SAFE_TOKENS = 100000

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
                    import json

                    for s_id, s_val in steps_dict.items():
                        if isinstance(s_val, dict):
                            if "normalized_score" in s_val:
                                try:
                                    pruned = ContextRouter.route_and_prune(s_val, output_profile)
                                    pruned_steps[s_id] = pruned.model_dump()
                                except Exception as e:
                                    logger.warning(f"ContextRouter trace pruning failed for step {s_id}: {e}")
                                    pruned_steps[s_id] = s_val
                            elif "atoms" in s_val:
                                atoms = s_val["atoms"]
                                count = len(atoms) if isinstance(atoms, list) else 0
                                pruned_steps[s_id] = {"status": "omitted_raw_atoms", "count": count}
                            elif "history_text" in s_val or "extracted_text" in s_val:
                                pruned_steps[s_id] = {"status": "omitted_raw_input_data"}
                            elif "evaluations" in s_val:
                                evs = s_val["evaluations"]
                                if isinstance(evs, list):
                                    pruned_steps[s_id] = {
                                        "evaluations_bool_only": [
                                            bool(e.get("boolean", False)) if isinstance(e, dict) else False
                                            for e in evs
                                        ]
                                    }
                                else:
                                    pruned_steps[s_id] = {"status": "omitted_raw_evaluations"}
                            else:
                                pruned_steps[s_id] = s_val
                        else:
                            pruned_steps[s_id] = s_val
                    return f"<matrix_data>\n{json.dumps(pruned_steps)}\n</matrix_data>"

                if clean_path == "steps" and isinstance(resolved_value, dict):
                    resolved_value = _prune_steps_dict(resolved_value)
                elif clean_path == "global_context_vars" and isinstance(resolved_value, dict):
                    resolved_value = copy.copy(resolved_value)
                    if "steps" in resolved_value and isinstance(resolved_value["steps"], dict):
                        resolved_value["steps"] = _prune_steps_dict(resolved_value["steps"])
                elif clean_path.startswith("steps."):
                    if isinstance(resolved_value, dict):
                        if "normalized_score" in resolved_value:
                            try:
                                pruned = ContextRouter.route_and_prune(resolved_value, output_profile)
                                resolved_value = f"<matrix_data>\n{pruned.model_dump_json()}\n</matrix_data>"
                            except Exception as e:
                                msg = f"ContextRouter trace pruning failed for {_logical_name}: {e}"
                                logger.error(msg, exc_info=True)
                                raise AppException(
                                    message=msg,
                                    status_code=500,
                                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                                ) from e
                        elif "atoms" in resolved_value:
                            atoms = resolved_value["atoms"]
                            count = len(atoms) if isinstance(atoms, list) else 0
                            resolved_value = {"status": "omitted_raw_atoms", "count": count}
                        elif "history_text" in resolved_value or "extracted_text" in resolved_value:
                            resolved_value = {"status": "omitted_raw_input_data"}

                val_str = str(resolved_value)
                # Task 2: Rigorous token checks
                try:
                    tokens = litellm.token_counter(model="gpt-4o", text=val_str)
                    if tokens > cls.MAX_SAFE_TOKENS:
                        msg = f"Mapping '{_logical_name}' exceeded token limit ({tokens} > {cls.MAX_SAFE_TOKENS})."
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

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
                if clean_path.startswith("steps."):
                    if isinstance(resolved_value, dict) and "normalized_score" in resolved_value:
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

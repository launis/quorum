import logging
from typing import Any

from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.lightweight_matrix import AtomEvaluationItemDTO

logger = logging.getLogger(__name__)


class ChunkAccumulator:
    """Safely aggregates multiple chunked responses from an LLM Map-Reduce execution.

    Enforces the 'No Naked Dicts in State' and 'Duct Tape Ban' rules by moving
    raw dictionary manipulation and type checking out of the main orchestrator loop
    into an isolated, testable component.
    """

    def __init__(self) -> None:
        self.final_result: dict[str, Any] = {}

    def add(self, chunk: dict[str, Any]) -> None:
        """Merges a new chunk into the final result."""
        self._merge_evaluations(chunk)
        self._merge_string_traces(chunk)
        self._merge_xai_extensions(chunk)

    def _merge_evaluations(self, chunk: dict[str, Any]) -> None:
        """Safely extends the evaluations array and enforces Fail-Fast validation."""
        if "evaluations" not in chunk:
            return

        if "evaluations" not in self.final_result:
            self.final_result["evaluations"] = []

        chunk_evals = chunk["evaluations"]
        final_evals = self.final_result["evaluations"]

        if not isinstance(chunk_evals, list):
            raise AppException(
                message="Strict Fail-Fast: 'evaluations' chunk must be a list.",
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        for raw_ev in chunk_evals:
            if not isinstance(raw_ev, dict):
                raise AppException(
                    message="Invalid evaluation chunk: evaluation item is not a dictionary.",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

            try:
                AtomEvaluationItemDTO.model_validate(raw_ev)
            except ValidationError as e:
                logger.error("ChunkAccumulator: Validation failed, marking as DLQ. Error: %s", e)
                raw_ev["dlq_status"] = True
                final_evals.append(raw_ev)
                continue

            # We no longer explicitly write mapped_state here because rule_satisfied
            # logic is fully delegated to calculate_rule_satisfied() in the scoring engine.
            final_evals.append(raw_ev)

    def _merge_string_traces(self, chunk: dict[str, Any]) -> None:
        """Safely concatenates high-level string traces like mechanical_trace."""
        for key in ["mechanical_trace", "evaluation_notes"]:
            if key in chunk:
                c_val = chunk[key]
                if key not in self.final_result:
                    self.final_result[key] = c_val
                else:
                    f_val = self.final_result[key]
                    if isinstance(c_val, str) and isinstance(f_val, str):
                        self.final_result[key] = f"{f_val}\n\n[Chunk]: {c_val}"
                    else:
                        raise AppException(
                            message=f"Strict Fail-Fast: Expected string for '{key}', got '{type(c_val)}'.",
                            status_code=500,
                            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                        )

    def _merge_xai_extensions(self, chunk: dict[str, Any]) -> None:
        """Safely merges dynamic matrix or block-level XAI extensions."""
        for k, v in chunk.items():
            if k in ["evaluations", "reasoning_trace", "evaluation_notes"]:
                continue

            if k.startswith("matrix_") or k.startswith("blk_"):
                if k not in self.final_result:
                    self.final_result[k] = v
                else:
                    self._merge_nested_dict(self.final_result[k], v, parent_key=k)

    def _merge_nested_dict(self, target: Any, source: Any, parent_key: str) -> None:
        """Merges two nested dictionaries, concatenating strings if there are collisions."""
        if not isinstance(target, dict) or not isinstance(source, dict):
            raise AppException(
                message=f"Strict Fail-Fast: Cannot merge non-dict XAI extensions for key '{parent_key}'.",
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        for s_key, s_val in source.items():
            if s_key not in target:
                target[s_key] = s_val
            else:
                t_val = target[s_key]
                if s_val is None:
                    continue
                elif t_val is None:
                    target[s_key] = s_val
                elif isinstance(s_val, str) and isinstance(t_val, str):
                    target[s_key] = f"{t_val} {s_val}"
                elif isinstance(s_val, list) and isinstance(t_val, list):
                    t_val.extend(s_val)
                elif isinstance(s_val, bool) and isinstance(t_val, bool):
                    target[s_key] = t_val or s_val
                elif isinstance(s_val, (int, float)) and isinstance(t_val, (int, float)):
                    target[s_key] = min(t_val, s_val)
                elif s_val == t_val:
                    continue
                else:
                    raise AppException(
                        message=(
                            f"Strict Fail-Fast: Unresolvable key collision on '{parent_key}.{s_key}'. "
                            f"Target: {t_val}, Source: {s_val}."
                        ),
                        status_code=500,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    )

    def get_final_result(self) -> dict[str, Any]:
        """Returns the accumulated dictionary."""
        return self.final_result

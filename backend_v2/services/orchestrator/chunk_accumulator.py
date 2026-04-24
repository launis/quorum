import logging
from typing import Any

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
        if not self.final_result:
            # First chunk, initialize state
            self.final_result = chunk
            return

        self._merge_evaluations(chunk)
        self._merge_string_traces(chunk)
        self._merge_xai_extensions(chunk)

    def _merge_evaluations(self, chunk: dict[str, Any]) -> None:
        """Safely extends the evaluations array."""
        if "evaluations" in chunk and "evaluations" in self.final_result:
            chunk_evals = chunk["evaluations"]
            final_evals = self.final_result["evaluations"]
            if isinstance(chunk_evals, list) and isinstance(final_evals, list):
                final_evals.extend(chunk_evals)
            else:
                logger.warning("ChunkAccumulator: 'evaluations' is not a list. Skipping merge.")

    def _merge_string_traces(self, chunk: dict[str, Any]) -> None:
        """Safely concatenates high-level string traces like reasoning_trace."""
        for key in ["reasoning_trace", "evaluation_notes"]:
            if key in chunk and key in self.final_result:
                c_val = chunk[key]
                f_val = self.final_result[key]
                if isinstance(c_val, str) and isinstance(f_val, str):
                    self.final_result[key] = f"{f_val}\n\n[Chunk]: {c_val}"
                else:
                    logger.warning("ChunkAccumulator: '%s' is not a string. Skipping merge.", key)

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
            logger.warning(
                "ChunkAccumulator: Cannot merge non-dict XAI extensions for key '%s'. Target type: %s, Source type: %s",
                parent_key,
                type(target),
                type(source),
            )
            return

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
                elif s_val == t_val:
                    continue
                else:
                    logger.warning(
                        "ChunkAccumulator: Key collision on '%s.%s' with incompatible types. "
                        "Target: %s, Source: %s. Skipping.",
                        parent_key,
                        s_key,
                        type(t_val),
                        type(s_val),
                    )

    def get_final_result(self) -> dict[str, Any]:
        """Returns the accumulated dictionary."""
        return self.final_result

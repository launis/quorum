import logging
from typing import Any

from pydantic import BaseModel, ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.lightweight_matrix import MergedFactsDTO

logger = logging.getLogger(__name__)


class ChunkAccumulator:
    """Safely aggregates multiple chunked responses from an LLM Map-Reduce execution.

    Banish in-flight asynchronous chunk merging to avoid race conditions. Workers
    append pure DynamicExtractionResponse objects to a list. Once all chunks complete,
    executes a single synchronous, deterministic Reducer operation.
    """

    def __init__(self, response_model: type[BaseModel] | None = None) -> None:
        self.response_model = response_model
        self.chunks: list[dict[str, Any]] = []

    def add(self, chunk: dict[str, Any]) -> None:
        """Appends a raw chunk or validated response to the list."""
        if not isinstance(chunk, dict):
            raise AppException(
                message="Strict Fail-Fast: Chunk must be a dictionary.",
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        # Fail-Fast schema validation if response_model is provided
        if self.response_model:
            try:
                self.response_model.model_validate(chunk)
            except ValidationError as e:
                logger.error("ChunkAccumulator: Validation failed. Error: %s", e)
                raise AppException(
                    message=f"Strict Fail-Fast: Chunk validation failed: {e}",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from e

        self.chunks.append(chunk)

    def reduce(self) -> dict[str, Any]:
        """Executes a single synchronous, deterministic Reducer operation."""
        # Sort chunks chronologically by chunk_index to ensure deterministic merging
        sorted_chunks = sorted(self.chunks, key=lambda c: c.get("chunk_index", 0))

        final_result: dict[str, Any] = {}
        merged_facts_dict: dict[str, str | None] = {}

        final_result["mechanical_trace"] = ""
        final_result["evaluation_notes"] = ""
        final_result["reasoning_trace"] = ""

        for chunk in sorted_chunks:
            # First-Wins strategy: Loop and keep the earliest non-null/non-empty text quote for each fact key
            facts = chunk.get("extracted_facts") or {}
            if hasattr(facts, "model_dump"):
                facts = facts.model_dump()
            elif not isinstance(facts, dict):
                facts = {}

            for k, v in facts.items():
                is_val_present = v is not None and str(v).strip() != ""
                if k not in merged_facts_dict:
                    merged_facts_dict[k] = v
                else:
                    current_val = merged_facts_dict[k]
                    is_current_present = current_val is not None and str(current_val).strip() != ""
                    if not is_current_present and is_val_present:
                        merged_facts_dict[k] = v

            # Concatenate high-level string traces safely
            for key in ["mechanical_trace", "evaluation_notes", "reasoning_trace"]:
                if key in chunk and chunk[key]:
                    val = chunk[key]
                    if final_result[key] == "":
                        final_result[key] = val
                    else:
                        final_result[key] = f"{final_result[key]}\n\n[Chunk]: {val}"

            # Accumulate evaluations list if present
            if "evaluations" in chunk and isinstance(chunk["evaluations"], list):
                if "evaluations" not in final_result:
                    final_result["evaluations"] = []
                final_result["evaluations"].extend(chunk["evaluations"])

            # Merge dynamic XAI extensions
            for k, v in chunk.items():
                if k in [
                    "extracted_facts",
                    "chunk_index",
                    "context_scan_trace",
                    "search_context_anchor",
                    "validation_decision",
                ]:
                    continue
                if k in ["mechanical_trace", "evaluation_notes", "reasoning_trace"]:
                    continue
                if k.startswith("matrix_") or k.startswith("blk_"):
                    if k not in final_result:
                        final_result[k] = v
                    else:
                        # Epic 59: Support dynamic primitive merge behavior for
                        # non-dict blocks (e.g. instruction blocks as strings)
                        if isinstance(final_result[k], dict) and isinstance(v, dict):
                            self._merge_nested_dict(final_result[k], v, parent_key=k)
                        elif isinstance(final_result[k], str) and isinstance(v, str):
                            if final_result[k] == v:
                                continue
                            elif not final_result[k].strip():
                                final_result[k] = v
                            elif not v.strip():
                                continue
                            else:
                                final_result[k] = f"{final_result[k]}\n\n[Chunk]: {v}"
                        elif isinstance(final_result[k], list) and isinstance(v, list):
                            final_result[k] = final_result[k] + v
                        elif isinstance(final_result[k], bool) and isinstance(v, bool):
                            final_result[k] = final_result[k] or v
                        elif isinstance(final_result[k], (int, float)) and isinstance(v, (int, float)):
                            final_result[k] = min(final_result[k], v)
                        elif v is None:
                            continue
                        elif final_result[k] is None:
                            final_result[k] = v
                        else:
                            raise AppException(
                                message=(
                                    f"Strict Fail-Fast: Cannot merge mismatched XAI extensions for key '{k}'. "
                                    f"Target type: {type(final_result[k])}, Source type: {type(v)}."
                                ),
                                status_code=500,
                                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                            )

        # Build MergedFactsDTO to enforce strict schemas and banish naked dicts in state transit
        merged_dto = MergedFactsDTO.model_validate(merged_facts_dict)
        final_result["extracted_facts"] = merged_dto.model_dump(mode="json")

        # Clean empty traces so subsequent pipeline checks do not receive empty strings
        for key in ["mechanical_trace", "evaluation_notes", "reasoning_trace"]:
            if key in final_result and final_result[key] == "":
                final_result.pop(key)

        return final_result

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
                    target[s_key] = t_val + s_val
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
        """Returns the accumulated dictionary by executing reduction synchronously."""
        return self.reduce()

"""Synthesis Payload Compressor.

Encapsulates payload compression logic for the synthesis pipeline.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from pydantic import BaseModel, ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.synthesis import DistilledEvaluation, DistilledMatrixPayloadDTO
from backend_v2.models.dtos.atom_result import EvaluatedAtomDTO
from backend_v2.models.dtos.step_output import StepPayloadValue
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

__all__ = ["SynthesisPayloadCompressor"]

_HEAVY_KEYS_TO_EXCLUDE: set[str] = {
    "shuffled_atoms",
    "atom_quotes",
    "hydrated_references",
    "_step_metadata",
    "_audit_signature",
    "_evaluative_matrices",
}


class SynthesisPayloadCompressor:
    """Compresses payloads for synthesis LLM steps by stripping extraneous metadata."""

    @classmethod
    def compress_synthesis_payload(cls, v: BaseModel | StepPayloadValue) -> str:
        """Deep strip heavy Pydantic metadata and AI internal logs before sending to final synthesis.

        Args:
            v: The extracted JSON payload, scalar, or DTO value to compress.

        Returns:
            A stringified JSON dump stripped of extraneous AI inference variables.

        Raises:
            AppException: Triggered with VALIDATION_FAILED if the payload or its inner
                evaluation components are invalid.
        """
        if isinstance(v, (int, float, bool)):
            return str(v)

        if not v:
            logger.error(
                "[SynthesisPayloadCompressor] %s: Cannot compress empty payload.",
                ErrorCodes.VALIDATION_FAILED.name,
            )
            raise AppException(
                message="Cannot compress empty payload.",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        if isinstance(v, str):
            trimmed = v.strip()
            if not trimmed:
                logger.error(
                    "[SynthesisPayloadCompressor] %s: Cannot compress empty string payload.",
                    ErrorCodes.VALIDATION_FAILED.name,
                )
                raise AppException(
                    message="Cannot compress empty string payload.",
                    status_code=400,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )
            return trimmed

        if isinstance(v, BaseModel):
            dumped = v.model_dump(
                mode="json",
                exclude=_HEAVY_KEYS_TO_EXCLUDE,
                exclude_none=True,
            )
            return json.dumps(dumped, ensure_ascii=False, indent=2)

        if not isinstance(v, list):
            try:
                _ = v.items()
            except (AttributeError, TypeError) as e:
                logger.error(
                    "[SynthesisPayloadCompressor] %s: Payload must be a dict, list, string, or scalar for compression.",
                    ErrorCodes.VALIDATION_FAILED.name,
                )
                raise AppException(
                    message="Payload must be a dict, list, string, or scalar for compression.",
                    status_code=400,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from e

        cleaned = cls._clean_and_distill_payload(v)
        return json.dumps(cleaned, ensure_ascii=False, indent=2)

    @staticmethod
    def _prune_and_stratify_evaluations(evals: list[DistilledEvaluation], limit: int) -> list[DistilledEvaluation]:
        """Prune and stratify evaluations with deterministic prioritized stratification.

        When limit == 0: Unbounded mode (forward all without truncation).
        When limit > 0 and len(evals) > limit:
          - Partition into Deficits/Failures (70% budget) and Strengths/Passes.
          - Sort both partitions by (-len(exact_quotes), atom_id).
          - Apply dynamic spillover.
          - Canonically sort by atom_id for byte-for-byte deterministic serialization.

        Args:
            evals: List of distilled evaluations to stratify.
            limit: Maximum count of evaluations to retain (0 for unbounded).

        Returns:
            Stratified and sorted list of distilled evaluations.
        """
        if limit == 0 or len(evals) <= limit:
            return list(evals)

        deficits: list[DistilledEvaluation] = []
        strengths: list[DistilledEvaluation] = []

        for item in evals:
            status = item.status
            if status in ("FAILED", "UNMET", "NON_COMPLIANT"):
                deficits.append(item)
            else:
                strengths.append(item)

        def sort_key(item: DistilledEvaluation) -> tuple[int, str]:
            quotes_count = len(item.exact_quotes)
            atom_id = ""
            if item.atom_id is not None:
                atom_id = item.atom_id
            return (-quotes_count, atom_id)

        deficits.sort(key=sort_key)
        strengths.sort(key=sort_key)

        deficit_budget = int(limit * 0.7)

        if len(deficits) <= deficit_budget:
            selected_deficits = deficits
            strength_budget = limit - len(selected_deficits)
            selected_strengths = strengths[:strength_budget]
        elif len(strengths) <= (limit - deficit_budget):
            selected_strengths = strengths
            deficit_budget_dynamic = limit - len(selected_strengths)
            selected_deficits = deficits[:deficit_budget_dynamic]
        else:
            selected_deficits = deficits[:deficit_budget]
            strength_budget = limit - deficit_budget
            selected_strengths = strengths[:strength_budget]

        selected = selected_deficits + selected_strengths

        def get_atom_id(x: DistilledEvaluation) -> str:
            if x.atom_id is not None:
                return x.atom_id
            return ""

        selected.sort(key=get_atom_id)

        logger.warning(
            "Token Shield: Prioritized stratification applied",
            extra={
                "original_count": len(evals),
                "limit": limit,
                "deficits_retained": len(selected_deficits),
                "strengths_retained": len(selected_strengths),
                "dropped_count": len(evals) - len(selected),
            },
        )
        return selected

    @classmethod
    def _clean_and_distill_payload(cls, val: Any) -> Any:
        """Recursively clean payloads, sanitize results into DistilledMatrixPayloadDTO, and exclude heavy keys.

        Args:
            val: Arbitrary nested value to clean.

        Returns:
            Cleaned, JSON-serializable structure.

        Raises:
            AppException: If results format or evaluation items are invalid.
        """
        if isinstance(val, BaseModel):
            return val.model_dump(
                mode="json",
                exclude=_HEAVY_KEYS_TO_EXCLUDE,
                exclude_none=True,
            )

        if isinstance(val, list):
            return [cls._clean_and_distill_payload(item) for item in val]

        if isinstance(val, (int, float, bool, str)) or val is None:
            return val

        try:
            val_items = val.items()
        except (AttributeError, TypeError) as e:
            logger.error(
                "[SynthesisPayloadCompressor] %s: Unsupported nested payload type: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                type(val).__name__,
            )
            raise AppException(
                message=f"Unsupported nested payload type: {type(val).__name__}",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from e

        filtered: dict[str, Any] = {k: v for k, v in val_items if k not in _HEAVY_KEYS_TO_EXCLUDE}

        if "results" in filtered:
            results_data = filtered["results"]
            if not isinstance(results_data, list):
                logger.error(
                    "[SynthesisPayloadCompressor] %s: 'results' must be a list.",
                    ErrorCodes.VALIDATION_FAILED.name,
                )
                raise AppException(
                    message="'results' must be a list.",
                    status_code=400,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

            settings = get_settings()
            distilled_evals: list[DistilledEvaluation] = []

            for ev in results_data:
                if isinstance(ev, (str, int, float, bool)) or ev is None:
                    logger.error(
                        "[SynthesisPayloadCompressor] %s: Evaluation item must be a dictionary or EvaluatedAtomDTO.",
                        ErrorCodes.VALIDATION_FAILED.name,
                    )
                    raise AppException(
                        message="Evaluation item must be a dictionary or EvaluatedAtomDTO.",
                        status_code=400,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    )

                if isinstance(ev, DistilledEvaluation):
                    distilled_evals.append(ev)
                elif isinstance(ev, EvaluatedAtomDTO):
                    atom_id = ev.atom_id or ev.tda_id
                    valid_quotes = [
                        q.strip()
                        for q in ev.exact_quotes
                        if q.strip()
                        and q.strip() not in ("None", "null", "N/A", "N/A - insufficient data")
                        and not (q.strip().startswith("[") and q.strip().endswith("]"))
                    ]
                    if ev.exact_quotes and not valid_quotes and not ev.evaluation_reasoning:
                        continue

                    reasoning: str | None = None
                    if ev.evaluation_reasoning:
                        reasoning = str(ev.evaluation_reasoning)[: settings.max_synthesis_reasoning_length]
                    distilled_evals.append(
                        DistilledEvaluation(
                            atom_id=atom_id,
                            status=ev.status,
                            exact_quotes=[q[: settings.max_synthesis_quote_length] for q in valid_quotes],
                            semantic_reasoning=reasoning,
                        )
                    )
                else:
                    atom_id_val: Any = None
                    if "atom_id" in ev and ev["atom_id"]:
                        atom_id_val = ev["atom_id"]
                    elif "tda_id" in ev and ev["tda_id"]:
                        atom_id_val = ev["tda_id"]
                    if not atom_id_val:
                        logger.error(
                            "[SynthesisPayloadCompressor] %s: Missing mandatory field in evaluation: 'atom_id'",
                            ErrorCodes.VALIDATION_FAILED.name,
                        )
                        raise AppException(
                            message="Missing mandatory field in evaluation: 'atom_id'",
                            status_code=400,
                            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                        )

                    eval_dict: dict[str, Any] = {"atom_id": str(atom_id_val)}
                    if "exact_quotes" in ev:
                        eval_dict["exact_quotes"] = ev["exact_quotes"]
                    if "semantic_reasoning" in ev:
                        eval_dict["semantic_reasoning"] = ev["semantic_reasoning"]
                    elif "output_text" in ev:
                        eval_dict["semantic_reasoning"] = ev["output_text"]
                    if "status" in ev:
                        eval_dict["status"] = ev["status"]
                    if "extensions" in ev:
                        eval_dict["extensions"] = ev["extensions"]

                    try:
                        parsed_ev = DistilledEvaluation.model_validate(eval_dict)
                    except (ValidationError, ValueError, TypeError) as e:
                        logger.error(
                            "[SynthesisPayloadCompressor] %s: Failed to hydrate evaluation: %s",
                            ErrorCodes.VALIDATION_FAILED.name,
                            str(e),
                        )
                        raise AppException(
                            message=f"Failed to hydrate evaluation: {str(e)}",
                            status_code=400,
                            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                        ) from e

                    valid_quotes = [
                        q.strip()
                        for q in parsed_ev.exact_quotes
                        if q.strip()
                        and q.strip() not in ("None", "null", "N/A", "N/A - insufficient data")
                        and not (q.strip().startswith("[") and q.strip().endswith("]"))
                    ]

                    has_quotes_in_source = "exact_quotes" in ev
                    if has_quotes_in_source and not valid_quotes and not parsed_ev.semantic_reasoning:
                        continue

                    sem_reasoning: str | None = None
                    if parsed_ev.semantic_reasoning:
                        sem_reasoning = str(parsed_ev.semantic_reasoning)[: settings.max_synthesis_reasoning_length]
                    distilled_evals.append(
                        DistilledEvaluation(
                            atom_id=parsed_ev.atom_id,
                            status=parsed_ev.status,
                            exact_quotes=[q[: settings.max_synthesis_quote_length] for q in valid_quotes],
                            semantic_reasoning=sem_reasoning,
                            extensions=parsed_ev.extensions,
                        )
                    )

            if not distilled_evals:
                logger.error(
                    "[SynthesisPayloadCompressor] %s: Results list cannot be empty after compression.",
                    ErrorCodes.VALIDATION_FAILED.name,
                )
                raise AppException(
                    message="Results list cannot be empty after compression.",
                    status_code=400,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

            stratified = cls._prune_and_stratify_evaluations(distilled_evals, settings.max_synthesis_evaluations)

            normalized_score_val: float | None = None
            if "normalized_score" in filtered and filtered["normalized_score"] is not None:
                normalized_score_val = float(filtered["normalized_score"])

            level_breakdown_val: Any = None
            if "level_breakdown" in filtered and filtered["level_breakdown"] is not None:
                level_breakdown_val = filtered["level_breakdown"]

            # Encapsulate in DistilledMatrixPayloadDTO
            matrix_dto = DistilledMatrixPayloadDTO(
                results=stratified,
                normalized_score=normalized_score_val,
                level_breakdown=level_breakdown_val,
            )
            dumped_matrix = matrix_dto.model_dump(mode="json", exclude_none=True)

            # Preserve any remaining non-heavy keys on filtered dict
            result_dict: dict[str, Any] = {}
            for k, v in filtered.items():
                if k in ("results", "normalized_score", "level_breakdown"):
                    continue
                result_dict[k] = cls._clean_and_distill_payload(v)
            result_dict.update(dumped_matrix)
            return result_dict

        return {k: cls._clean_and_distill_payload(v) for k, v in filtered.items()}

        return val

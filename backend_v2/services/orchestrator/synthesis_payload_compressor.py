"""Synthesis Payload Compressor.

Encapsulates payload compression logic for the synthesis pipeline.
"""

from __future__ import annotations

import copy
import json
import logging
from collections.abc import Mapping, Sequence
from typing import Any

from pydantic import BaseModel, JsonValue, ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.synthesis import DistilledEvaluation
from backend_v2.models.dtos.atom_result import EvaluatedAtomDTO
from backend_v2.models.dtos.step_output import StepPayloadValue
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

__all__ = ["SynthesisPayloadCompressor"]


class SynthesisPayloadCompressor:
    """Compresses payloads for synthesis LLM steps by stripping extraneous metadata."""

    @staticmethod
    def compress_synthesis_payload(
        v: BaseModel | StepPayloadValue,
    ) -> str:
        """Deep copy and strip heavy Pydantic metadata and AI internal logs before sending to final synthesis.

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
                exclude={
                    "shuffled_atoms",
                    "atom_quotes",
                    "hydrated_references",
                    "_step_metadata",
                    "_audit_signature",
                    "_evaluative_matrices",
                },
                exclude_none=True,
            )
            return json.dumps(dumped, ensure_ascii=False, indent=2)

        clean_v: Any
        if isinstance(v, list):
            clean_list = [
                item.model_dump(
                    mode="json",
                    exclude={
                        "shuffled_atoms",
                        "atom_quotes",
                        "hydrated_references",
                        "_step_metadata",
                        "_audit_signature",
                        "_evaluative_matrices",
                    },
                    exclude_none=True,
                )
                if isinstance(item, BaseModel)
                else item
                for item in v
            ]
            clean_v = copy.deepcopy(clean_list)
        elif isinstance(v, Mapping):
            clean_v = copy.deepcopy(dict(v))
        else:
            logger.error(
                "[SynthesisPayloadCompressor] %s: Payload must be a dict, list, string, or scalar for compression.",
                ErrorCodes.VALIDATION_FAILED.name,
            )
            raise AppException(
                message="Payload must be a dict, list, string, or scalar for compression.",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        settings = get_settings()

        def _prune_and_stratify_evaluations(
            evals: Sequence[EvaluatedAtomDTO | Mapping[str, JsonValue]], limit: int
        ) -> list[EvaluatedAtomDTO | Mapping[str, JsonValue]]:
            """Prune and stratify evaluations with deterministic prioritized stratification.

            When limit == 0: Unbounded mode (forward all without truncation).
            When limit > 0 and len(evals) > limit:
              - Partition into Deficits/Failures (70% budget) and Strengths/Passes.
              - Sort both partitions by (-len(exact_quotes), atom_id).
              - Apply dynamic spillover.
              - Canonically sort by atom_id for byte-for-byte deterministic serialization.
            """
            if limit == 0 or len(evals) <= limit:
                return list(evals)

            deficits: list[EvaluatedAtomDTO | Mapping[str, JsonValue]] = []
            strengths: list[EvaluatedAtomDTO | Mapping[str, JsonValue]] = []

            for item in evals:
                if isinstance(item, EvaluatedAtomDTO):
                    status = item.status
                elif isinstance(item, Mapping):
                    if "status" in item and isinstance(item["status"], str):
                        status = item["status"]
                    else:
                        status = None
                else:
                    logger.error(
                        "[SynthesisPayloadCompressor] %s: Invalid evaluation item type: %s",
                        ErrorCodes.VALIDATION_FAILED.name,
                        type(item),
                    )
                    raise AppException(
                        message=f"Invalid evaluation item type: {type(item)}",
                        status_code=400,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    )

                if status in ("FAILED", "UNMET", "NON_COMPLIANT"):
                    deficits.append(item)
                else:
                    strengths.append(item)

            def sort_key(item: EvaluatedAtomDTO | Mapping[str, JsonValue]) -> tuple[int, str]:
                if isinstance(item, EvaluatedAtomDTO):
                    quotes_count = len(item.exact_quotes)
                    atom_id = item.atom_id or item.tda_id
                else:
                    if "exact_quotes" in item and isinstance(item["exact_quotes"], list):
                        quotes_count = len(item["exact_quotes"])
                    else:
                        quotes_count = 0
                    if "atom_id" in item and item["atom_id"] is not None:
                        atom_id = str(item["atom_id"])
                    else:
                        atom_id = ""
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

            def get_atom_id(x: EvaluatedAtomDTO | Mapping[str, JsonValue]) -> str:
                if isinstance(x, EvaluatedAtomDTO):
                    return str(x.atom_id or x.tda_id)
                if "atom_id" in x and x["atom_id"] is not None:
                    return str(x["atom_id"])
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

        def _strip_heavy_keys(obj: Any) -> None:
            if isinstance(obj, list):
                for item in obj:
                    _strip_heavy_keys(item)
                return
            if not isinstance(obj, (str, int, float, bool)) and obj is not None:
                try:
                    obj.pop("shuffled_atoms", None)
                    obj.pop("atom_quotes", None)
                    obj.pop("hydrated_references", None)
                    obj.pop("_step_metadata", None)
                    obj.pop("_audit_signature", None)
                    obj.pop("_evaluative_matrices", None)

                    if "results" in obj:
                        results_data = obj["results"]
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

                        lite_evals = []
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

                            if isinstance(ev, EvaluatedAtomDTO):
                                atom_id = ev.atom_id or ev.tda_id
                                valid_quotes = [
                                    q.strip()
                                    for q in ev.exact_quotes
                                    if q.strip()
                                    and q.strip() not in ("None", "null", "N/A", "N/A - insufficient data")
                                    and not (q.strip().startswith("[") and q.strip().endswith("]"))
                                ]
                                if valid_quotes:
                                    reasoning = None
                                    if ev.evaluation_reasoning:
                                        reasoning = str(ev.evaluation_reasoning)[
                                            : settings.max_synthesis_reasoning_length
                                        ]
                                    sanitized_ev = DistilledEvaluation(
                                        atom_id=atom_id,
                                        exact_quotes=[q[: settings.max_synthesis_quote_length] for q in valid_quotes],
                                        semantic_reasoning=reasoning,
                                    )
                                    dumped: dict[str, JsonValue] = sanitized_ev.model_dump(mode="json")
                                    if ev.status:
                                        dumped["status"] = ev.status
                                    lite_evals.append(dumped)
                            elif isinstance(ev, Mapping) and "exact_quotes" in ev:
                                if "atom_id" not in ev or not ev["atom_id"]:
                                    logger.error(
                                        "[SynthesisPayloadCompressor] %s: "
                                        "Missing mandatory field in evaluation: atom_id",
                                        ErrorCodes.VALIDATION_FAILED.name,
                                    )
                                    raise AppException(
                                        message="Missing mandatory field in evaluation: 'atom_id'",
                                        status_code=400,
                                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                                    )

                                try:
                                    lite_ev_dict: dict[str, JsonValue] = {
                                        "atom_id": ev["atom_id"],
                                        "exact_quotes": ev["exact_quotes"],
                                    }
                                    if "semantic_reasoning" in ev:
                                        lite_ev_dict["semantic_reasoning"] = ev["semantic_reasoning"]
                                    if "extensions" in ev:
                                        lite_ev_dict["extensions"] = ev["extensions"]

                                    lite_ev_obj = DistilledEvaluation.model_validate(lite_ev_dict, strict=False)
                                except KeyError as e:
                                    logger.error(
                                        "[SynthesisPayloadCompressor] %s: Missing mandatory field in evaluation: %s",
                                        ErrorCodes.VALIDATION_FAILED.name,
                                        str(e),
                                    )
                                    raise AppException(
                                        message=f"Missing mandatory field in evaluation: {str(e)}",
                                        status_code=400,
                                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                                    ) from e
                                except (ValidationError, ValueError) as e:
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

                                valid_quotes = []
                                for q_str in lite_ev_obj.exact_quotes:
                                    q_str = q_str.strip()
                                    if (
                                        q_str
                                        and q_str not in ("None", "null", "N/A", "N/A - insufficient data")
                                        and not (q_str.startswith("[") and q_str.endswith("]"))
                                    ):
                                        valid_quotes.append(q_str)

                                if valid_quotes:
                                    sem_reasoning = None
                                    if lite_ev_obj.semantic_reasoning:
                                        sem_reasoning = str(lite_ev_obj.semantic_reasoning)[
                                            : settings.max_synthesis_reasoning_length
                                        ]
                                    sanitized_ev = DistilledEvaluation.model_validate(
                                        lite_ev_obj.model_dump(exclude_unset=True)
                                        | {
                                            "exact_quotes": [
                                                q[: settings.max_synthesis_quote_length] for q in valid_quotes
                                            ],
                                            "semantic_reasoning": sem_reasoning,
                                        }
                                    )
                                    dumped = sanitized_ev.model_dump(mode="json")
                                    if "status" in ev and "status" not in dumped:
                                        dumped["status"] = ev["status"]
                                    lite_evals.append(dumped)
                            elif isinstance(ev, Mapping):
                                normalized: dict[str, JsonValue] = {
                                    k: v for k, v in ev.items() if k in {"output_text", "status", "atom_id"}
                                }
                                if normalized:
                                    lite_evals.append(normalized)

                        if not lite_evals:
                            logger.error(
                                "[SynthesisPayloadCompressor] %s: Results list cannot be empty after compression.",
                                ErrorCodes.VALIDATION_FAILED.name,
                            )
                            raise AppException(
                                message="Results list cannot be empty after compression.",
                                status_code=400,
                                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                            )

                        obj["results"] = _prune_and_stratify_evaluations(lite_evals, settings.max_synthesis_evaluations)

                    for _, val in list(obj.items()):
                        _strip_heavy_keys(val)
                except (AttributeError, TypeError) as e:
                    logger.error(
                        "[SynthesisPayloadCompressor] %s: Key stripping failed: %s",
                        ErrorCodes.VALIDATION_FAILED.name,
                        str(e),
                    )
                    raise AppException(
                        message=f"Key stripping failed: {str(e)}",
                        status_code=400,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    ) from e

        _strip_heavy_keys(clean_v)
        return json.dumps(clean_v, ensure_ascii=False, indent=2)

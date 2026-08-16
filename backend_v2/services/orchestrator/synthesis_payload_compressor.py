"""Synthesis Payload Compressor.

Encapsulates payload compression logic for the synthesis pipeline.
"""

import copy
import json
from typing import Any

from pydantic import BaseModel

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.synthesis import DistilledEvaluation, SynthesisStepDataDTO
from backend_v2.settings import get_settings


class SynthesisPayloadCompressor:
    """Compresses payloads for synthesis LLM steps by stripping extraneous metadata."""

    @staticmethod
    def compress_synthesis_payload(v: dict[str, Any] | list[Any] | str | SynthesisStepDataDTO) -> str:
        """Deep copy and strip heavy Pydantic metadata and AI internal logs before sending to final synthesis.

        Args:
            v: The extracted JSON payload or DTO value to compress.

        Returns:
            A stringified JSON dump stripped of extraneous AI inference variables.

        Raises:
            AppException: Triggered with VALIDATION_FAILED if the payload or its inner evaluation components are invalid or exceed limits.
        """
        if not v:
            raise AppException(
                message="Cannot compress empty payload.",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        if isinstance(v, BaseModel):
            v = v.model_dump(mode="json")
        elif isinstance(v, list):
            v = [item.model_dump(mode="json") if isinstance(item, BaseModel) else item for item in v]

        if not isinstance(v, (dict, list)):
            raise AppException(
                message="Payload must be a dict or list for compression.",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        clean_v = copy.deepcopy(v)
        settings = get_settings()

        def _strip_heavy_keys(obj: Any) -> None:
            if isinstance(obj, dict):
                obj.pop("shuffled_atoms", None)
                obj.pop("atom_quotes", None)

                if "evaluations" in obj:
                    evals = obj["evaluations"]
                    if not isinstance(evals, list):
                        raise AppException(
                            message="'evaluations' must be a list.",
                            status_code=400,
                            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                        )

                    lite_evals = []
                    for ev in evals:
                        if not isinstance(ev, dict):
                            raise AppException(
                                message="Evaluation item must be a dictionary.",
                                status_code=400,
                                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                            )

                        # Enforce strict Pydantic validation IMMEDIATELY instead of loose dict.get
                        # We extract mandatory fields strictly (failing fast on KeyError)
                        # to shield DistilledEvaluation's extra="forbid" from LLM bloat keys.
                        try:
                            lite_ev_dict = {
                                "atom_id": ev["atom_id"],
                                "exact_quotes": ev["exact_quotes"],
                            }
                            if "semantic_reasoning" in ev:
                                lite_ev_dict["semantic_reasoning"] = ev["semantic_reasoning"]
                            if "extensions" in ev:
                                lite_ev_dict["extensions"] = ev["extensions"]

                            lite_ev_obj = DistilledEvaluation.model_validate(lite_ev_dict, strict=False)
                        except KeyError as e:
                            raise AppException(
                                message=f"Missing mandatory field in evaluation: {str(e)}",
                                status_code=400,
                                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                            ) from e
                        except Exception as e:
                            raise AppException(
                                message=f"Failed to hydrate evaluation: {str(e)}",
                                status_code=400,
                                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                            ) from e

                        # Further sanitize exactly as needed for compression
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
                            lite_ev_obj = lite_ev_obj.model_copy(
                                update={
                                    "exact_quotes": [q[: settings.max_synthesis_quote_length] for q in valid_quotes],
                                    "semantic_reasoning": str(lite_ev_obj.semantic_reasoning)[:300]
                                    if lite_ev_obj.semantic_reasoning
                                    else None,
                                }
                            )
                            lite_evals.append(lite_ev_obj.model_dump(mode="json"))

                    if len(lite_evals) > settings.max_synthesis_evaluations:
                        raise AppException(
                            message=f"Evaluations exceed maximum limit of {settings.max_synthesis_evaluations}",
                            status_code=400,
                            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                        )
                    if not lite_evals:
                        raise AppException(
                            message="Evaluations list cannot be empty after compression.",
                            status_code=400,
                            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                        )
                    obj["evaluations"] = lite_evals

                for _, val in list(obj.items()):
                    _strip_heavy_keys(val)
            elif isinstance(obj, list):
                for item in obj:
                    _strip_heavy_keys(item)

        _strip_heavy_keys(clean_v)
        return json.dumps(clean_v, ensure_ascii=False, indent=2)

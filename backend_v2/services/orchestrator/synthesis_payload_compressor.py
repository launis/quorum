"""Synthesis Payload Compressor.

Encapsulates payload compression logic for the synthesis pipeline.
"""

import copy
import json
from typing import Any

from pydantic import BaseModel

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
        """
        if isinstance(v, BaseModel):
            v = v.model_dump(mode="json")
        elif isinstance(v, list):
            v = [item.model_dump(mode="json") if isinstance(item, BaseModel) else item for item in v]

        if not isinstance(v, (dict, list)):
            return str(v)

        clean_v = copy.deepcopy(v)
        settings = get_settings()

        def _strip_heavy_keys(obj: Any) -> None:
            if isinstance(obj, dict):
                obj.pop("shuffled_atoms", None)
                obj.pop("atom_quotes", None)

                if "evaluations" in obj:
                    evals = obj["evaluations"]
                    if isinstance(evals, list):
                        lite_evals = []
                        for ev in evals:
                            if isinstance(ev, dict):
                                eq_list = ev.get("exact_quotes", [])
                                sr = ev.get("semantic_reasoning")

                                if not isinstance(eq_list, list):
                                    eq_list = [eq_list] if eq_list else []

                                valid_quotes = []
                                for q in eq_list:
                                    if not q:
                                        continue
                                    q_text = (
                                        (q.get("quote") or q.get("quote_text") or q.get("text", ""))
                                        if isinstance(q, dict)
                                        else str(q)
                                    )
                                    q_str = q_text.strip()
                                    if (
                                        q_str
                                        and q_str not in ("None", "null", "N/A", "N/A - insufficient data")
                                        and not (q_str.startswith("[") and q_str.endswith("]"))
                                    ):
                                        valid_quotes.append(q_str)

                                if valid_quotes:
                                    lite_ev_dict = {
                                        "atom_id": ev.get("atom_id"),
                                        "exact_quotes": [q[:300] for q in valid_quotes],
                                        "semantic_reasoning": str(sr)[:300] if sr else None,
                                    }
                                    if "extensions" in ev:
                                        lite_ev_dict["extensions"] = ev["extensions"]

                                    # Enforce strict Pydantic validation
                                    lite_ev_obj = DistilledEvaluation.model_validate(lite_ev_dict)
                                    lite_evals.append(lite_ev_obj.model_dump(mode="json"))

                        lite_evals = lite_evals[: settings.max_synthesis_evaluations]
                        obj["evaluations"] = lite_evals if lite_evals else None
                    else:
                        obj["evaluations"] = None
                    if not obj.get("evaluations"):
                        obj.pop("evaluations", None)

                for _, val in list(obj.items()):
                    _strip_heavy_keys(val)
            elif isinstance(obj, list):
                for item in obj:
                    _strip_heavy_keys(item)

        _strip_heavy_keys(clean_v)
        return json.dumps(clean_v, ensure_ascii=False, indent=2)

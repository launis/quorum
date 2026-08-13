"""Matrix Explanation Service.

Abstracts the matrix quote assembly and justification logic out of the
synthesis distiller to prevent God Code and maintain Single Responsibility.
"""

from typing import Any

from backend_v2.models.state import StepOutputDTO
from backend_v2.models.v2_core import PromptBlock
from backend_v2.utils.alias_engine import AliasEngine


class MatrixExplanationService:
    """Service to assemble matrices to explain by extracting quotes."""

    @staticmethod
    def assemble_matrices_to_explain(
        available_dtos: list[StepOutputDTO], title_map: dict[str, str], blocks_by_id: dict[str, PromptBlock]
    ) -> list[dict[str, Any]]:
        """Assemble the matrices_to_explain list by extracting quotes from evaluated_atoms.

        Epic 94 Enriched Atom Graph migration: Extracts directly from MatrixScorecardRowDTO structures.
        Epic 133A: Supports lightweight MatrixEvaluationResult dictionaries.

        Args:
            available_dtos: All step output DTOs from the execution state.
            title_map: Map of localized titles.
            blocks_by_id: Map of PromptBlock ID to PromptBlock model.

        Returns:
            List of dicts with keys: matrix_id, score, justification.
        """
        matrices_to_explain_map: dict[str, dict[str, Any]] = {}
        alias_engine = AliasEngine()

        # Epic 133A/133B Migration: Build global map of tda_id -> list of quotes
        global_quotes_map: dict[str, list[str]] = {}
        for dto in available_dtos:
            if isinstance(dto.payload, dict) and "results" in dto.payload:
                for atom_res in dto.payload["results"]:
                    if isinstance(atom_res, dict) and "tda_id" in atom_res:
                        t_id = atom_res["tda_id"]
                        quotes = []

                        if "exact_quotes" in atom_res and isinstance(atom_res["exact_quotes"], list):
                            for eq in atom_res["exact_quotes"]:
                                if isinstance(eq, dict):
                                    txt = eq.get("text") or eq.get("quote")
                                    if txt:
                                        quotes.append(str(txt))
                        elif "extensions" in atom_res and isinstance(atom_res["extensions"], dict):
                            ext_quotes = atom_res["extensions"].get("exact_quotes", [])
                            if isinstance(ext_quotes, list):
                                for eq in ext_quotes:
                                    if isinstance(eq, dict):
                                        txt = eq.get("text") or eq.get("quote")
                                        if txt:
                                            quotes.append(str(txt))
                                    elif isinstance(eq, str):
                                        quotes.append(eq)

                        if not quotes and "source_quote" in atom_res and atom_res["source_quote"]:
                            quotes.append(str(atom_res["source_quote"]))

                        if quotes:
                            global_quotes_map[t_id] = quotes

        for step_dto_obj in available_dtos:
            payload = step_dto_obj.payload
            block_id = step_dto_obj.block_id

            pb = blocks_by_id.get(block_id)
            if not pb or pb.category_id != "matrix":
                continue

            if isinstance(payload, dict):
                quotes_list: list[str] = []
                evaluated_claims: list[str] = []

                # Map tda_id to its claim label for fallback explanation
                tda_to_claim = {}
                if pb.scales is not None:
                    for scale in pb.scales:
                        if scale.claims is not None:
                            for claim in scale.claims:
                                try:
                                    claim_text = claim.label.resolve("en") if hasattr(claim.label, "resolve") else ""
                                except Exception:
                                    claim_text = ""
                                if claim_text and claim.tda_assertions is not None:
                                    for tda in claim.tda_assertions:
                                        tda_to_claim[tda.tda_id] = claim_text

                # Epic 133A: Lightweight Matrix evaluates atoms as a dict
                atoms = payload.get("evaluated_atoms", {})

                if isinstance(atoms, dict):
                    for tda_id, hit_status in atoms.items():
                        if hit_status is True or str(hit_status).upper() == "PASS":
                            if tda_id in global_quotes_map:
                                quotes_list.extend(global_quotes_map[tda_id])
                            if tda_id in tda_to_claim:
                                evaluated_claims.append(tda_to_claim[tda_id])

                if block_id not in matrices_to_explain_map:
                    matrix_alias = alias_engine.register(block_id, prefix="MX-")
                    # Deduplicate quotes to prevent redundant justifications
                    unique_quotes = list(dict.fromkeys(quotes_list))

                    level_breakdown_str = ""
                    level_breakdown = payload.get("level_breakdown")
                    if isinstance(level_breakdown, dict) and level_breakdown:
                        breakdowns = []
                        for lvl, stats in level_breakdown.items():
                            if isinstance(stats, dict):
                                hits = stats.get("hits", 0)
                                total = stats.get("total", 0)
                                breakdowns.append(f"Level {lvl}: {hits}/{total} hits")
                        if breakdowns:
                            level_breakdown_str = "[DISTRIBUTION CONTEXT: " + ", ".join(breakdowns) + "]\n\n"

                    if unique_quotes:
                        justification_text = level_breakdown_str + "\n".join([f"- {q}" for q in unique_quotes])
                    elif evaluated_claims:
                        unique_claims = list(dict.fromkeys(evaluated_claims))
                        justification_text = (
                            level_breakdown_str
                            + "Evaluation based on the targeted presence/absence of: "
                            + ", ".join(unique_claims)
                        )
                    else:
                        justification_text = (
                            level_breakdown_str + "No direct evidence quotes extracted for this matrix."
                        )

                    matrices_to_explain_map[block_id] = {
                        "real_matrix_id": block_id,
                        "matrix_id": matrix_alias,
                        "matrix_label": title_map.get(block_id.lower(), block_id),
                        "score": payload.get("normalized_score"),
                        "justification": justification_text,
                    }

        return list(matrices_to_explain_map.values())

"""Matrix Explanation Service.

Abstracts the matrix quote assembly and justification logic out of the
synthesis distiller to prevent God Code and maintain Single Responsibility.
"""

from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
from backend_v2.models.dtos.synthesis import MatrixExplanationContextDTO
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.state import StepOutputDTO
from backend_v2.models.v2_core import AtomResultDTO, PromptBlock
from backend_v2.utils.alias_engine import AliasEngine


class MatrixExplanationService:
    """Service to assemble matrices to explain by extracting quotes."""

    @staticmethod
    def assemble_matrices_to_explain(
        available_dtos: list[StepOutputDTO], 
        title_map: dict[str, str], 
        blocks_by_id: dict[str, PromptBlock],
        target_locale: str
    ) -> list[MatrixExplanationContextDTO]:
        """Assemble the matrices_to_explain list by extracting quotes from evaluated_atoms.

        Epic 94 Enriched Atom Graph migration: Extracts directly from MatrixScorecardRowDTO structures.
        Epic 133A: Supports lightweight MatrixEvaluationResult dictionaries.

        Args:
            available_dtos: All step output DTOs from the execution state.
            title_map: Map of localized titles.
            blocks_by_id: Map of PromptBlock ID to PromptBlock model.
            target_locale: Target locale for claim label resolution.

        Returns:
            List of dicts with keys: matrix_id, score, justification.
        """
        matrices_to_explain_map: dict[str, MatrixExplanationContextDTO] = {}
        alias_engine = AliasEngine()

        # Build map of tda_id -> list of quotes
        global_quotes_map: dict[str, list[str]] = {}
        for dto in available_dtos:
            if not isinstance(dto.payload, dict) or "results" not in dto.payload:
                continue
            
            results_list = dto.payload["results"]
            if not isinstance(results_list, list):
                continue
                
            for atom_dict in results_list:
                if not isinstance(atom_dict, dict):
                    continue
                try:
                    atom_res = AtomResultDTO.model_validate(atom_dict, strict=False)
                    if atom_res.source_quote:
                        global_quotes_map.setdefault(atom_res.tda_id, []).append(str(atom_res.source_quote))
                except Exception:
                    continue

        # Load limits from settings SSOT
        from backend_v2.settings import settings
        max_q = settings.max_synthesis_quotes_per_matrix
        max_len = settings.max_synthesis_quote_length
        max_u = settings.max_synthesis_unmet_criteria_per_matrix

        for step_dto_obj in available_dtos:
            payload = step_dto_obj.payload
            block_id = step_dto_obj.block_id

            pb = blocks_by_id.get(block_id)
            if not pb or pb.category_id != "matrix":
                continue

            if not isinstance(payload, dict):
                continue

            supporting_quotes: list[str] = []
            unmet_claims: list[str] = []

            # Precompute claim labels localized to target_locale
            tda_to_claim = {}
            if pb.scales:
                for scale in pb.scales:
                    if scale.claims:
                        for claim in scale.claims:
                            try:
                                claim_text = claim.label.resolve(target_locale)
                            except Exception:
                                claim_text = ""
                            if claim_text and claim.tda_assertions:
                                for tda in claim.tda_assertions:
                                    tda_to_claim[tda.tda_id] = claim_text

            payload_to_validate = dict(payload)
            payload_to_validate.pop("results", None)

            # Strict Pydantic parsing. Fail-Fast bypass.
            try:
                lw_matrix = LightweightMatrixOutput.model_validate(payload_to_validate, strict=True)
            except Exception:
                continue

            if isinstance(lw_matrix.evaluated_atoms, dict):
                for tda_id, hit_status in lw_matrix.evaluated_atoms.items():
                    # Strict Enum validation
                    if not isinstance(hit_status, ExecutionStatus):
                        try:
                            hit_status = ExecutionStatus(hit_status)
                        except ValueError:
                            continue

                    if hit_status == ExecutionStatus.PASSED:
                        if tda_id in global_quotes_map:
                            for q in global_quotes_map[tda_id]:
                                truncated_q = q[:max_len] + "..." if len(q) > max_len else q
                                supporting_quotes.append(truncated_q)
                    elif hit_status == ExecutionStatus.FAILED:
                        if tda_id in tda_to_claim:
                            unmet_claims.append(tda_to_claim[tda_id])

            if block_id not in matrices_to_explain_map:
                matrix_alias = alias_engine.register(block_id, prefix="MX-")
                
                # Truncate lists based on limits
                unique_quotes = list(dict.fromkeys(supporting_quotes))[:max_q]
                unique_unmet = list(dict.fromkeys(unmet_claims))[:max_u]

                level_breakdown_str = ""
                if lw_matrix.level_breakdown:
                    breakdowns = []
                    for lvl, stats in lw_matrix.level_breakdown.items():
                        # Strict Pydantic models, no getattr Fallbacks
                        breakdowns.append(f"Level {lvl}: {stats.hits}/{stats.total} hits")
                    if breakdowns:
                        level_breakdown_str = "[DISTRIBUTION: " + ", ".join(breakdowns) + "]\n"

                justification_parts = [level_breakdown_str] if level_breakdown_str else []
                
                if unique_quotes:
                    justification_parts.append("SUPPORTING EVIDENCE:")
                    for q in unique_quotes:
                        justification_parts.append(f'- "{q}"')
                
                if unique_unmet:
                    if justification_parts and justification_parts[-1] != level_breakdown_str:
                        justification_parts.append("\nUNMET CRITERIA:")
                    else:
                        justification_parts.append("UNMET CRITERIA:")
                    for u in unique_unmet:
                        justification_parts.append(f"- {u}")

                if not unique_quotes and not unique_unmet:
                    justification_parts.append("No explicit evidence or unmet criteria found.")

                matrices_to_explain_map[block_id] = MatrixExplanationContextDTO(
                    real_matrix_id=block_id,
                    matrix_id=matrix_alias,
                    matrix_label=title_map.get(block_id.lower(), block_id),
                    score=lw_matrix.normalized_score,
                    justification="\n".join(justification_parts).strip(),
                )

        return list(matrices_to_explain_map.values())

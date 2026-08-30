"""Matrix Explanation Service.

Abstracts the matrix quote assembly and justification logic out of the
synthesis distiller to prevent God Code and maintain Single Responsibility.
"""

import logging
from typing import Any

from pydantic import ValidationError

from backend_v2.exceptions import ErrorCodes
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock, PromptBlock
from backend_v2.models.dtos.lightweight_matrix import LevelStatsDTO, LightweightMatrixOutput
from backend_v2.models.dtos.synthesis import MatrixExplanationContextDTO
from backend_v2.models.enums import ExecutionStatus, PromptBlockCategory
from backend_v2.models.state import StepOutputDTO
from backend_v2.models.v2_core import AtomResultDTO
from backend_v2.settings import get_settings
from backend_v2.utils.alias_engine import AliasEngine
from backend_v2.utils.ranked_round_robin import ranked_round_robin_select

logger = logging.getLogger(__name__)

__all__ = ["MatrixExplanationService"]


class MatrixExplanationService:
    """Service to assemble matrices to explain by extracting quotes."""

    @staticmethod
    def assemble_matrices_to_explain(
        available_dtos: list[StepOutputDTO],
        title_map: dict[str, str],
        blocks_by_id: dict[str, PromptBlock],
        target_locale: str,
        max_quotes_per_matrix: int | None = None,
        max_unmet_criteria: int | None = None,
    ) -> list[MatrixExplanationContextDTO]:
        """Assemble the matrices_to_explain list by extracting quotes from evaluated_atoms.

        Args:
            available_dtos: All step output DTOs from the execution state.
            title_map: Map of localized titles.
            blocks_by_id: Map of PromptBlock ID to PromptBlock model.
            target_locale: Target locale for claim label resolution.
            max_quotes_per_matrix: Optional override for quotes per matrix limit.
            max_unmet_criteria: Optional override for unmet criteria per matrix limit.

        Returns:
            List of MatrixExplanationContextDTO objects.
        """
        matrices_to_explain_map: dict[str, MatrixExplanationContextDTO] = {}
        alias_engine = AliasEngine()

        # Hoist limits via Tripartite Configuration Resolution SSOT
        settings_obj = get_settings()
        max_quote_len = settings_obj.max_synthesis_quote_length
        effective_max_quotes = (
            max_quotes_per_matrix if max_quotes_per_matrix is not None else settings_obj.max_synthesis_quotes_per_matrix
        )
        effective_max_unmet = (
            max_unmet_criteria
            if max_unmet_criteria is not None
            else settings_obj.max_synthesis_unmet_criteria_per_matrix
        )

        # Build map of tda_id -> list of quotes
        global_quotes_map: dict[str, list[str]] = {}
        for dto in available_dtos:
            if not isinstance(dto.payload, dict) or "results" not in dto.payload:  # noqa: QGR012 [REASON: Polymorphic DAG payload validation]
                continue

            results_list = dto.payload["results"]
            if not isinstance(results_list, list):
                continue

            for atom_dict in results_list:
                if not isinstance(atom_dict, dict):  # noqa: QGR012 [REASON: Polymorphic DAG payload validation]
                    continue
                try:
                    atom_res = AtomResultDTO.model_validate(atom_dict, strict=False)
                    if atom_res.source_quote:
                        cleaned = atom_res.source_quote.strip()
                        if len(cleaned) >= 15:
                            global_quotes_map.setdefault(atom_res.tda_id, []).append(cleaned[:max_quote_len])
                except (ValidationError, ValueError) as e:
                    logger.warning(
                        "[MatrixExplanationService] %s: Skipping malformed atom result",
                        ErrorCodes.INVALID_OUTPUT_SCHEMA.name,
                        extra={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.name, "details": str(e)},
                    )
                    continue

        for step_dto_obj in available_dtos:
            payload = step_dto_obj.payload
            block_id = step_dto_obj.block_id

            if block_id not in blocks_by_id:
                continue

            pb = blocks_by_id[block_id]
            if pb.category_id != PromptBlockCategory.MATRIX:
                continue

            if not isinstance(payload, dict):  # noqa: QGR012 [REASON: Polymorphic DAG payload validation]
                continue

            payload_to_validate = dict(payload)
            payload_to_validate.pop("results", None)
            raw_level_breakdown = payload_to_validate.pop("level_breakdown", None)

            # Strict Pydantic parsing probe boundary
            # REVIEWED EXCEPTION to the_duct_tape_ban: probe boundary validating
            # heterogeneous polymorphic step payloads for LightweightMatrixOutput shape
            try:
                lw_matrix = LightweightMatrixOutput.model_validate(payload_to_validate, strict=False)
            except (ValidationError, ValueError) as e:
                logger.warning(
                    "[MatrixExplanationService] %s: Skipping invalid matrix payload for block %s",
                    ErrorCodes.INVALID_OUTPUT_SCHEMA.name,
                    block_id,
                    extra={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.name, "details": str(e)},
                )
                continue

            # Precompute claim labels and scale scores localized to target_locale
            tda_to_claim: dict[str, str] = {}
            tda_to_scale: dict[str, int] = {}
            if isinstance(pb, MatrixPromptBlock) and pb.scales:
                for scale in pb.scales:
                    if scale.claims:
                        for claim in scale.claims:
                            try:
                                claim_text = claim.label.resolve(target_locale)
                            except KeyError, AttributeError:
                                claim_text = ""
                            if claim_text and claim.tda_assertions:
                                for tda in claim.tda_assertions:
                                    tda_to_claim[tda.tda_id] = claim_text
                                    tda_to_scale[tda.tda_id] = scale.score

            seen_matrix_quotes: set[str] = set()
            quote_candidates: list[dict[str, Any]] = []
            unmet_claim_to_min_scale: dict[str, int] = {}

            if isinstance(lw_matrix.evaluated_atoms, dict):  # noqa: QGR012 [REASON: Polymorphic DAG payload validation]
                for tda_id, hit_status in lw_matrix.evaluated_atoms.items():
                    if hit_status == ExecutionStatus.PASSED:
                        claim_name = tda_to_claim[tda_id] if tda_id in tda_to_claim else "General Evidence"
                        if tda_id in global_quotes_map:
                            for q in global_quotes_map[tda_id]:
                                if q not in seen_matrix_quotes:
                                    seen_matrix_quotes.add(q)
                                    quote_candidates.append(
                                        {
                                            "claim_label": claim_name,
                                            "quote": q,
                                            "quote_length": len(q),
                                        }
                                    )
                    elif hit_status == ExecutionStatus.FAILED:
                        if tda_id in tda_to_claim and tda_id in tda_to_scale:
                            claim_name = tda_to_claim[tda_id]
                            scale_score = tda_to_scale[tda_id]
                            if (
                                claim_name not in unmet_claim_to_min_scale
                                or scale_score < unmet_claim_to_min_scale[claim_name]
                            ):
                                unmet_claim_to_min_scale[claim_name] = scale_score

            if block_id not in matrices_to_explain_map:
                matrix_alias = alias_engine.register(block_id, prefix="MX-")

                # Curate quotes via Ranked Round-Robin selection
                selected_quote_items = ranked_round_robin_select(
                    quote_candidates,
                    group_key=lambda item: item["claim_label"],
                    rank_key=lambda item: item["quote_length"],
                    max_items=effective_max_quotes,
                    reverse_rank=True,
                )
                selected_quotes = [item["quote"] for item in selected_quote_items]

                # Curate unmet criteria deterministically (ascending scale score order, alphabetical tie-break)
                sorted_unmet_claims = sorted(
                    unmet_claim_to_min_scale.keys(),
                    key=lambda c: (unmet_claim_to_min_scale[c], c),
                )[:effective_max_unmet]

                distribution_str = ""
                if isinstance(raw_level_breakdown, dict):  # noqa: QGR012 [REASON: Polymorphic DAG payload validation]
                    breakdowns = []
                    for lvl, raw_stats in raw_level_breakdown.items():
                        # REVIEWED EXCEPTION to the_duct_tape_ban: probe boundary validating
                        # untrusted level stats dictionary
                        try:
                            stats_dto = LevelStatsDTO.model_validate(raw_stats, strict=False)
                            breakdowns.append(f"Level {lvl}: {stats_dto.hits}/{stats_dto.total} hits")
                        except (ValidationError, ValueError) as e:
                            logger.warning(
                                "[MatrixExplanationService] %s: Skipping malformed level stats for level %s",
                                ErrorCodes.INVALID_OUTPUT_SCHEMA.name,
                                lvl,
                                extra={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.name, "details": str(e)},
                            )
                            continue
                    if breakdowns:
                        distribution_str = f"[DISTRIBUTION CONTEXT: {', '.join(breakdowns)}]"

                justification_sections: list[str] = []
                if distribution_str:
                    justification_sections.append(distribution_str)

                if selected_quotes:
                    quote_lines = [f'- "{q}"' for q in selected_quotes]
                    justification_sections.append("SUPPORTING EVIDENCE:\n" + "\n".join(quote_lines))

                if sorted_unmet_claims:
                    unmet_lines = [f"- {u}" for u in sorted_unmet_claims]
                    justification_sections.append("UNMET CRITERIA / DEFICITS:\n" + "\n".join(unmet_lines))

                if not selected_quotes and not sorted_unmet_claims:
                    justification_sections.append(
                        "No direct evidence quotes or specific deficits recorded for this matrix."
                    )

                final_justification = "\n\n".join(justification_sections).strip()
                resolved_label = title_map[block_id.lower()] if block_id.lower() in title_map else block_id

                matrices_to_explain_map[block_id] = MatrixExplanationContextDTO(
                    real_matrix_id=block_id,
                    matrix_id=matrix_alias,
                    matrix_label=resolved_label,
                    score=lw_matrix.normalized_score,
                    justification=final_justification,
                )

        return list(matrices_to_explain_map.values())

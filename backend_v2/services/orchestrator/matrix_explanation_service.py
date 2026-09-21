"""Matrix Explanation Service.

Abstracts the matrix quote assembly and justification logic out of the
synthesis distiller to prevent God Code and maintain Single Responsibility.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock, PromptBlock
from backend_v2.models.dtos.atom_result import AtomResultDTO
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
from backend_v2.models.dtos.synthesis import MatrixExplanationContextDTO
from backend_v2.models.enums import ExecutionStatus, PromptBlockCategory
from backend_v2.models.state import StepOutputDTO
from backend_v2.settings import get_settings
from backend_v2.utils.alias_engine import AliasEngine
from backend_v2.utils.ranked_round_robin import ranked_round_robin_select

logger = logging.getLogger(__name__)

__all__ = ["MatrixExplanationService", "QuoteCandidateDTO"]


class QuoteCandidateDTO(BaseModel):
    """Candidate evidence quote for ranked round-robin selection.

    Attributes:
        claim_label: Localized label of the associated claim.
        quote: Evidence quote text string.
        quote_length: Character length of the quote.
    """

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    claim_label: Annotated[str, Field(description="Localized label of the associated claim.")]
    quote: Annotated[str, Field(description="Evidence quote text string.")]
    quote_length: Annotated[int, Field(description="Character length of the quote.")]


class MatrixExplanationService:
    """Service to assemble matrices to explain by extracting quotes and unmet criteria."""

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

        Raises:
            AppException: If atom results or matrix payloads are malformed, or if an evaluated TDA atom
                is missing from the claim mapping (VALIDATION_FAILED).
        """
        matrices_to_explain_map: dict[str, MatrixExplanationContextDTO] = {}
        alias_engine = AliasEngine()

        # Hoist limits via Tripartite Configuration Resolution SSOT
        settings_obj = get_settings()
        max_quote_len = settings_obj.max_synthesis_quote_length
        if max_quotes_per_matrix is not None:
            effective_max_quotes = max_quotes_per_matrix
        else:
            effective_max_quotes = settings_obj.max_synthesis_quotes_per_matrix

        if max_unmet_criteria is not None:
            effective_max_unmet = max_unmet_criteria
        else:
            effective_max_unmet = settings_obj.max_synthesis_unmet_criteria_per_matrix

        # Build map of tda_id -> list of quotes
        global_quotes_map: dict[str, list[str]] = {}
        for dto in available_dtos:
            if isinstance(dto.payload, (str, int, float, bool, list)) or dto.payload is None:
                continue

            results_list: Any = None
            if isinstance(dto.payload, Mapping) and "results" in dto.payload:
                results_list = dto.payload["results"]

            if not isinstance(results_list, list):
                continue

            for atom_dict in results_list:
                if isinstance(atom_dict, (str, int, float, bool)) or atom_dict is None:
                    continue
                try:
                    atom_res = AtomResultDTO.model_validate(atom_dict, strict=False)
                    if atom_res.source_quote:
                        cleaned = atom_res.source_quote.strip()
                        if len(cleaned) >= 15:
                            global_quotes_map.setdefault(atom_res.tda_id, []).append(cleaned[:max_quote_len])
                except (ValidationError, ValueError) as e:
                    logger.error(
                        "[MatrixExplanationService] %s: Malformed atom result in results list: %s",
                        ErrorCodes.VALIDATION_FAILED.name,
                        e,
                        extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "details": str(e)},
                    )
                    raise AppException(
                        message=f"Malformed atom result in results list: {e}",
                        status_code=422,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    ) from e

        for step_dto_obj in available_dtos:
            payload = step_dto_obj.payload
            block_id = step_dto_obj.block_id

            if block_id not in blocks_by_id:
                continue

            pb = blocks_by_id[block_id]
            if pb.category_id != PromptBlockCategory.MATRIX:
                continue

            if isinstance(payload, (str, int, float, bool, list)) or payload is None:
                continue

            if not isinstance(payload, Mapping):
                continue

            payload_to_validate = dict(payload)
            payload_to_validate.pop("results", None)

            # Strict Pydantic parsing probe boundary
            try:
                lw_matrix = LightweightMatrixOutput.model_validate(payload_to_validate, strict=False)
            except (ValidationError, ValueError) as e:
                logger.error(
                    "[MatrixExplanationService] %s: Invalid matrix payload for block %s: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    block_id,
                    e,
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "details": str(e)},
                )
                raise AppException(
                    message=f"Invalid matrix payload for block {block_id}: {e}",
                    status_code=422,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from e

            # Precompute claim labels and scale scores localized to target_locale
            tda_to_claim: dict[str, str] = {}
            tda_to_scale: dict[str, int] = {}
            if isinstance(pb, MatrixPromptBlock) and pb.scales:
                for scale in pb.scales:
                    if scale.claims:
                        for claim in scale.claims:
                            claim_text = claim.label.resolve(target_locale)
                            if claim_text and claim.tda_assertions:
                                for tda in claim.tda_assertions:
                                    tda_to_claim[tda.tda_id] = claim_text
                                    tda_to_scale[tda.tda_id] = scale.score

            seen_matrix_quotes: set[str] = set()
            quote_candidates: list[QuoteCandidateDTO] = []
            unmet_claim_to_min_scale: dict[str, int] = {}

            if lw_matrix.evaluated_atoms:
                for tda_id, hit_status in lw_matrix.evaluated_atoms.items():
                    if hit_status == ExecutionStatus.PASSED:
                        if tda_id not in tda_to_claim:
                            logger.error(
                                "[MatrixExplanationService] %s: TDA atom '%s' missing from claim mapping in matrix '%s'",
                                ErrorCodes.VALIDATION_FAILED.name,
                                tda_id,
                                block_id,
                                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "tda_id": tda_id},
                            )
                            raise AppException(
                                message=f"TDA atom '{tda_id}' missing from claim mapping in matrix '{block_id}'.",
                                status_code=400,
                                details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "tda_id": tda_id},
                            )
                        claim_name = tda_to_claim[tda_id]
                        if tda_id in global_quotes_map:
                            for q in global_quotes_map[tda_id]:
                                if q not in seen_matrix_quotes:
                                    seen_matrix_quotes.add(q)
                                    quote_candidates.append(
                                        QuoteCandidateDTO(
                                            claim_label=claim_name,
                                            quote=q,
                                            quote_length=len(q),
                                        )
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
                    group_key=lambda item: item.claim_label,
                    rank_key=lambda item: item.quote_length,
                    max_items=effective_max_quotes,
                    reverse_rank=True,
                )
                selected_quotes = [item.quote for item in selected_quote_items]

                # Curate unmet criteria deterministically (ascending scale score order, alphabetical tie-break)
                sorted_unmet_claims = sorted(
                    unmet_claim_to_min_scale.keys(),
                    key=lambda c: (unmet_claim_to_min_scale[c], c),
                )[:effective_max_unmet]

                distribution_str = ""
                if lw_matrix.level_breakdown:
                    breakdowns = []
                    for lvl, stats_dto in lw_matrix.level_breakdown.items():
                        breakdowns.append(f"Level {lvl}: {stats_dto.hits}/{stats_dto.total} hits")
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
                if block_id.lower() in title_map:
                    resolved_label = title_map[block_id.lower()]
                else:
                    resolved_label = block_id

                matrices_to_explain_map[block_id] = MatrixExplanationContextDTO(
                    real_matrix_id=block_id,
                    matrix_id=matrix_alias,
                    matrix_label=resolved_label,
                    score=lw_matrix.normalized_score,
                    justification=final_justification,
                )

        return list(matrices_to_explain_map.values())

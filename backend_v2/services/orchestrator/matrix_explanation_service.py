"""Matrix Explanation Service.

Abstracts the matrix quote assembly and justification logic out of the
synthesis distiller to prevent God Code and maintain Single Responsibility.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.matrix import TDAAssertion
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock, PromptBlock
from backend_v2.models.dtos.atom_evaluation import ReducedAtomDTO
from backend_v2.models.dtos.atom_result import AtomResultDTO
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
from backend_v2.models.dtos.synthesis import MatrixExplanationContextDTO, MatrixFailureDeficitDTO
from backend_v2.models.dtos.trace import TraceMatrixPayloadDTO
from backend_v2.models.enums import ExecutionStatus, LaxExecutionStatus, PromptBlockCategory
from backend_v2.models.state import StepOutputDTO
from backend_v2.settings import get_settings
from backend_v2.utils.alias_engine import AliasEngine
from backend_v2.utils.ranked_round_robin import ranked_round_robin_select

logger = logging.getLogger(__name__)

__all__ = ["MatrixExplanationService", "QuoteCandidateDTO"]

_ATOM_RESULT_ADAPTER: TypeAdapter[AtomResultDTO | ReducedAtomDTO] = TypeAdapter(AtomResultDTO | ReducedAtomDTO)


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


def _extract_atom_reasoning(atom_eval: AtomResultDTO | ReducedAtomDTO | None) -> str | None:
    """Extract evaluation reasoning text from an AtomResultDTO or ReducedAtomDTO instance.

    Args:
        atom_eval: Optional evaluated or reduced atom DTO.

    Returns:
        Non-empty reasoning string or None when absent.
    """
    if atom_eval is None:
        return None
    raw_reasoning = atom_eval.evaluation_reasoning if isinstance(atom_eval, AtomResultDTO) else atom_eval.reasoning
    if raw_reasoning is not None and raw_reasoning.strip():
        return raw_reasoning.strip()
    return None


def _resolve_short_circuit_lineage(
    blocked_claim: str,
    atom_eval: AtomResultDTO | ReducedAtomDTO | None,
    tda_assertion: TDAAssertion | None,
    tda_to_claim: dict[str, str],
    global_tda_to_claim: dict[str, str],
    global_atom_evals_map: dict[str, AtomResultDTO | ReducedAtomDTO],
    alias_engine: AliasEngine,
) -> list[str]:
    """Transitively resolve upstream blocker claims and parent evaluation reasoning for N_A atoms.

    Args:
        blocked_claim: Localized claim label of the short-circuited atom.
        atom_eval: Optional evaluated or reduced atom DTO for the short-circuited atom.
        tda_assertion: Optional TDAAssertion definition for static dependency edges.
        tda_to_claim: Mapping of TDA IDs to localized claim labels in the current matrix.
        global_tda_to_claim: Mapping of TDA IDs to localized claim labels across all matrix blocks.
        global_atom_evals_map: Mapping of TDA IDs to evaluated atom DTOs across the execution state.
        alias_engine: AliasEngine used to sanitize any unmapped fallback TDA identifiers.

    Returns:
        List of formatted transitive short-circuit lineage strings.
    """
    queue: list[str] = []
    if atom_eval is not None and atom_eval.short_circuit_reason_tda_ids:
        queue.extend(atom_eval.short_circuit_reason_tda_ids)
    elif atom_eval is not None and atom_eval.depends_on_tda_ids:
        queue.extend(atom_eval.depends_on_tda_ids)
    elif tda_assertion is not None and tda_assertion.depends_on:
        queue.extend(edge.tda_id for edge in tda_assertion.depends_on)

    visited: set[str] = set()
    lineage: list[str] = []
    idx = 0
    while idx < len(queue):
        parent_tda_id = queue[idx]
        idx += 1
        if parent_tda_id in visited:
            continue
        visited.add(parent_tda_id)

        parent_eval: AtomResultDTO | ReducedAtomDTO | None = None
        if parent_tda_id in global_atom_evals_map:
            parent_eval = global_atom_evals_map[parent_tda_id]

        if parent_eval is not None and parent_eval.short_circuit_reason_tda_ids:
            for upstream_id in parent_eval.short_circuit_reason_tda_ids:
                if upstream_id not in visited:
                    queue.append(upstream_id)

        if parent_tda_id in tda_to_claim:
            parent_claim = tda_to_claim[parent_tda_id]
        elif parent_tda_id in global_tda_to_claim:
            parent_claim = global_tda_to_claim[parent_tda_id]
        else:
            parent_claim = alias_engine.register(parent_tda_id, prefix="a")

        parent_reasoning = _extract_atom_reasoning(parent_eval)
        if parent_reasoning is not None:
            entry = (
                f"[{blocked_claim}] <-- SHORT-CIRCUITED BY PREREQUISITE FAILURE: [{parent_claim}: {parent_reasoning}]"
            )
        else:
            entry = f"[{blocked_claim}] <-- SHORT-CIRCUITED BY PREREQUISITE FAILURE: [{parent_claim}]"

        if entry not in lineage:
            lineage.append(entry)

    return lineage


def _format_deficit_justification_line(deficit: MatrixFailureDeficitDTO) -> str:
    """Format a structured MatrixFailureDeficitDTO into a human-readable justification bullet line.

    Args:
        deficit: Structured failure or short-circuit deficit DTO.

    Returns:
        Formatted markdown bullet line containing reasoning, short-circuit lineage, and contrastive bounds.
    """
    parts: list[str] = [f"- {deficit.claim} [Scale {deficit.scale_score} | {deficit.status}]"]
    if deficit.is_inverse_evidence:
        parts.append("[INVERSE EVIDENCE / POISON HIT]")
    if deficit.evaluation_reasoning is not None:
        parts.append(f"Reasoning: {deficit.evaluation_reasoning}")
    if deficit.short_circuited_by_claims:
        parts.append(f"Short-Circuited By: {'; '.join(deficit.short_circuited_by_claims)}")
    if deficit.anti_patterns:
        parts.append(f"Anti-Patterns: {'; '.join(deficit.anti_patterns)}")
    if deficit.contrastive_rejected is not None and deficit.contrastive_acceptable is not None:
        parts.append(
            f"Contrastive Boundary (Rejected: {deficit.contrastive_rejected} | "
            f"Acceptable: {deficit.contrastive_acceptable})"
        )
    return " | ".join(parts)


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
        """Assemble the matrices_to_explain list by extracting quotes and full contrastive deficits.

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

        # Phase 2, Step 2.1: Hoist limits via Tripartite Configuration Resolution SSOT
        settings_obj = get_settings()
        min_quote_len = settings_obj.min_synthesis_quote_length
        max_quote_len = settings_obj.max_synthesis_quote_length
        if max_quotes_per_matrix is not None:
            effective_max_quotes = max_quotes_per_matrix
        else:
            effective_max_quotes = settings_obj.max_synthesis_quotes_per_matrix

        if max_unmet_criteria is not None:
            effective_max_unmet = max_unmet_criteria
        else:
            effective_max_unmet = settings_obj.max_synthesis_unmet_criteria_per_matrix

        # Precompute global TDA -> localized claim mapping across all MatrixPromptBlocks
        global_tda_to_claim: dict[str, str] = {}
        for block_obj in blocks_by_id.values():
            if isinstance(block_obj, MatrixPromptBlock) and block_obj.scales:
                for scale_item in block_obj.scales:
                    for claim_item in scale_item.claims:
                        resolved_claim_text = claim_item.label.resolve(target_locale)
                        if resolved_claim_text and claim_item.tda_assertions:
                            for tda_item in claim_item.tda_assertions:
                                global_tda_to_claim[tda_item.tda_id] = resolved_claim_text

        # Build maps of tda_id -> list of quotes and tda_id -> evaluated atom DTO
        global_quotes_map: dict[str, list[str]] = {}
        global_atom_evals_map: dict[str, AtomResultDTO | ReducedAtomDTO] = {}
        for dto in available_dtos:
            if isinstance(dto.payload, (str, int, float, bool)) or dto.payload is None:
                continue

            # Skip non-atom collections from system steps
            if dto.step_id == "matrix_reducer" and dto.block_id != "reduced_atoms":
                continue
            if dto.block_id in ("evaluated_matrices", "raw_extensions"):
                continue

            results_list: Sequence[object] | None = None
            if isinstance(dto.payload, (AtomResultDTO, ReducedAtomDTO)):
                results_list = [dto.payload]
            elif isinstance(dto.payload, list):
                results_list = dto.payload
            else:
                continue

            for atom_item in results_list:
                if isinstance(atom_item, (str, int, float, bool)) or atom_item is None:
                    continue
                try:
                    atom_res = (
                        atom_item
                        if isinstance(atom_item, (AtomResultDTO, ReducedAtomDTO))
                        else _ATOM_RESULT_ADAPTER.validate_python(atom_item)
                    )

                    if atom_res.tda_id not in global_atom_evals_map or isinstance(atom_res, AtomResultDTO):
                        global_atom_evals_map[atom_res.tda_id] = atom_res

                    if atom_res.source_quotes:
                        for q in atom_res.source_quotes:
                            cleaned = q.strip()
                            if len(cleaned) >= min_quote_len:
                                clipped_quote = cleaned[:max_quote_len] if max_quote_len > 0 else cleaned
                                global_quotes_map.setdefault(atom_res.tda_id, []).append(clipped_quote)
                except (ValidationError, ValueError) as e:
                    logger.error(
                        "[MatrixExplanationService] %s: Malformed atom result in results list: %s",
                        ErrorCodes.VALIDATION_FAILED.name,
                        e,
                        extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "details": str(e)},
                        exc_info=True,
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

            if isinstance(payload, (str, int, float, bool, list, set, frozenset, tuple, bytes)) or payload is None:
                continue

            lw_matrix: LightweightMatrixOutput
            if isinstance(payload, LightweightMatrixOutput):
                lw_matrix = payload
            elif isinstance(payload, TraceMatrixPayloadDTO):
                justification_val = ""
                if payload.justification is not None:
                    justification_val = payload.justification
                evaluated_atoms_val: dict[str, LaxExecutionStatus] = {}
                if payload.evaluated_atoms is not None:
                    evaluated_atoms_val = payload.evaluated_atoms
                lw_matrix = LightweightMatrixOutput(
                    raw_score=payload.raw_score,
                    normalized_score=payload.normalized_score,
                    level_breakdown=payload.level_breakdown,
                    justification=justification_val,
                    evaluated_atoms=evaluated_atoms_val,
                    extensions={},
                )
            else:
                logger.error(
                    "[MatrixExplanationService] %s: Invalid matrix payload for block %s: expected "
                    "LightweightMatrixOutput or TraceMatrixPayloadDTO, got %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    block_id,
                    type(payload),
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.name},
                    exc_info=True,
                )
                raise AppException(
                    message=(
                        f"Invalid matrix payload for block {block_id}: expected "
                        f"LightweightMatrixOutput or TraceMatrixPayloadDTO, got {type(payload)}"
                    ),
                    status_code=422,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

            # Precompute claim labels, scale scores, and TDAAssertion definitions localized to target_locale
            tda_to_claim: dict[str, str] = {}
            tda_to_scale: dict[str, int] = {}
            tda_to_assertion: dict[str, TDAAssertion] = {}
            if isinstance(pb, MatrixPromptBlock) and pb.scales:
                for scale in pb.scales:
                    if scale.claims:
                        for claim in scale.claims:
                            claim_text = claim.label.resolve(target_locale)
                            if claim_text and claim.tda_assertions:
                                for tda in claim.tda_assertions:
                                    tda_to_claim[tda.tda_id] = claim_text
                                    tda_to_scale[tda.tda_id] = scale.score
                                    tda_to_assertion[tda.tda_id] = tda

            seen_matrix_quotes: set[str] = set()
            quote_candidates: list[QuoteCandidateDTO] = []
            raw_deficits: list[MatrixFailureDeficitDTO] = []

            # Phase 2, Step 2.1: Derive scale boundaries dynamically via computed_max
            is_max_score_achieved = (
                isinstance(pb, MatrixPromptBlock)
                and pb.computed_max is not None
                and lw_matrix.raw_score is not None
                and lw_matrix.raw_score >= float(pb.computed_max)
            )

            if lw_matrix.evaluated_atoms:
                for tda_id, hit_status in lw_matrix.evaluated_atoms.items():
                    if hit_status == ExecutionStatus.PASSED:
                        if tda_id not in tda_to_claim:
                            logger.error(
                                "[MatrixExplanationService] %s: TDA atom '%s' missing from claim mapping in "
                                "matrix '%s'",
                                ErrorCodes.VALIDATION_FAILED.name,
                                tda_id,
                                block_id,
                                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "tda_id": tda_id},
                                exc_info=True,
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
                    elif (
                        not is_max_score_achieved
                        and hit_status in (ExecutionStatus.FAILED, ExecutionStatus.N_A)
                        and tda_id in tda_to_claim
                        and tda_id in tda_to_scale
                    ):
                        claim_name = tda_to_claim[tda_id]
                        scale_score = tda_to_scale[tda_id]
                        tda_def: TDAAssertion | None = None
                        if tda_id in tda_to_assertion:
                            tda_def = tda_to_assertion[tda_id]

                        atom_eval: AtomResultDTO | ReducedAtomDTO | None = None
                        if tda_id in global_atom_evals_map:
                            atom_eval = global_atom_evals_map[tda_id]

                        eval_reasoning = _extract_atom_reasoning(atom_eval)
                        is_inverse = False
                        if tda_def is not None and tda_def.inverse_evidence:
                            is_inverse = True
                        if atom_eval is not None and atom_eval.is_inverse_evidence:
                            is_inverse = True

                        anti_patterns: list[str] = []
                        contrastive_rejected: str | None = None
                        contrastive_acceptable: str | None = None
                        if tda_def is not None:
                            anti_patterns = [ap.pattern for ap in tda_def.anti_patterns]
                            if tda_def.contrastive_example is not None:
                                contrastive_rejected = tda_def.contrastive_example.rejected
                                contrastive_acceptable = tda_def.contrastive_example.acceptable

                        short_circuited_by_claims: list[str] = []
                        deficit_status: Literal["FAILED", "N_A"] = "FAILED"
                        if hit_status == ExecutionStatus.N_A:
                            deficit_status = "N_A"
                            short_circuited_by_claims = _resolve_short_circuit_lineage(
                                blocked_claim=claim_name,
                                atom_eval=atom_eval,
                                tda_assertion=tda_def,
                                tda_to_claim=tda_to_claim,
                                global_tda_to_claim=global_tda_to_claim,
                                global_atom_evals_map=global_atom_evals_map,
                                alias_engine=alias_engine,
                            )

                        deficit_dto = MatrixFailureDeficitDTO(
                            claim=claim_name,
                            status=deficit_status,
                            scale_score=scale_score,
                            evaluation_reasoning=eval_reasoning,
                            is_inverse_evidence=is_inverse,
                            short_circuited_by_claims=short_circuited_by_claims,
                            anti_patterns=anti_patterns,
                            contrastive_rejected=contrastive_rejected,
                            contrastive_acceptable=contrastive_acceptable,
                        )
                        if deficit_dto not in raw_deficits:
                            raw_deficits.append(deficit_dto)

            if block_id not in matrices_to_explain_map:
                matrix_alias = alias_engine.register(block_id, prefix="MX-")

                # Curate quotes via Ranked Round-Robin selection (0 = unbounded)
                quote_budget = effective_max_quotes if effective_max_quotes > 0 else len(quote_candidates)
                selected_quote_items = ranked_round_robin_select(
                    quote_candidates,
                    group_key=lambda item: item.claim_label,
                    rank_key=lambda item: item.quote_length,
                    max_items=quote_budget,
                    reverse_rank=True,
                )
                selected_quotes = [item.quote for item in selected_quote_items]

                # Curate unmet deficits deterministically (ascending scale score order, alphabetical claim tie-break)
                sorted_deficits = sorted(
                    raw_deficits,
                    key=lambda d: (d.scale_score, d.claim),
                )
                if effective_max_unmet > 0:
                    sorted_deficits = sorted_deficits[:effective_max_unmet]

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

                if sorted_deficits:
                    unmet_lines = [_format_deficit_justification_line(d) for d in sorted_deficits]
                    justification_sections.append("UNMET CRITERIA / DEFICITS:\n" + "\n".join(unmet_lines))

                if not selected_quotes and not sorted_deficits:
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
                    unmet_deficits=sorted_deficits,
                )

        return list(matrices_to_explain_map.values())

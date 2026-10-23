"""Matrix scale boundary projection and step scorecard atom hydration stage utilities."""

from __future__ import annotations

import logging
from collections.abc import Sequence

from fastapi import status
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock
from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO
from backend_v2.models.dtos.atom_result import AtomResultDTO
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
from backend_v2.models.dtos.matrix_parser import MatrixAtomHydrationResultDTO, MatrixScaleProjectionDTO
from backend_v2.models.dtos.matrix_scorecard import ScorecardAtomDTO
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.dtos.step_output import StepOutputDTO, StepPayloadValue
from backend_v2.models.dtos.trace import TraceMatrixPayloadDTO
from backend_v2.models.enums import DisplayScale, ExecutionStatus, LaxExecutionStatus, VisualIntent
from backend_v2.services.localization import LocalizationService
from backend_v2.utils.math_utils import scale_to_custom_range

__all__ = ["compute_scale_and_score_projection", "hydrate_step_scorecard_atoms", "unpack_matrix_payload"]

logger = logging.getLogger(__name__)


# Phase 2, Step 1: Relocate matrix payload unpacking, scale projection, and atom hydration stages
def unpack_matrix_payload(block_data: StepPayloadValue, block_id: str) -> TraceMatrixPayloadDTO:
    """Hydrates a TraceMatrixPayloadDTO from raw or lightweight matrix step output.

    Args:
        block_data: Raw block payload, LightweightMatrixOutput, or TraceMatrixPayloadDTO.
        block_id: Canonical matrix PromptBlock identifier.

    Returns:
        Validated TraceMatrixPayloadDTO instance.

    Raises:
        AppException: If payload validation fails (ErrorCodes.VALIDATION_FAILED).
    """
    try:
        if isinstance(block_data, TraceMatrixPayloadDTO):
            return block_data
        if isinstance(block_data, LightweightMatrixOutput):
            return TraceMatrixPayloadDTO.model_validate(block_data.model_dump(mode="python"))
        return TraceMatrixPayloadDTO.model_validate(block_data)
    except (ValidationError, TypeError, ValueError) as e:
        msg = f"Strict Fail-Fast: Invalid matrix payload format for '{block_id}': {e}"
        logger.error("[MatrixDomainParser] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
        http_500 = status.HTTP_500_INTERNAL_SERVER_ERROR
        raise AppException(msg, http_500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}) from e


def compute_scale_and_score_projection(
    matrix_payload: TraceMatrixPayloadDTO,
    pb_meta: MatrixPromptBlock,
    profile: OutputProfile,
    locale: str,
    block_id: str,
) -> MatrixScaleProjectionDTO:
    """Computes mathematical scale boundaries and projects UI display scores.

    Args:
        matrix_payload: Validated matrix trace payload.
        pb_meta: MatrixPromptBlock definition containing scales and extrema.
        profile: Active OutputProfile governing display scale projection.
        locale: Target language locale string.
        block_id: Canonical matrix PromptBlock identifier.

    Returns:
        Immutable MatrixScaleProjectionDTO containing scale bounds and projected scores.

    Raises:
        AppException: On missing extrema, scales, names, or custom scale bounds
            (CONFIGURATION_ERROR, VALIDATION_FAILED).
    """
    display_scale = profile.display_scale
    true_atoms = None
    total_atoms = None
    raw_score = matrix_payload.raw_score
    norm_score = matrix_payload.normalized_score
    http_500 = status.HTTP_500_INTERNAL_SERVER_ERROR
    if matrix_payload.evaluated_atoms:
        true_atoms = sum(1 for v in matrix_payload.evaluated_atoms.values() if v == ExecutionStatus.PASSED)
        total_atoms = sum(1 for v in matrix_payload.evaluated_atoms.values() if v != ExecutionStatus.N_A)
        if total_atoms > 0 and raw_score is None:
            raw_score = true_atoms / total_atoms
            norm_score = raw_score * 100.0
        elif total_atoms == 0:
            logger.info(
                "[MatrixDomainParser] Matrix '%s' evaluated to N_A (total_atoms=0). Bypassing scoring.", block_id
            )
            raw_score = None
            norm_score = None
    if pb_meta.computed_min is None or pb_meta.computed_max is None:
        msg = f"PromptBlock '{block_id}' missing Pydantic computed_min/max."
        logger.error("[MatrixDomainParser] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
        raise AppException(msg, http_500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})
    math_min = float(pb_meta.computed_min)
    math_max = float(pb_meta.computed_max)
    scales_def = pb_meta.scales
    if not scales_def:
        msg = f"PromptBlock '{block_id}' initialized as matrix but has no scales."
        logger.error("[MatrixDomainParser] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
        raise AppException(msg, http_500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})
    level_names: dict[str, str] = {}
    ui_boundary_labels: dict[str, str] = {}
    for s in scales_def:
        s_score = float(s.score)
        if not s.name:
            msg = f"Fail-Fast: MatrixScale in block '{block_id}' missing 'name'."
            logger.error("[MatrixDomainParser] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(msg, http_500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        s_label = s.name.resolve(locale)
        int_str = str(int(s_score)) if s_score.is_integer() else str(s_score)
        float_str = str(s_score)
        level_names[int_str] = s_label
        if float_str != int_str:
            level_names[float_str] = s_label
        if s_score == math_min:
            ui_boundary_labels["0.0"] = s_label
        if s_score == math_max:
            ui_boundary_labels["1.0"] = s_label
    display_scale_min = math_min
    display_scale_max = math_max
    active_score_key = "raw_score"
    if display_scale == DisplayScale.NORMALIZED_100:
        active_score_key = "normalized_score"
        display_scale_min = 0.0
        display_scale_max = 100.0
    elif display_scale == DisplayScale.CUSTOM:
        if profile.custom_scale_min is None or profile.custom_scale_max is None:
            msg = f"OutputProfile '{profile.id}' is missing custom_scale_min/max under custom scale."
            logger.error("[MatrixDomainParser] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
            raise AppException(msg, http_500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})
        display_scale_min = float(profile.custom_scale_min)
        display_scale_max = float(profile.custom_scale_max)
    if display_scale == DisplayScale.CUSTOM:
        if raw_score is not None:
            projected = scale_to_custom_range(
                float(raw_score), math_min, math_max, display_scale_min, display_scale_max
            )
            score_float: float | None = float(round(projected, 1))
        else:
            score_float = None
    else:
        target_val = (
            matrix_payload.normalized_score if active_score_key == "normalized_score" else matrix_payload.raw_score
        )
        if target_val is None:
            target_val = raw_score
        score_float = None
        if target_val is not None:
            score_float = float(round(float(target_val), 1))
        if display_scale == DisplayScale.NORMALIZED_100 and score_float is not None:
            score_float = float(round(score_float))
    ui_plot_ratio = None
    if raw_score is not None:
        ratio = 0.0 if math_max == math_min else (float(raw_score) - math_min) / (math_max - math_min)
        ui_plot_ratio = float(max(0.0, min(1.0, ratio)))
    score_display_label = "-"
    if score_float is not None:
        max_val = 100.0
        if display_scale_max is not None:
            max_val = display_scale_max
        score_display_label = f"{score_float:.1f} / {max_val:.1f}"
    raw_score_float: float | None = None
    if raw_score is not None:
        raw_score_float = float(raw_score)
    norm_score_float: float | None = None
    if norm_score is not None:
        norm_score_float = float(norm_score)
    return MatrixScaleProjectionDTO(
        true_atoms=true_atoms,
        total_atoms=total_atoms,
        raw_score=raw_score_float,
        norm_score=norm_score_float,
        math_min=math_min,
        math_max=math_max,
        display_scale_min=display_scale_min,
        display_scale_max=display_scale_max,
        score_float=score_float,
        score_display_label=score_display_label,
        ui_plot_ratio=ui_plot_ratio,
        level_names=level_names,
        ui_boundary_labels=ui_boundary_labels,
    )


def hydrate_step_scorecard_atoms(
    results: Sequence[StepOutputDTO],
    step_id: str,
    pb_meta: MatrixPromptBlock,
    level_names: dict[str, str],
    locale: str,
    matrix_visible_cols: list[str],
    step_scorecard_atoms_accum: dict[str, list[ScorecardAtomDTO]],
) -> MatrixAtomHydrationResultDTO:
    """Hydrates TDA assertion evaluations into ScorecardAtomDTOs for a matrix row.

    Args:
        results: Folded state trace output items (Sequence of StepOutputDTO).
        step_id: Execution step identifier.
        pb_meta: MatrixPromptBlock definition containing scales, claims, and TDA assertions.
        level_names: Mapping of normalized scale score keys to localized scale labels.
        locale: Target language locale string.
        matrix_visible_cols: Active visible columns configured for the matrix.
        step_scorecard_atoms_accum: Mutable accumulator mapping step_id to hydrated ScorecardAtomDTO lists.

    Returns:
        Immutable MatrixAtomHydrationResultDTO containing evaluated atoms and clustered row sources.

    Raises:
        AppException: If an AtomResultDTO or ScorecardAtomDTO fails strict validation (VALIDATION_FAILED).
    """
    evaluated_atoms_list: list[ScorecardAtomDTO] = []
    clustered_row_sources: list[MCPAuditTrace] = []
    http_500 = status.HTTP_500_INTERNAL_SERVER_ERROR
    if "quotes" in matrix_visible_cols or "criteria" in matrix_visible_cols:
        step_evals_map: dict[str, AtomResultDTO] = {}
        for r_dto in results:
            if r_dto.step_id == step_id and r_dto.block_id == "results" and isinstance(r_dto.payload, list):
                for ev in r_dto.payload:
                    if isinstance(ev, AtomResultDTO):
                        step_evals_map[ev.tda_id] = ev
                    else:
                        try:
                            atom_dto = AtomResultDTO.model_validate(ev)
                            step_evals_map[atom_dto.tda_id] = atom_dto
                        except (ValidationError, TypeError, ValueError) as val_err:
                            msg = f"Invalid atom result payload in step {step_id}: {val_err}"
                            logger.error(
                                "[MatrixDomainParser] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True
                            )
                            raise AppException(
                                msg, http_500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                            ) from val_err
                break
        if pb_meta.scales:
            r_step = ReasoningStepDTO(
                step_1_identify_premise="",
                step_2_scan_source="",
                step_3_evaluate_anti_patterns="",
                step_4_final_conclusion="",
            )
            for scale in pb_meta.scales:
                l_val = int(scale.score)
                l_name = level_names[str(l_val)]
                for claim in scale.claims:
                    claim_label = ""
                    if isinstance(claim.label, I18nText):
                        claim_label = claim.label.resolve(locale)
                    elif claim.label is not None:
                        claim_label = str(claim.label)
                    for tda in claim.tda_assertions:
                        atom_id = tda.tda_id
                        val_data = None
                        if atom_id in step_evals_map:
                            val_data = step_evals_map[atom_id]
                        display_label = LocalizationService.translate("matrix_fallback_criteria", lang=locale)
                        if claim_label.strip():
                            display_label = claim_label.strip()
                        elif tda.concept_description and tda.concept_description.strip():
                            display_label = tda.concept_description.strip()
                        try:
                            exact_quotes: list[QuoteEvidenceDTO] = []
                            atom_status: LaxExecutionStatus | None = ExecutionStatus.FAILED
                            atom_reason = ""
                            atom_override = False
                            if val_data:
                                if val_data.source_quotes:
                                    q_raw = {"source_quotes": val_data.source_quotes, "source_alias": []}
                                    exact_quotes = [
                                        QuoteEvidenceDTO.model_validate(q_raw, context={"alias_registry": {}})
                                    ]
                                atom_status = val_data.status
                                if val_data.evaluation_reasoning is not None:
                                    atom_reason = val_data.evaluation_reasoning
                                atom_override = val_data.contextual_override
                            s_atom = ScorecardAtomDTO(
                                atom_id=atom_id,
                                level=l_val,
                                level_name=l_name,
                                claim_label=claim_label,
                                extracted_facts={},
                                exact_quotes=exact_quotes,
                                internal_logic_en=r_step,
                                status=atom_status,
                                semantic_reasoning=atom_reason,
                                contextual_override=atom_override,
                                structural_location=None,
                                chart_display_label=display_label,
                                visual_intent=VisualIntent.NEUTRAL,
                                human_override=None,
                            )
                        except ValidationError as e:
                            err_msg = f"LLM output violated schema during Display parsing for atom {atom_id}"
                            logger.error(
                                "[MatrixDomainParser] %s: %s", ErrorCodes.VALIDATION_FAILED.name, err_msg, exc_info=True
                            )
                            fail_msg = f"Strict type validation failed for atom {atom_id}"
                            raise AppException(
                                fail_msg, http_500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                            ) from e
                        evaluated_atoms_list.append(s_atom)
                        step_scorecard_atoms_accum.setdefault(step_id, []).append(s_atom)
    return MatrixAtomHydrationResultDTO(
        evaluated_atoms=evaluated_atoms_list, clustered_row_sources=clustered_row_sources
    )

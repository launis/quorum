"""Matrix axis label disambiguation, context target resolution, and scorecard row construction stages."""

from __future__ import annotations

import logging

from fastapi import status

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock
from backend_v2.models.domain.step import ExpectedInput, StepRule
from backend_v2.models.dtos.matrix_parser import (
    MatrixAtomHydrationResultDTO,
    MatrixContextTargetResultDTO,
    MatrixScaleProjectionDTO,
)
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO
from backend_v2.models.dtos.trace import TraceMatrixExtensionsDTO, TraceMatrixPayloadDTO
from backend_v2.models.enums import EvidenceType
from backend_v2.models.view.sdui import AnySduiBlock
from backend_v2.services.localization import LocalizationService

__all__ = [
    "build_matrix_scorecard_row",
    "resolve_axis_description",
    "resolve_context_target",
    "resolve_unique_axis_name",
]

logger = logging.getLogger(__name__)


# Phase 3, Step 1: Relocate axis resolution, context target resolution, and row builder stages
def resolve_unique_axis_name(
    pb_meta: MatrixPromptBlock,
    block_id: str,
    step_id: str,
    locale: str,
    workflow_steps: dict[str, StepRule],
    all_parsed_matrices: dict[str, MatrixScorecardRowDTO],
) -> str:
    """Resolves localized axis label and disambiguates duplicate names across workflow steps.

    Args:
        pb_meta: MatrixPromptBlock definition containing the localized label.
        block_id: Canonical matrix PromptBlock identifier.
        step_id: Execution step identifier.
        locale: Target language locale string.
        workflow_steps: Mapping of step IDs to StepRule definitions.
        all_parsed_matrices: Mapping of composite step/block keys to already parsed rows.

    Returns:
        Unique localized axis name string.

    Raises:
        AppException: If PromptBlock is missing a required I18n label (CONFIGURATION_ERROR).
    """
    if not pb_meta.label:
        msg = f"Fail-Fast: PromptBlock '{block_id}' is missing a required I18n label."
        logger.error("[MatrixDomainParser] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
        http_500 = status.HTTP_500_INTERNAL_SERVER_ERROR
        raise AppException(msg, http_500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})
    axis_name = pb_meta.label.resolve(locale)
    if not axis_name:
        axis_name = block_id
    original_axis_name = axis_name
    collision_counter = 1
    while any(ext.name == axis_name for ext in all_parsed_matrices.values()):
        step_title = workflow_steps[step_id].id
        axis_name = f"{original_axis_name} ({step_title})"
        if any(ext.name == axis_name for ext in all_parsed_matrices.values()):
            axis_name = f"{original_axis_name} ({step_title} {collision_counter})"
            collision_counter += 1
    return axis_name


def resolve_axis_description(pb_meta: MatrixPromptBlock, locale: str) -> str:
    """Resolves localized axis description from a MatrixPromptBlock.

    Args:
        pb_meta: MatrixPromptBlock definition containing optional localized description.
        locale: Target language locale string.

    Returns:
        Localized axis description string or empty string when unset.
    """
    if pb_meta.description:
        return pb_meta.description.resolve(locale)
    return ""


def resolve_context_target(
    step_id: str,
    pb_meta: MatrixPromptBlock,
    workflow_steps: dict[str, StepRule],
    expected_inputs_map: dict[str, ExpectedInput] | None,
) -> MatrixContextTargetResultDTO:
    """Resolves deterministic context target and localized label using the three-tier protocol.

    Args:
        step_id: Execution step identifier.
        pb_meta: MatrixPromptBlock definition containing optional target_input_key.
        workflow_steps: Mapping of step IDs to StepRule definitions.
        expected_inputs_map: Optional mapping of expected input keys to ExpectedInput definitions.

    Returns:
        Immutable MatrixContextTargetResultDTO containing resolved target key and localized label.
    """
    context_target: str | None = None
    context_target_label: I18nText | None = None
    step_rule: StepRule | None = None
    if step_id in workflow_steps:
        step_rule = workflow_steps[step_id]
    step_input_keys: list[str] = []
    if step_rule and step_rule.input_mappings:
        for mapped_val in step_rule.input_mappings.values():
            if isinstance(mapped_val, str):
                val_clean = mapped_val.strip()
                if val_clean.startswith("$inputs."):
                    clean_key = val_clean.removeprefix("$inputs.").strip()
                    if expected_inputs_map is None or clean_key in expected_inputs_map:
                        if clean_key not in step_input_keys:
                            step_input_keys.append(clean_key)
                elif expected_inputs_map is not None and val_clean in expected_inputs_map:
                    if val_clean not in step_input_keys:
                        step_input_keys.append(val_clean)
                elif expected_inputs_map is None and "$" not in val_clean and val_clean not in step_input_keys:
                    step_input_keys.append(val_clean)
    if len(step_input_keys) == 1:
        context_target = step_input_keys[0]
    elif len(step_input_keys) > 1:
        target_key = pb_meta.target_input_key
        if target_key in ("chat_log", "product_text"):
            context_target = target_key
        else:
            context_target = "all"
    elif pb_meta.target_input_key is not None:
        context_target = pb_meta.target_input_key
    if context_target is not None:
        input_def: ExpectedInput | None = None
        if expected_inputs_map and context_target in expected_inputs_map:
            input_def = expected_inputs_map[context_target]
        if input_def and input_def.label:
            context_target_label = input_def.label
        elif context_target in ("all", "chat_log", "product_text"):
            l10n_key = f"matrix_target_{context_target}"
            fi_label = LocalizationService.translate(l10n_key, "fi")
            en_label = LocalizationService.translate(l10n_key, "en")
            context_target_label = I18nText(translations={"fi": fi_label, "en": en_label})
        else:
            context_target_label = I18nText(translations={"fi": context_target, "en": context_target})
    return MatrixContextTargetResultDTO(context_target=context_target, context_target_label=context_target_label)


def build_matrix_scorecard_row(
    block_id: str,
    axis_name: str,
    axis_description: str,
    pb_meta: MatrixPromptBlock,
    matrix_payload: TraceMatrixPayloadDTO,
    scale_proj: MatrixScaleProjectionDTO,
    axis_level_breakdown: dict[str, str] | None,
    cleaned_explanation: str,
    atom_hydration: MatrixAtomHydrationResultDTO,
    context_target_res: MatrixContextTargetResultDTO,
) -> MatrixScorecardRowDTO:
    """Constructs an immutable MatrixScorecardRowDTO from resolved stage artifacts.

    Args:
        block_id: Canonical matrix PromptBlock identifier.
        axis_name: Unique localized axis name.
        axis_description: Localized axis description.
        pb_meta: MatrixPromptBlock definition containing metadata and theory grounding.
        matrix_payload: Validated matrix trace payload.
        scale_proj: Computed mathematical scale and UI display score projections.
        axis_level_breakdown: Formatted empirical scale distribution breakdown.
        cleaned_explanation: Sanitized row explanation text.
        atom_hydration: Hydrated scorecard atoms and clustered row sources.
        context_target_res: Resolved deterministic context target key and localized label.

    Returns:
        Constructed MatrixScorecardRowDTO instance.
    """
    inner_sdui_blocks: list[AnySduiBlock] = []
    ext = matrix_payload.extensions
    if ext is None:
        ext = TraceMatrixExtensionsDTO()
    cited_source_title = None
    if pb_meta.theory_grounding and pb_meta.theory_grounding.citation_reference:
        cited_source_title = pb_meta.theory_grounding.citation_reference
    cited_source_url = None
    if pb_meta.theory_grounding and pb_meta.theory_grounding.source_url:
        cited_source_url = pb_meta.theory_grounding.source_url
    elif ext.google_citation:
        cited_source_url = ext.google_citation
    row_semantic_reasoning: str | None = matrix_payload.justification
    if ext.semantic_reasoning:
        row_semantic_reasoning = ext.semantic_reasoning
    validated_evidence_type: EvidenceType | None = None
    match ext.evidence_type:
        case EvidenceType.EXPLICIT_QUOTE:
            validated_evidence_type = EvidenceType.EXPLICIT_QUOTE
        case EvidenceType.IMPLIED_INTENT:
            validated_evidence_type = EvidenceType.IMPLIED_INTENT
        case EvidenceType.NO_EVIDENCE:
            validated_evidence_type = EvidenceType.NO_EVIDENCE
        case _:
            validated_evidence_type = None
    return MatrixScorecardRowDTO(
        block_id=block_id,
        name=axis_name,
        label_i18n=pb_meta.label,
        description=axis_description,
        score=scale_proj.score_float,
        raw_score=scale_proj.raw_score,
        raw_scale_min=scale_proj.math_min,
        raw_scale_max=scale_proj.math_max,
        score_display_label=scale_proj.score_display_label,
        scale_min=scale_proj.display_scale_min,
        scale_max=scale_proj.display_scale_max,
        normalized_score=scale_proj.norm_score,
        true_atoms=scale_proj.true_atoms,
        total_atoms=scale_proj.total_atoms,
        row_explanation=cleaned_explanation,
        evidence_type=validated_evidence_type,
        cited_source_id=ext.source_id,
        cited_text_quote=ext.citation,
        cited_web_citation=ext.google_citation,
        cited_source_title=cited_source_title,
        cited_source_url=cited_source_url,
        context_target=context_target_res.context_target,
        context_target_label=context_target_res.context_target_label,
        remediation_steps=ext.remediation_steps,
        coaching=ext.coaching,
        falsification=ext.falsification,
        confidence=ext.confidence,
        contextual_override=ext.contextual_override,
        semantic_reasoning=row_semantic_reasoning,
        level_breakdown=axis_level_breakdown,
        level_names=scale_proj.level_names,
        ui_boundary_labels=scale_proj.ui_boundary_labels,
        ui_plot_ratio=scale_proj.ui_plot_ratio,
        is_evaluative=pb_meta.is_evaluative,
        allow_contextual_override=pb_meta.allow_contextual_override,
        evaluated_atoms=atom_hydration.evaluated_atoms,
        clustered_row_sources=atom_hydration.clustered_row_sources,
        used_evidence_ids=[],
        inner_sdui_blocks=inner_sdui_blocks,
        tda_state=None,
    )

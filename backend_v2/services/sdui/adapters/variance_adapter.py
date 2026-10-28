"""Variance Validation SDUI Adapter.

Transforms variance data into polymorphic AnySduiBlock components
for Server-Driven UI rendering. Visual rules are co-located as a module-level
AESTHETICS_RULES dictionary to enforce separation of presentation from logic.
"""

from __future__ import annotations

import logging

from pydantic import JsonValue, ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.linguistics import LinguisticsResultDTO
from backend_v2.models.dtos.atom_result import ExtensionMetricsDTO
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO
from backend_v2.models.dtos.sdui_rules import VarianceRuleItemDTO, VarianceRulesDTO
from backend_v2.models.enums import VisualIntent, XaiExtensionType
from backend_v2.models.view.sdui import (
    AlertBlock,
    AnySduiBlock,
    BulletListBlock,
    BulletListItem,
    MarkdownBlock,
    ParagraphBlock,
    SduiGridBlock,
    SduiQuadrantMatrixBlock,
)
from backend_v2.services.localization import LocalizationService
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.settings import get_settings

__all__ = ["VARIANCE_RULES", "VarianceAdapter"]

logger = logging.getLogger(__name__)


# ============================================================================
# SECTION 1: AESTHETICS RULES
# ============================================================================
# All visual decisions (severity, icon, label) are defined here as a flat
# dictionary. The adapter class below MUST NOT contain any if/elif/else
# chains for visual property selection.
#
# To add a new visual variant:  Add a key to this dictionary.
# To change a color or icon:   Edit the value in this dictionary.
# To understand the logic:     Read SECTION 2 below.
# ============================================================================

VARIANCE_RULES: VarianceRulesDTO = VarianceRulesDTO(
    rules={
        "aligned": VarianceRuleItemDTO(severity=VisualIntent.INFO),
        "misaligned": VarianceRuleItemDTO(severity=VisualIntent.WARNING),
        "misaligned_sycophancy": VarianceRuleItemDTO(severity=VisualIntent.WARNING),
    }
)


# ============================================================================
# SECTION 2: ADAPTER CLASS
# ============================================================================
# This class is a stateless transformer. It reads data from AdapterContext,
# looks up visual properties from SECTION 1, and assembles SDUI blocks.
# It MUST NOT:
#   - Import or access any repository or database
#   - Contain if/elif/else chains for visual property selection
#   - Mutate the context object
#   - Use .get() for AESTHETICS_RULES lookups
# ============================================================================


class VarianceAdapter:
    """Transforms Variance Validation into SDUI visual blocks.

    Uses co-located VARIANCE_RULES for all aesthetic decisions.
    Stateless: no instance state, no side effects.
    """

    @staticmethod
    def _validate_metrics(context: AdapterContext) -> ExtensionMetricsDTO:
        """Validate execution and extension metrics presence and completeness.

        Args:
            context: Frozen, immutable adapter context.

        Returns:
            Validated ExtensionMetricsDTO instance with required fields populated.

        Raises:
            AppException: If execution, extension_metrics, or required metric fields
                are missing (ErrorCodes.VALIDATION_FAILED).
        """
        if context.execution is None:
            msg = "Strict Fail-Fast: context.execution cannot be None for variance calculation."
            logger.error("[VarianceAdapter] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        if not context.profile_cache or not context.profile_cache.extension_metrics:
            msg = (
                "Strict Fail-Fast Enforced: 'variance_validation' requested but extension_metrics is missing in cache."
            )
            logger.error("[VarianceAdapter] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        metrics = context.profile_cache.extension_metrics
        if (
            metrics.authenticity_score is None
            or metrics.performative_phrases_count is None
            or metrics.variance_score is None
            or metrics.alignment_verdict is None
        ):
            msg = "Strict Fail-Fast Enforced: 'variance_validation' requested but metrics are incomplete."
            logger.error("[VarianceAdapter] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        return metrics

    @staticmethod
    def _resolve_alert_block(alignment_verdict: str, locale: str) -> AlertBlock:
        """Resolve alignment verdict aesthetics from VARIANCE_RULES and build AlertBlock.

        Args:
            alignment_verdict: Raw alignment verdict string from extension metrics.
            locale: Active presentation locale code.

        Returns:
            Configured AlertBlock representing the variance alignment verdict.

        Raises:
            AppException: If verdict rule mapping is missing in VARIANCE_RULES
                (ErrorCodes.CONFIGURATION_ERROR).
        """
        verdict_upper = str(alignment_verdict).upper()
        match verdict_upper:
            case "ALIGNED":
                lvl_key = "aligned"
            case "MISALIGNED_SYCOPHANCY":
                lvl_key = "misaligned_sycophancy"
            case _:
                lvl_key = "misaligned"

        try:
            aesthetics = VARIANCE_RULES[lvl_key]
        except KeyError as e:
            msg = f"Missing rule mapping for type_key: {lvl_key}"
            logger.error("[VarianceAdapter] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            ) from e

        lbl_align = LocalizationService.translate("alignment_verdict", locale)
        align_val = LocalizationService.translate(f"alignment_{lvl_key}", locale)

        return AlertBlock(
            severity=aesthetics.severity,
            text=f"{lbl_align}: {align_val}",
            exact_quotes=[],
            citations=[],
        )

    @staticmethod
    def _extract_performative_patterns(execution: ExecutionRecord) -> list[str]:
        """Extract detected performative phrase strings from execution context variables.

        Args:
            execution: Execution record containing runtime context variables.

        Returns:
            Ordered list of detected performative phrase strings.

        Raises:
            AppException: If step_linguistics payload fails LinguisticsResultDTO validation
                (ErrorCodes.INTERNAL_SERVER_ERROR).
        """
        performative_patterns: list[str] = []
        if execution.context_variables and "step_linguistics" in execution.context_variables:
            raw_ling = execution.context_variables["step_linguistics"]
            if raw_ling is not None:
                try:
                    ling_out = LinguisticsResultDTO.model_validate(raw_ling, strict=False)
                    performative_patterns = [
                        p.detected_phrase for p in ling_out.performative_patterns if p.detected_phrase
                    ]
                except (ValidationError, TypeError, ValueError) as e:
                    msg = f"[VarianceAdapter] Failed to parse linguistics from context_variables: {e}"
                    logger.error(
                        "[VarianceAdapter] %s: %s",
                        ErrorCodes.INTERNAL_SERVER_ERROR.name,
                        msg,
                        exc_info=True,
                    )
                    raise AppException(
                        message=msg,
                        status_code=500,
                        details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
                    ) from e
        return performative_patterns

    @staticmethod
    def _resolve_target_matrix(context: AdapterContext) -> MatrixScorecardRowDTO:
        """Resolve and validate the configured variance target matrix row.

        Args:
            context: Frozen, immutable adapter context.

        Returns:
            Target MatrixScorecardRowDTO with verified scale boundaries.

        Raises:
            AppException: If variance_target_block is unset, missing from parsed_matrices,
                or has invalid scale extrema (ErrorCodes.CONFIGURATION_ERROR).
        """
        target_block_id = context.profile.variance_target_block
        if not target_block_id:
            msg = f"OutputProfile '{context.profile.id}' requires 'variance_target_block' when variance validation is active."
            logger.error("[VarianceAdapter] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        target_matrix = next(
            (axis for axis in context.parsed_matrices.values() if axis.block_id == target_block_id),
            None,
        )
        if target_matrix is None:
            available_blocks: list[JsonValue] = [
                b for b in sorted({axis.block_id for axis in context.parsed_matrices.values()})
            ]
            msg = (
                f"Variance target block '{target_block_id}' not found in evaluated scorecard matrices. "
                f"Available evaluated matrices: {available_blocks}."
            )
            logger.error("[VarianceAdapter] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=500,
                details={
                    "error_code": ErrorCodes.CONFIGURATION_ERROR.value,
                    "target_block_id": target_block_id,
                    "available_matrices": available_blocks,
                },
            )

        scale_min = target_matrix.scale_min
        scale_max = target_matrix.scale_max
        if scale_min is None or scale_max is None or scale_max <= scale_min:
            msg = f"Target matrix '{target_block_id}' has invalid scale boundaries: min={scale_min}, max={scale_max}."
            logger.error("[VarianceAdapter] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        return target_matrix

    @staticmethod
    def _build_x_axis(
        auth_score_rounded: float,
        scale_min: float,
        scale_max: float,
        locale: str,
    ) -> MatrixScorecardRowDTO:
        """Construct the cognitive depth X-axis row for the 2D quadrant matrix.

        Args:
            auth_score_rounded: Rounded cognitive authenticity score.
            scale_min: Target matrix minimum scale bound.
            scale_max: Target matrix maximum scale bound.
            locale: Active presentation locale code.

        Returns:
            MatrixScorecardRowDTO representing the X-axis.
        """
        scale_range = scale_max - scale_min
        axis_cog_title = LocalizationService.translate("axis_cognitive_depth_title", locale)
        return MatrixScorecardRowDTO(
            block_id="axis_cognitive_depth",
            name=axis_cog_title,
            label_i18n=I18nText(
                translations={
                    "fi": LocalizationService.translate("axis_cognitive_depth_title", "fi"),
                    "en": LocalizationService.translate("axis_cognitive_depth_title", "en"),
                }
            ),
            description=None,
            score=auth_score_rounded,
            raw_score=auth_score_rounded,
            raw_scale_min=scale_min,
            raw_scale_max=scale_max,
            score_display_label=None,
            scale_min=scale_min,
            scale_max=scale_max,
            normalized_score=None,
            true_atoms=None,
            total_atoms=None,
            row_explanation="",
            evidence_type=None,
            cited_source_id=None,
            cited_text_quote=None,
            cited_web_citation=None,
            cited_source_title=None,
            cited_source_url=None,
            context_target=None,
            context_target_label=None,
            remediation_steps=None,
            coaching=None,
            falsification=None,
            confidence=None,
            inner_sdui_blocks=[],
            contextual_override=None,
            semantic_reasoning=None,
            level_breakdown=None,
            level_names=None,
            ui_plot_ratio=round(max(0.0, min(1.0, (auth_score_rounded - scale_min) / scale_range)), 4),
            ui_boundary_labels={},
            is_evaluative=False,
            allow_contextual_override=False,
            used_evidence_ids=[],
            evaluated_atoms=[],
            clustered_row_sources=[],
            tda_state=None,
        )

    @staticmethod
    def _build_y_axis(
        phrase_count_rounded: float,
        jargon_density: float | None,
        locale: str,
    ) -> MatrixScorecardRowDTO:
        """Construct the mechanical load Y-axis row for the 2D quadrant matrix.

        Args:
            phrase_count_rounded: Rounded performative phrase count.
            jargon_density: Optional length-invariant jargon density per 100 words.
            locale: Active presentation locale code.

        Returns:
            MatrixScorecardRowDTO representing the Y-axis.
        """
        settings = get_settings()
        if jargon_density is not None:
            normalized_load = min(
                (jargon_density / settings.variance_jargon_density_normalizer) * settings.variance_max_performative_cap,
                settings.variance_max_performative_cap,
            )
            mech_score = round(float(jargon_density), 2)
        else:
            normalized_load = min(
                (phrase_count_rounded / settings.variance_performative_normalizer)
                * settings.variance_max_performative_cap,
                settings.variance_max_performative_cap,
            )
            mech_score = phrase_count_rounded

        axis_mech_title = LocalizationService.translate("axis_mechanical_load_title", locale)
        return MatrixScorecardRowDTO(
            block_id="axis_mechanical_load",
            name=axis_mech_title,
            label_i18n=I18nText(
                translations={
                    "fi": LocalizationService.translate("axis_mechanical_load_title", "fi"),
                    "en": LocalizationService.translate("axis_mechanical_load_title", "en"),
                }
            ),
            description=None,
            score=mech_score,
            raw_score=mech_score,
            raw_scale_min=0.0,
            raw_scale_max=settings.variance_max_performative_cap,
            score_display_label=None,
            scale_min=0.0,
            scale_max=settings.variance_max_performative_cap,
            normalized_score=None,
            true_atoms=None,
            total_atoms=None,
            row_explanation="",
            evidence_type=None,
            cited_source_id=None,
            cited_text_quote=None,
            cited_web_citation=None,
            cited_source_title=None,
            cited_source_url=None,
            context_target=None,
            context_target_label=None,
            remediation_steps=None,
            coaching=None,
            falsification=None,
            confidence=None,
            inner_sdui_blocks=[],
            contextual_override=None,
            semantic_reasoning=None,
            level_breakdown=None,
            level_names=None,
            ui_plot_ratio=round(max(0.0, min(1.0, normalized_load / settings.variance_max_performative_cap)), 4),
            ui_boundary_labels={},
            is_evaluative=False,
            allow_contextual_override=False,
            used_evidence_ids=[],
            evaluated_atoms=[],
            clustered_row_sources=[],
            tda_state=None,
        )

    @staticmethod
    def _build_summary_grid(
        phrase_count_rounded: float,
        auth_score_rounded: float,
        var_score_rounded: float,
        scale_max: float,
        performative_patterns: list[str],
        jargon_density: float | None,
        locale: str,
    ) -> SduiGridBlock:
        """Construct the 4-metric summary SduiGridBlock.

        Args:
            phrase_count_rounded: Rounded performative phrase count.
            auth_score_rounded: Rounded cognitive authenticity score.
            var_score_rounded: Rounded total variance score.
            scale_max: Target matrix maximum scale bound.
            performative_patterns: Extracted performative phrases list.
            jargon_density: Optional length-invariant jargon density per 100 words.
            locale: Active presentation locale code.

        Returns:
            SduiGridBlock containing the 4 localized metric paragraphs.
        """
        lbl_mech = LocalizationService.translate("variance_mechanical", locale)
        lbl_cog = LocalizationService.translate("variance_cognitive", locale)
        lbl_var = LocalizationService.translate("variance_total", locale)
        lbl_jargon = LocalizationService.translate("jargon_score", locale)
        unit_pcs = LocalizationService.translate("unit_pcs", locale)

        jargon_count = len(performative_patterns) if performative_patterns else int(phrase_count_rounded)
        jargon_display = (
            f"{jargon_count} ({jargon_density:.1f}/100w)" if jargon_density is not None else str(jargon_count)
        )

        return SduiGridBlock(
            items=[
                ParagraphBlock(
                    text=f"{lbl_mech}: {int(phrase_count_rounded)} {unit_pcs}", exact_quotes=[], citations=[]
                ),
                ParagraphBlock(
                    text=f"{lbl_cog}: {auth_score_rounded} / {scale_max:.1f}", exact_quotes=[], citations=[]
                ),
                ParagraphBlock(text=f"{lbl_var}: {var_score_rounded}", exact_quotes=[], citations=[]),
                ParagraphBlock(text=f"{lbl_jargon}: {jargon_display}", exact_quotes=[], citations=[]),
            ]
        )

    @staticmethod
    def _resolve_explanation(
        context: AdapterContext,
        performative_phrases_count: float,
        auth_score_rounded: float,
    ) -> str:
        """Resolve variance synthesis explanation or localized fallback text.

        Args:
            context: Frozen, immutable adapter context.
            performative_phrases_count: Raw performative phrases count.
            auth_score_rounded: Rounded cognitive authenticity score.

        Returns:
            Resolved variance explanation string.
        """
        if context.profile_cache and context.profile_cache.variance_explanation:
            return context.profile_cache.variance_explanation
        fallback_template = LocalizationService.translate("variance_fallback_explanation", context.locale)
        return fallback_template.format(performative_phrases_count, auth_score_rounded)

    @staticmethod
    def build(context: AdapterContext) -> list[AnySduiBlock]:
        """Build SDUI blocks from the adapter context.

        Args:
            context: Frozen, immutable adapter context containing all
                required data for block construction.

        Returns:
            Ordered list of polymorphic SDUI blocks ready for rendering.

        Raises:
            AppException: If domain validation or configuration resolution fails
                (ErrorCodes.VALIDATION_FAILED, ErrorCodes.CONFIGURATION_ERROR,
                ErrorCodes.INTERNAL_SERVER_ERROR).
        """
        blocks: list[AnySduiBlock] = []

        if (
            not context.profile.visible_workflow_extensions
            or XaiExtensionType.VARIANCE_VALIDATION not in context.profile.visible_workflow_extensions
            or context.is_data_starved
        ):
            return blocks

        metrics = VarianceAdapter._validate_metrics(context)
        assert context.execution is not None
        assert metrics.authenticity_score is not None
        assert metrics.performative_phrases_count is not None
        assert metrics.variance_score is not None
        assert metrics.alignment_verdict is not None

        auth_score_rounded = round(float(metrics.authenticity_score), 2)
        var_score_rounded = round(float(metrics.variance_score), 2)
        phrase_count_rounded = round(float(metrics.performative_phrases_count), 2)

        alert_block = VarianceAdapter._resolve_alert_block(metrics.alignment_verdict, context.locale)
        performative_patterns = VarianceAdapter._extract_performative_patterns(context.execution)
        target_matrix = VarianceAdapter._resolve_target_matrix(context)
        assert target_matrix.scale_min is not None
        assert target_matrix.scale_max is not None

        x_axis = VarianceAdapter._build_x_axis(
            auth_score_rounded=auth_score_rounded,
            scale_min=target_matrix.scale_min,
            scale_max=target_matrix.scale_max,
            locale=context.locale,
        )
        y_axis = VarianceAdapter._build_y_axis(
            phrase_count_rounded=phrase_count_rounded,
            jargon_density=metrics.jargon_density,
            locale=context.locale,
        )
        scatter_block = SduiQuadrantMatrixBlock(title=None, axes=[x_axis, y_axis])
        grid_block = VarianceAdapter._build_summary_grid(
            phrase_count_rounded=phrase_count_rounded,
            auth_score_rounded=auth_score_rounded,
            var_score_rounded=var_score_rounded,
            scale_max=target_matrix.scale_max,
            performative_patterns=performative_patterns,
            jargon_density=metrics.jargon_density,
            locale=context.locale,
        )
        llm_explanation = VarianceAdapter._resolve_explanation(
            context=context,
            performative_phrases_count=metrics.performative_phrases_count,
            auth_score_rounded=auth_score_rounded,
        )
        title_str = LocalizationService.translate(
            f"xai_ext_{XaiExtensionType.VARIANCE_VALIDATION.value}", context.locale
        )

        blocks.append(MarkdownBlock(text=f"### {title_str}"))
        if llm_explanation:
            blocks.append(ParagraphBlock(text=llm_explanation, exact_quotes=[], citations=[]))
        blocks.append(scatter_block)
        blocks.append(grid_block)

        if performative_patterns:
            phrases_label = LocalizationService.translate("phrases_detected_label", context.locale)
            bullet_items = [
                BulletListItem(text=f"{phrases_label}: {phrase}", exact_quotes=[], citations=[])
                for phrase in performative_patterns
            ]
            blocks.append(BulletListBlock(items=bullet_items))

        blocks.append(alert_block)
        return blocks

"""Variance Validation SDUI Adapter.

Transforms variance data into polymorphic AnySduiBlock components
for Server-Driven UI rendering. Visual rules are co-located as a module-level
AESTHETICS_RULES dictionary to enforce separation of presentation from logic.
"""

import logging

from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.linguistics import LinguisticsResultDTO
from backend_v2.models.enums import VisualIntent, XaiExtensionType
from backend_v2.models.v2_core import MatrixScorecardRowDTO
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

VARIANCE_RULES: dict[str, dict[str, VisualIntent]] = {
    "aligned": {
        "severity": VisualIntent.INFO,
    },
    "misaligned": {
        "severity": VisualIntent.WARNING,
    },
    "misaligned_sycophancy": {
        "severity": VisualIntent.WARNING,
    },
}


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
    def build(context: AdapterContext) -> list[AnySduiBlock]:
        """Build SDUI blocks from the adapter context.

        Args:
            context: Frozen, immutable adapter context containing all
                required data for block construction.

        Returns:
            Ordered list of polymorphic SDUI blocks ready for rendering.

        Raises:
            KeyError: If an unmapped key is encountered in VARIANCE_RULES.
                This is intentional Fail-Fast behavior indicating incomplete
                rules configuration.
            AppException: If domain validation fails.
        """
        blocks: list[AnySduiBlock] = []

        # 1. READ: Extract only the data this adapter needs from the context
        if (
            not context.profile.visible_workflow_extensions
            or XaiExtensionType.VARIANCE_VALIDATION not in context.profile.visible_workflow_extensions
        ):
            return blocks

        # Starvation Circuit Breaker: If data starvation occurred, skip extension metrics
        if context.is_data_starved:
            return blocks

        if context.execution is None:
            msg = "Strict Fail-Fast: context.execution cannot be None for variance calculation."
            logger.error(
                "[VarianceAdapter] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                exc_info=True,
            )
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

        authenticity_score = metrics.authenticity_score
        performative_phrases_count = metrics.performative_phrases_count

        lbl_mech = LocalizationService.translate("variance_mechanical", context.locale)
        lbl_cog = LocalizationService.translate("variance_cognitive", context.locale)
        lbl_var = LocalizationService.translate("variance_total", context.locale)
        lbl_jargon = LocalizationService.translate("jargon_score", context.locale)
        lbl_align = LocalizationService.translate("alignment_verdict", context.locale)

        auth_score_rounded = round(float(authenticity_score), 2)
        var_score_rounded = round(float(metrics.variance_score), 2)
        phrase_count_rounded = round(float(performative_phrases_count), 2)

        verdict_upper = str(metrics.alignment_verdict).upper()
        if verdict_upper == "ALIGNED":
            lvl_key = "aligned"
        elif verdict_upper == "MISALIGNED_SYCOPHANCY":
            lvl_key = "misaligned_sycophancy"
        else:
            lvl_key = "misaligned"

        # 2. TRANSFORM: Look up visual rules
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

        alert_severity = aesthetics["severity"]
        align_val = LocalizationService.translate(f"alignment_{lvl_key}", context.locale)

        # 3. EXTRACT PERFORMATIVE PATTERNS (if available)
        performative_patterns: list[str] = []
        if context.execution.context_variables and "step_linguistics" in context.execution.context_variables:
            raw_ling = context.execution.context_variables["step_linguistics"]
            if raw_ling is not None:
                try:
                    ling_out = LinguisticsResultDTO.model_validate(raw_ling, strict=False)
                    performative_patterns = [
                        p.detected_phrase for p in ling_out.performative_patterns if p.detected_phrase
                    ]
                except (ValidationError, TypeError, ValueError) as e:
                    logger.warning(
                        "[VarianceAdapter] Failed to parse linguistics from context_variables",
                        extra={"error": str(e)},
                    )

        # 4. CONSTRUCT 2D AXES & SCATTER PLOT BLOCK
        axis_cog_title = LocalizationService.translate("axis_cognitive_depth_title", context.locale)
        axis_mech_title = LocalizationService.translate("axis_mechanical_load_title", context.locale)

        x_axis = MatrixScorecardRowDTO.model_validate(
            {
                "block_id": "axis_cognitive_depth",
                "name": axis_cog_title,
                "label_i18n": I18nText(
                    translations={
                        "fi": LocalizationService.translate("axis_cognitive_depth_title", "fi"),
                        "en": LocalizationService.translate("axis_cognitive_depth_title", "en"),
                    }
                ),
                "row_explanation": "",
                "is_evaluative": False,
                "score": auth_score_rounded,
                "scale_min": 1.0,
                "scale_max": 3.0,
                "ui_plot_ratio": round(max(0.0, min(1.0, (auth_score_rounded - 1.0) / 2.0)), 4),
            },
            strict=False,
        )

        settings = get_settings()
        if metrics.jargon_density is not None:
            normalized_load = min(
                (metrics.jargon_density / settings.variance_jargon_density_normalizer)
                * settings.variance_max_performative_cap,
                settings.variance_max_performative_cap,
            )
            mech_score = round(float(metrics.jargon_density), 2)
        else:
            normalized_load = min(
                (phrase_count_rounded / settings.variance_performative_normalizer)
                * settings.variance_max_performative_cap,
                settings.variance_max_performative_cap,
            )
            mech_score = phrase_count_rounded

        y_axis = MatrixScorecardRowDTO.model_validate(
            {
                "block_id": "axis_mechanical_load",
                "name": axis_mech_title,
                "label_i18n": I18nText(
                    translations={
                        "fi": LocalizationService.translate("axis_mechanical_load_title", "fi"),
                        "en": LocalizationService.translate("axis_mechanical_load_title", "en"),
                    }
                ),
                "row_explanation": "",
                "is_evaluative": False,
                "score": mech_score,
                "scale_min": 0.0,
                "scale_max": settings.variance_max_performative_cap,
                "ui_plot_ratio": round(max(0.0, min(1.0, normalized_load / settings.variance_max_performative_cap)), 4),
            },
            strict=False,
        )

        scatter_block = SduiQuadrantMatrixBlock(
            title=None,
            axes=[x_axis, y_axis],
        )

        # 5. CONSTRUCT 4-METRIC SUMMARY GRID
        unit_pcs = LocalizationService.translate("unit_pcs", context.locale)
        jargon_count = len(performative_patterns) if performative_patterns else int(performative_phrases_count)
        if metrics.jargon_density is not None:
            jargon_display = f"{jargon_count} ({metrics.jargon_density:.1f}/100w)"
        else:
            jargon_display = str(jargon_count)

        grid_block = SduiGridBlock(
            items=[
                ParagraphBlock(
                    text=f"{lbl_mech}: {int(phrase_count_rounded)} {unit_pcs}", exact_quotes=[], citations=[]
                ),
                ParagraphBlock(text=f"{lbl_cog}: {auth_score_rounded} / 3.0", exact_quotes=[], citations=[]),
                ParagraphBlock(text=f"{lbl_var}: {var_score_rounded}", exact_quotes=[], citations=[]),
                ParagraphBlock(text=f"{lbl_jargon}: {jargon_display}", exact_quotes=[], citations=[]),
            ]
        )

        # 6. CONSTRUCT ALERT BANNER
        alert_block = AlertBlock(
            severity=alert_severity,
            text=f"{lbl_align}: {align_val}",
            exact_quotes=[],
            citations=[],
        )

        # 7. RESOLVE SYNTHESIS EXPLANATION
        llm_explanation = ""
        if context.profile_cache and context.profile_cache.variance_explanation:
            llm_explanation = context.profile_cache.variance_explanation

        if not llm_explanation:
            fallback_template = LocalizationService.translate("variance_fallback_explanation", context.locale)
            llm_explanation = fallback_template.format(performative_phrases_count, auth_score_rounded)

        title_str = LocalizationService.translate(
            f"xai_ext_{XaiExtensionType.VARIANCE_VALIDATION.value}", context.locale
        )

        # 8. ASSEMBLE: Canonical Flat Dumb Painter sequence
        # Element 1: Localized Markdown Header
        blocks.append(MarkdownBlock(text=f"### {title_str}"))

        # Element 2: LLM Explanation Paragraph (if present)
        if llm_explanation:
            blocks.append(ParagraphBlock(text=llm_explanation, exact_quotes=[], citations=[]))

        # Element 3: 2D Cartesian Quadrant Scatter Plot
        blocks.append(scatter_block)

        # Element 4: Summary 4-Metric Grid
        blocks.append(grid_block)

        # Element 5: Detected Jargon Phrases (if present)
        if performative_patterns:
            phrases_label = LocalizationService.translate("phrases_detected_label", context.locale)
            bullet_items = [
                BulletListItem(
                    text=f"{phrases_label}: {phrase}",
                    exact_quotes=[],
                    citations=[],
                )
                for phrase in performative_patterns
            ]
            blocks.append(BulletListBlock(items=bullet_items))

        # Element 6: Verdict Banner Alert Block
        blocks.append(alert_block)

        return blocks

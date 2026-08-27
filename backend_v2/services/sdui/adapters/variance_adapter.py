"""Variance Validation SDUI Adapter.

Transforms variance data into polymorphic AnySduiBlock components
for Server-Driven UI rendering. Visual rules are co-located as a module-level
AESTHETICS_RULES dictionary to enforce separation of presentation from logic.
"""

import logging

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.enums import VisualIntent, XaiExtensionType
from backend_v2.models.v2_core import MatrixScorecardRowDTO
from backend_v2.models.view.sdui import (
    AlertBlock,
    AnySduiBlock,
    MarkdownBlock,
    ParagraphBlock,
    SduiGridBlock,
    SduiMetrics1DBlock,
)
from backend_v2.services.localization import LocalizationService
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext

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
        lbl_align = LocalizationService.translate("alignment_verdict", context.locale)

        auth_score_rounded = float(f"{float(authenticity_score):.2f}")
        var_score_rounded = float(f"{float(metrics.variance_score):.2f}")
        is_aligned = str(metrics.alignment_verdict) == "ALIGNED"

        lvl_key = "aligned" if is_aligned else "misaligned"
        align_val = LocalizationService.translate(f"alignment_{lvl_key}", context.locale)

        # 2. TRANSFORM: Iterate, look up visual rules, assemble blocks
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

        grid_block = SduiGridBlock(
            items=[
                ParagraphBlock(text=f"{lbl_mech}: {performative_phrases_count}", exact_quotes=[], citations=[]),
                ParagraphBlock(text=f"{lbl_cog}: {auth_score_rounded}", exact_quotes=[], citations=[]),
                ParagraphBlock(text=f"{lbl_var}: {var_score_rounded}", exact_quotes=[], citations=[]),
            ]
        )
        alert_block = AlertBlock(
            severity=alert_severity,
            text=f"{lbl_align}: {align_val}",
            exact_quotes=[],
            citations=[],
        )

        llm_explanation = ""
        if (
            context.profile_cache
            and context.profile_cache.row_explanations
            and "variance_validation" in context.profile_cache.row_explanations
        ):
            llm_explanation = context.profile_cache.row_explanations["variance_validation"]

        if not llm_explanation:
            fallback_template = LocalizationService.translate("variance_fallback_explanation", context.locale)
            llm_explanation = fallback_template.format(performative_phrases_count, auth_score_rounded)

        title_str = LocalizationService.translate(
            f"xai_ext_{XaiExtensionType.VARIANCE_VALIDATION.value}", context.locale
        )
        variance_label = I18nText(
            translations={
                "fi": LocalizationService.translate(f"xai_ext_{XaiExtensionType.VARIANCE_VALIDATION.value}", "fi"),
                "en": LocalizationService.translate(f"xai_ext_{XaiExtensionType.VARIANCE_VALIDATION.value}", "en"),
            }
        )

        variance_kwargs = {
            "block_id": "variance_metrics_row",
            "name": "Variance Metrics",
            "label_i18n": variance_label,
            "row_explanation": "",
            "is_evaluative": False,
            "inner_sdui_blocks": [grid_block, alert_block],
        }
        row_dto = MatrixScorecardRowDTO.model_validate(variance_kwargs, strict=False)

        # 3. ASSEMBLE: Canonical Dumb Painter sequence
        # Step 1: Localized Markdown Header
        blocks.append(MarkdownBlock(text=f"### {title_str}"))

        # Step 2: LLM Explanation Paragraph (if present)
        if llm_explanation:
            blocks.append(ParagraphBlock(text=llm_explanation, exact_quotes=[], citations=[]))

        # Step 3: Visual Metrics Box
        blocks.append(SduiMetrics1DBlock(axes=[row_dto]))

        return blocks

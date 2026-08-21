"""Authenticity Evaluation SDUI Adapter.

Transforms authenticity score data into polymorphic AnySduiBlock components
for Server-Driven UI rendering. Visual rules are co-located as a module-level
AESTHETICS_RULES dictionary to enforce separation of presentation from logic.
"""

import logging

from backend_v2.exceptions import AppException, ErrorCodes
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
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.settings import get_settings

__all__ = ["AUTHENTICITY_RULES", "AuthenticityAdapter"]

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

AUTHENTICITY_RULES: dict[str, dict[str, VisualIntent]] = {
    "level_high": {
        "severity": VisualIntent.INFO,
    },
    "level_medium": {
        "severity": VisualIntent.WARNING,
    },
    "level_low": {
        "severity": VisualIntent.ERROR,
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


class AuthenticityAdapter:
    """Transforms Authenticity Evaluation into SDUI visual blocks.

    Uses co-located AUTHENTICITY_RULES for all aesthetic decisions.
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
            KeyError: If an unmapped key is encountered in AUTHENTICITY_RULES.
                This is intentional Fail-Fast behavior indicating incomplete
                rules configuration.
            AppException: If domain validation fails.
        """
        blocks: list[AnySduiBlock] = []

        # 1. READ: Extract only the data this adapter needs from the context
        if (
            not context.profile.visible_workflow_extensions
            or XaiExtensionType.AUTHENTICITY_EVALUATION not in context.profile.visible_workflow_extensions
        ):
            return blocks

        # Starvation Circuit Breaker: If data starvation occurred, skip extension metrics
        if context.is_data_starved:
            return blocks

        if context.execution is None:
            msg = "Strict Fail-Fast: context.execution cannot be None for authenticity evaluation."
            logger.error(
                "[AuthenticityAdapter] %s: %s",
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
            msg = "Strict Fail-Fast Enforced: 'authenticity_evaluation' requested but extension_metrics is missing in cache."
            logger.error("[AuthenticityAdapter] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        authenticity_score = context.profile_cache.extension_metrics.authenticity_score
        if authenticity_score is None:
            msg = "Strict Fail-Fast Enforced: 'authenticity_evaluation' requested but authenticity_score is missing."
            logger.error("[AuthenticityAdapter] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        auth_score_rounded = float(f"{float(authenticity_score):.2f}")

        def get_metric_label(key: str) -> str:
            lbl = context.profile.metric_mappings.get(key)
            if not lbl:
                msg = f"Strict Fail-Fast: Missing metric_mappings translation for '{key}'."
                logger.error("[AuthenticityAdapter] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )
            return lbl.resolve(context.locale)

        lbl_jargon = get_metric_label("jargon_score")
        lbl_auth_level = get_metric_label("authenticity_level")

        grid_block = SduiGridBlock(
            items=[
                ParagraphBlock(text=f"{lbl_jargon}: {auth_score_rounded}", exact_quotes=[], citations=[]),
            ]
        )

        settings = get_settings()
        high_thresh = settings.authenticity_threshold_high
        low_thresh = settings.authenticity_threshold_low

        lvl_key = (
            "level_high"
            if auth_score_rounded >= high_thresh
            else "level_medium"
            if auth_score_rounded >= low_thresh
            else "level_low"
        )

        # 2. TRANSFORM: Iterate, look up visual rules, assemble blocks
        try:
            aesthetics = AUTHENTICITY_RULES[lvl_key]
        except KeyError as e:
            msg = f"Missing rule mapping for type_key: {lvl_key}"
            logger.error("[AuthenticityAdapter] CONFIGURATION_ERROR: %s", msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": "CONFIGURATION_ERROR"},
            ) from e

        alert_severity = aesthetics["severity"]
        lbl_lvl = get_metric_label(lvl_key)

        alert_block = AlertBlock(
            severity=alert_severity,
            text=f"{lbl_auth_level}: {lbl_lvl}",
            exact_quotes=[],
            citations=[],
        )

        llm_explanation = ""
        if context.profile_cache and context.profile_cache.row_explanations:
            llm_explanation = context.profile_cache.row_explanations.get("authenticity_evaluation", "")

        if not llm_explanation:
            fallback_template = get_metric_label("authenticity_fallback_explanation")
            llm_explanation = fallback_template.format(auth_score_rounded)

        auth_label = context.profile.extension_labels.get(XaiExtensionType.AUTHENTICITY_EVALUATION)
        if not auth_label:
            msg = f"Strict Fail-Fast: Missing extension_labels mapping for {XaiExtensionType.AUTHENTICITY_EVALUATION.value} in OutputProfile."
            logger.error("[AuthenticityAdapter] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        title_str = auth_label.resolve(context.locale)

        auth_kwargs = {
            "block_id": "authenticity_metrics_row",
            "name": "Authenticity Metrics",
            "label_i18n": auth_label,
            "row_explanation": "",
            "is_evaluative": False,
            "inner_sdui_blocks": [grid_block, alert_block],
        }
        auth_row_dto = MatrixScorecardRowDTO.model_validate(auth_kwargs, strict=False)

        # 3. ASSEMBLE: Canonical Dumb Painter sequence
        # Step 1: Localized Markdown Header
        blocks.append(MarkdownBlock(text=f"### {title_str}"))

        # Step 2: LLM Explanation Paragraph (if present)
        if llm_explanation:
            blocks.append(ParagraphBlock(text=llm_explanation, exact_quotes=[], citations=[]))

        # Step 3: Visual Metrics Box
        blocks.append(SduiMetrics1DBlock(axes=[auth_row_dto]))

        return blocks

"""Jargon Ratio SDUI Adapter.

Transforms performative linguistics extraction data into polymorphic AnySduiBlock
components for Server-Driven UI rendering. Visual rules are co-located as a module-level
JARGON_RATIO_RULES dictionary to enforce separation of presentation from logic.
"""

import logging

from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.linguistics import LinguisticsResultDTO
from backend_v2.models.enums import VisualIntent
from backend_v2.models.view.sdui import (
    AlertBlock,
    AnySduiBlock,
    BulletListBlock,
    BulletListItem,
    MarkdownBlock,
)
from backend_v2.services.localization import LocalizationService
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext

__all__ = ["JARGON_RATIO_RULES", "JargonRatioAdapter"]

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

JARGON_RATIO_RULES: dict[str, dict[str, VisualIntent]] = {
    "clean": {
        "severity": VisualIntent.INFO,
    },
    "moderate": {
        "severity": VisualIntent.WARNING,
    },
    "heavy": {
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


class JargonRatioAdapter:
    """Transforms Performative Linguistics results into SDUI visual blocks.

    Uses co-located JARGON_RATIO_RULES for all aesthetic decisions.
    Stateless: no instance state, no side effects.
    """

    @staticmethod
    def build(context: AdapterContext) -> list[AnySduiBlock]:
        """Build SDUI blocks from the adapter context.

        Args:
            context: The frozen AdapterContext containing execution state and locale.

        Returns:
            list[AnySduiBlock]: Polymorphic SDUI blocks representing jargon analysis.

        Raises:
            AppException: If configuration lookup or block assembly fails unexpectedly.
        """
        blocks: list[AnySduiBlock] = []

        if context.is_data_starved or context.execution is None:
            return blocks

        if not context.execution.context_variables or "step_linguistics" not in context.execution.context_variables:
            return blocks

        raw_ling = context.execution.context_variables["step_linguistics"]
        if raw_ling is None:
            return blocks

        try:
            ling_out = LinguisticsResultDTO.model_validate(raw_ling, strict=False)
        except (ValidationError, TypeError, ValueError) as e:
            logger.warning(
                "[JargonRatioAdapter] Failed to parse linguistics from context_variables",
                extra={"error": str(e)},
            )
            return blocks

        patterns = [p.detected_phrase for p in ling_out.performative_patterns if p.detected_phrase]
        pattern_count = len(patterns)
        total_words = ling_out.total_word_count

        # Compute density if total_words > 0
        density = (pattern_count / max(1, total_words)) * 100.0 if total_words > 0 else 0.0

        # Classify density level for aesthetic lookup
        if pattern_count == 0 or density < 1.0:
            lvl_key = "clean"
        elif density < 2.5:
            lvl_key = "moderate"
        else:
            lvl_key = "heavy"

        try:
            aesthetics = JARGON_RATIO_RULES[lvl_key]
        except KeyError as e:
            msg = f"Missing rule mapping for type_key: {lvl_key}"
            logger.error("[JargonRatioAdapter] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            ) from e

        alert_severity = aesthetics["severity"]

        # Localized header and summary
        header_title = LocalizationService.translate("jargon_ratio_title", context.locale)
        blocks.append(MarkdownBlock(text=f"### {header_title}"))

        lbl_jargon_score = LocalizationService.translate("jargon_score", context.locale)
        lbl_phrases = LocalizationService.translate("detected_phrases", context.locale)

        density_str = f"{density:.1f}% ({pattern_count}/{max(1, total_words)} w)"
        blocks.append(
            AlertBlock(
                severity=alert_severity,
                text=f"{lbl_jargon_score}: {density_str}",
                exact_quotes=[],
                citations=[],
            )
        )

        if patterns:
            bullet_items = [
                BulletListItem(
                    text=f"{lbl_phrases}: {phrase}",
                    exact_quotes=[phrase],
                    citations=[],
                )
                for phrase in patterns
            ]
            blocks.append(BulletListBlock(items=bullet_items))

        return blocks

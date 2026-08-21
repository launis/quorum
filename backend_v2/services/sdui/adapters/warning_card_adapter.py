"""Warning Card SDUI Adapter.

Transforms system events (such as data starvation) into polymorphic AlertBlocks
for Server-Driven UI rendering. Visual rules are co-located as a module-level
WARNING_CARD_RULES dictionary to enforce separation of presentation from logic.
"""

import logging

from backend_v2.exceptions import AppException
from backend_v2.models.enums import VisualIntent
from backend_v2.models.v2_core import I18nText
from backend_v2.models.view.sdui import AlertBlock, AnySduiBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext

logger = logging.getLogger(__name__)


# ============================================================================
# SECTION 1: AESTHETICS RULES
# ============================================================================
# All visual decisions (severity, icon, label) and localized static texts
# are defined here. The adapter class below MUST NOT contain any if/elif/else
# chains for visual property selection.
# ============================================================================

WARNING_CARD_RULES: dict[str, dict[str, VisualIntent]] = {
    "starvation": {
        "severity": VisualIntent.WARNING,
    },
}

I18N_WARNING_STARVATION = I18nText(
    default_locale="en",
    translations={
        "en": "Evaluation data was insufficient to generate synthesis.",
        "fi": "Arviointiaineisto ei sisältänyt riittävästi havaintoja synteesin tuottamiseksi.",
    },
)


# ============================================================================
# SECTION 2: ADAPTER CLASS
# ============================================================================
# This class is a stateless transformer. It reads data from AdapterContext,
# looks up visual properties from SECTION 1, and assembles SDUI blocks.
# ============================================================================


class WarningCardAdapter:
    """Transforms system events into SDUI AlertBlocks.

    Uses co-located WARNING_CARD_RULES for all aesthetic decisions.
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
            AppException: If an unmapped event_type key is encountered in WARNING_CARD_RULES.
        """
        blocks: list[AnySduiBlock] = []

        starvation = context.profile_cache.data_starvation if context.profile_cache else None
        if starvation is None:
            return blocks

        try:
            aesthetics = WARNING_CARD_RULES[starvation.event_type]
        except KeyError as e:
            msg = f"Missing rule mapping for event_type: '{starvation.event_type}'"
            logger.error("[WarningCardAdapter] CONFIGURATION_ERROR: %s", msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": "CONFIGURATION_ERROR"},
            ) from e

        warning_msg = I18N_WARNING_STARVATION.resolve(context.locale)

        blocks.append(
            AlertBlock(
                id=f"alert_starvation_{starvation.event_type}",
                severity=aesthetics["severity"],
                text=warning_msg,
                exact_quotes=[],
                citations=[],
            )
        )

        return blocks

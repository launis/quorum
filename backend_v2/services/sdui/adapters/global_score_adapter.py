"""Global Score SDUI Adapter.

Transforms execution global score into a SduiScoreCardBlock component
for Server-Driven UI rendering. Visual rules are co-located as a module-level
AESTHETICS_RULES dictionary to enforce separation of presentation from logic.
"""

import logging

from backend_v2.models.view.sdui import AnySduiBlock, SduiScoreCardBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext

logger = logging.getLogger(__name__)


# ============================================================================
# SECTION 1: AESTHETICS RULES
# ============================================================================

AESTHETICS_RULES: dict[str, dict[str, str]] = {
    "default": {
        "visual_intent": "primary",
    }
}


# ============================================================================
# SECTION 2: ADAPTER CLASS
# ============================================================================


class GlobalScoreAdapter:
    """Transforms global score into an SDUI visual block.

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
        """
        blocks: list[AnySduiBlock] = []

        if context.global_score is not None:
            blocks.append(SduiScoreCardBlock(global_score=context.global_score))

        return blocks

"""Synthesis Text SDUI Adapter.

Transforms synthesis markdown into SDUI visual blocks
for Server-Driven UI rendering. Visual rules are co-located as a module-level
AESTHETICS_RULES dictionary to enforce separation of presentation from logic.
"""

import logging

from backend_v2.models.view.sdui import AnySduiBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext

__all__ = ["SYNTHESIS_TEXT_RULES", "SynthesisTextAdapter"]

logger = logging.getLogger(__name__)


# ============================================================================
# SECTION 1: AESTHETICS RULES
# ============================================================================

SYNTHESIS_TEXT_RULES: dict[str, dict[str, str]] = {
    "default_text": {
        "mode": "standard",
    }
}


# ============================================================================
# SECTION 2: ADAPTER CLASS
# ============================================================================


class SynthesisTextAdapter:
    """Transforms synthesis markdown into SDUI visual blocks.

    Uses co-located SYNTHESIS_TEXT_RULES for all aesthetic decisions.
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

        # 1. READ: Insert pre-defined content blocks from profile
        if context.profile and context.profile.content_blocks:
            for cb in context.profile.content_blocks:
                blocks.append(cb.model_copy(deep=True))

        return blocks

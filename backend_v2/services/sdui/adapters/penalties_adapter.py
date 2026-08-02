"""Penalties SDUI Adapter.

Transforms applied penalty strings into polymorphic AlertBlocks
for Server-Driven UI rendering. Visual rules are co-located as a module-level
AESTHETICS_RULES dictionary to enforce separation of presentation from logic.
"""

import logging

from backend_v2.models.enums import VisualIntent
from backend_v2.models.view.sdui import (
    AlertBlock,
    AnySduiBlock,
)
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext

logger = logging.getLogger(__name__)


# ============================================================================
# SECTION 1: AESTHETICS RULES
# ============================================================================
# All visual decisions (severity, icon, label) are defined here as a flat
# dictionary. The adapter class below MUST NOT contain any if/elif/else
# chains for visual property selection.
# ============================================================================

PENALTIES_RULES: dict[str, dict[str, VisualIntent]] = {
    "default_penalty": {
        "severity": VisualIntent.CRITICAL_OVERRIDE,
    },
}


# ============================================================================
# SECTION 2: ADAPTER CLASS
# ============================================================================
# This class is a stateless transformer. It reads data from AdapterContext,
# looks up visual properties from SECTION 1, and assembles SDUI blocks.
# ============================================================================


class PenaltiesAdapter:
    """Transforms applied penalties into SDUI visual blocks.

    Uses co-located PENALTIES_RULES for all aesthetic decisions.
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
            KeyError: If an unmapped key is encountered in PENALTIES_RULES.
        """
        blocks: list[AnySduiBlock] = []

        source_data = context.penalties_applied

        if not source_data:
            return blocks

        for p_str in source_data:
            # Fail-Fast: strict key access, NO .get() fallback
            aesthetics = PENALTIES_RULES["default_penalty"]

            blocks.append(
                AlertBlock(
                    severity=aesthetics["severity"],
                    text=f"Penalty applied: {p_str}",
                    exact_quotes=[],
                    citations=[],
                )
            )

        return blocks

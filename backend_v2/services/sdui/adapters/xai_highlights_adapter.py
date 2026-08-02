"""XAI Highlights SDUI Adapter.

Transforms extracted XAI extensions into polymorphic AnySduiBlock components
for Server-Driven UI rendering. Visual rules are co-located as a module-level
AESTHETICS_RULES dictionary to enforce separation of presentation from logic.
"""

import logging

from backend_v2.models.enums import VisualIntent
from backend_v2.models.view.sdui import AnySduiBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext

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

XAI_AESTHETICS_RULES: dict[str, dict[str, str | VisualIntent]] = {
    # NOTE: Full aesthetic rule mapping for severity/icon is populated in Phase 6
    # when the _add_ext closure is extracted from the God Method.
    # This Phase 2 adapter simply flattens pre-built AccordionBlock lists
    # from accumulated_extensions.
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


class XaiHighlightsAdapter:
    """Transforms XAI highlights into SDUI visual blocks.

    Uses co-located XAI_AESTHETICS_RULES for all aesthetic decisions.
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

        if not context.accumulated_extensions:
            return blocks

        for ext_blocks in context.accumulated_extensions.values():
            blocks.extend(ext_blocks)

        return blocks

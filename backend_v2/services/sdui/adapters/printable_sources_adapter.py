"""Printable Sources SDUI Adapter.

Transforms cited sources into polymorphic AnySduiBlock components
for Server-Driven UI rendering. Visual rules are co-located as a module-level
AESTHETICS_RULES dictionary to enforce separation of presentation from logic.
"""

import logging
from typing import Any

from backend_v2.models.view.sdui import (
    AnySduiBlock,
    MarkdownBlock,
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

PRINTABLE_SOURCES_RULES: dict[str, Any] = {}


# ============================================================================
# SECTION 2: ADAPTER CLASS
# ============================================================================
# This class is a stateless transformer. It reads data from AdapterContext,
# looks up visual properties from SECTION 1, and assembles SDUI blocks.
# ============================================================================


class PrintableSourcesAdapter:
    """Transforms printable sources into SDUI visual blocks.

    Uses co-located PRINTABLE_SOURCES_RULES for all aesthetic decisions.
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

        # 1. READ: Extract only the data this adapter needs from the context
        profile_cache = context.profile_cache

        if not profile_cache or not profile_cache.cited_sources:
            return blocks

        # 2. TRANSFORM: Iterate and assemble blocks
        md_lines = []
        for src in profile_cache.cited_sources:
            if not src.strip().startswith("-"):
                md_lines.append(f"- {src}")
            else:
                md_lines.append(src)

        md_content = "\n".join(md_lines)
        blocks.append(MarkdownBlock(text=md_content))

        return blocks

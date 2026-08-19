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

        cited_urls: set[str] = set()
        md_lines: list[str] = []

        if profile_cache and profile_cache.cited_sources:
            for src in profile_cache.cited_sources:
                clean_src = src.strip()
                if not clean_src:
                    continue
                formatted = clean_src if clean_src.startswith("- ") else f"- {clean_src}"
                if formatted not in md_lines:
                    md_lines.append(formatted)
                if "http" in clean_src:
                    clean_url = clean_src.removeprefix("- ").strip()
                    cited_urls.add(clean_url)

        # Extract source URLs from Tavily search / MCP Audit tools
        if context.mcp_audit_map:
            for trace in context.mcp_audit_map.values():
                if trace.source_urls:
                    for url in trace.source_urls:
                        clean_u = url.strip()
                        if clean_u and clean_u not in cited_urls:
                            formatted = f"- {clean_u}"
                            if formatted not in md_lines:
                                md_lines.append(formatted)
                            cited_urls.add(clean_u)

        if not md_lines:
            return blocks

        md_content = "\n".join(md_lines)
        blocks.append(MarkdownBlock(text=md_content))

        return blocks

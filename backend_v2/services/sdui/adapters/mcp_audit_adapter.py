"""MCP Audit Trail SDUI Adapter.

Transforms execution MCP audit trail into a SduiAuditTrailBlock component
for Server-Driven UI rendering. Visual rules are co-located as a module-level
AESTHETICS_RULES dictionary to enforce separation of presentation from logic.
"""

import logging

from backend_v2.models.view.sdui import AnySduiBlock, SduiAuditTrailBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext

logger = logging.getLogger(__name__)


# ============================================================================
# SECTION 1: AESTHETICS RULES
# ============================================================================

AESTHETICS_RULES: dict[str, dict[str, str]] = {
    "default": {
        "visual_intent": "secondary",
    }
}


# ============================================================================
# SECTION 2: ADAPTER CLASS
# ============================================================================


class McpAuditAdapter:
    """Transforms execution MCP audit data into an SDUI visual block.

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

        if context.is_data_starved or not context.mcp_audit_map:
            return blocks
            # We map any needed structure here. The SduiAuditTrailBlock
            # currently does not enforce specific fields but can be expanded.
            blocks.append(SduiAuditTrailBlock())

        return blocks

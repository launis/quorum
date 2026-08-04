"""Metadata SDUI Adapter.

Transforms execution metadata into a HeaderBlock component
for Server-Driven UI rendering. Visual rules are co-located as a module-level
AESTHETICS_RULES dictionary to enforce separation of presentation from logic.
"""

import logging
from datetime import datetime

from backend_v2.models.view.sdui import AnySduiBlock, HeaderBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext

logger = logging.getLogger(__name__)


# ============================================================================
# SECTION 1: AESTHETICS RULES
# ============================================================================

METADATA_RULES: dict[str, dict[str, str]] = {
    "default_metadata": {
        "badge_status": "STATUS",
    }
}


# ============================================================================
# SECTION 2: ADAPTER CLASS
# ============================================================================


class MetadataAdapter:
    """Transforms execution metadata into SDUI visual blocks.

    Uses co-located METADATA_RULES for all aesthetic decisions.
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

        title = context.profile.name.resolve(context.locale) if context.profile and context.profile.name else "Raportti"

        badges = []
        if context.execution and hasattr(context.execution, "status"):
            status_val = context.execution.status
            if isinstance(status_val, str):
                badges.append(status_val.upper())
            elif hasattr(status_val, "value"):
                badges.append(str(status_val.value).upper())
            else:
                badges.append(str(status_val).upper())

        metadata_lines = []

        if context.user_name:
            metadata_lines.append(f"Käyttäjä: {context.user_name}")
        if context.org_name:
            metadata_lines.append(f"Organisaatio: {context.org_name}")

        if context.execution and context.execution.created_at:
            dt = context.execution.created_at
            if isinstance(dt, datetime):
                metadata_lines.append(dt.strftime("%d.%m.%Y %H:%M"))
            else:
                metadata_lines.append(str(dt))

        custom_preface = getattr(context.profile, "custom_preamble", None)

        blocks.append(
            HeaderBlock(
                title=title,
                badges=badges,
                metadata_lines=metadata_lines,
                costs=None,
                tokens=None,
                custom_preface_md=custom_preface,
            )
        )

        return blocks

"""Metadata SDUI Adapter.

Transforms execution metadata into a HeaderBlock component
for Server-Driven UI rendering. Visual rules are co-located as a module-level
AESTHETICS_RULES dictionary to enforce separation of presentation from logic.
"""

import logging
from datetime import datetime

from backend_v2.models.view.sdui import AnySduiBlock, SduiMetadataBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext

logger = logging.getLogger(__name__)


# ============================================================================
# SECTION 1: AESTHETICS RULES
# ============================================================================

METADATA_RULES: dict[str, dict[str, str]] = {"default_metadata": {}}


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

        metadata_lines = []
        costs_val = None
        tokens_val = None

        visible_fields = (
            context.profile.visible_metadata if context.profile and context.profile.visible_metadata else []
        )

        for field in visible_fields:
            if field == "user" and context.user_name:
                metadata_lines.append(f"Käyttäjä: {context.user_name}")
            elif field == "organization" and context.org_name:
                metadata_lines.append(f"Organisaatio: {context.org_name}")
            elif field == "date" and context.execution:
                if context.local_time_str:
                    metadata_lines.append(context.local_time_str)
                elif context.execution.created_at:
                    dt = context.execution.created_at
                    if isinstance(dt, datetime):
                        metadata_lines.append(dt.strftime("%d.%m.%Y %H:%M"))
                    else:
                        metadata_lines.append(str(dt))
            elif field == "scoring_engine" and context.scoring_engine:
                metadata_lines.append(f"Arviointimoottori: {context.scoring_engine}")
            elif field == "strictness" and context.profile.strictness_level is not None:
                metadata_lines.append(f"Ankaruustaso: {context.profile.strictness_level}")
            elif field == "cost" and context.cost is not None:
                costs_val = f"${context.cost:.2f}"
            elif field == "tokens" and context.tokens is not None:
                tokens_val = {"total": str(context.tokens)}

        custom_preface = getattr(context.profile, "custom_preamble", None)

        blocks.append(
            SduiMetadataBlock(
                title=title,
                badges=[],
                metadata_lines=metadata_lines,
                costs=costs_val,
                tokens=tokens_val,
                custom_preface_md=custom_preface,
            )
        )

        return blocks

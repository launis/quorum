"""Metadata SDUI Adapter.

Transforms execution metadata into a HeaderBlock component
for Server-Driven UI rendering. Visual rules are co-located as a module-level
AESTHETICS_RULES dictionary to enforce separation of presentation from logic.
"""

import logging

from backend_v2.models.view.sdui import AnySduiBlock, SduiMetadataBlock
from backend_v2.services.localization import LocalizationService
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext

__all__ = ["METADATA_RULES", "MetadataAdapter"]

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

        Raises:
            AppException: If profile or profile name is missing.
        """
        blocks: list[AnySduiBlock] = []

        title = context.profile.name.resolve(context.locale)

        metadata_lines: list[str] = []
        costs_val: str | None = None
        tokens_val: dict[str, str] | None = None

        visible_fields = context.profile.visible_metadata or []

        for field in visible_fields:
            if field == "user" and context.user_name:
                lbl = LocalizationService.translate("metadata_user", context.locale)
                metadata_lines.append(f"{lbl}: {context.user_name}")
            elif field == "organization" and context.org_name:
                lbl = LocalizationService.translate("metadata_organization", context.locale)
                metadata_lines.append(f"{lbl}: {context.org_name}")
            elif field == "date" and context.execution:
                if context.local_time_str:
                    metadata_lines.append(context.local_time_str)
                elif context.execution.created_at:
                    metadata_lines.append(LocalizationService.format_date(context.execution.created_at, context.locale))
            elif field == "scoring_engine" and context.scoring_engine:
                lbl = LocalizationService.translate("metadata_scoring_engine", context.locale)
                metadata_lines.append(f"{lbl}: {context.scoring_engine}")
            elif field == "strictness" and context.profile.strictness_level is not None:
                lbl = LocalizationService.translate("metadata_strictness", context.locale)
                metadata_lines.append(f"{lbl}: {context.profile.strictness_level}")
            elif field == "cost" and context.cost is not None:
                costs_val = LocalizationService.format_cost(context.cost, context.locale)
            elif field == "tokens" and context.tokens is not None:
                tokens_val = {"total": str(context.tokens)}

        custom_preface = (
            context.profile.custom_preface.resolve(context.locale) if context.profile.custom_preface else None
        )

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

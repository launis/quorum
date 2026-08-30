"""XAI Highlights SDUI Adapter.

Transforms extracted XAI extensions into polymorphic AnySduiBlock components
for Server-Driven UI rendering. Visual rules are co-located as a module-level
XAI_AESTHETICS_RULES dictionary to enforce separation of presentation from logic.
"""

import logging
from typing import Any, Literal, cast

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.enums import VisualIntent, XaiExtensionType
from backend_v2.models.view.sdui import AccordionBlock, AlertBlock, AnySduiBlock
from backend_v2.services.localization import LocalizationService
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.utils.ranked_round_robin import ranked_round_robin_select

__all__ = ["XAI_AESTHETICS_RULES", "XaiHighlightsAdapter"]

logger = logging.getLogger(__name__)


# ============================================================================
# SECTION 1: AESTHETICS RULES
# ============================================================================
XAI_AESTHETICS_RULES: dict[str, dict[str, Any]] = {
    "coaching": {"severity": VisualIntent.SUCCESS, "icon_name": "lightbulb"},
    "falsification": {"severity": VisualIntent.ERROR, "icon_name": "warning"},
    "risk_flag": {"severity": VisualIntent.ERROR, "icon_name": "flag"},
    "remediation_steps": {"severity": VisualIntent.WARNING, "icon_name": "build"},
    "missing_context": {"severity": VisualIntent.WARNING, "icon_name": "help_outline"},
    "emotional_sentiment": {"severity": VisualIntent.INFO, "icon_name": "mood"},
    "theory_link": {"severity": VisualIntent.INFO, "icon_name": "menu_book"},
    "justification": {"severity": VisualIntent.INFO, "icon_name": "fact_check"},
    "citation": {"severity": VisualIntent.INFO, "icon_name": "format_quote"},
    "confidence": {"severity": VisualIntent.INFO, "icon_name": "verified"},
    "source_id": {"severity": VisualIntent.INFO, "icon_name": "link"},
    "contextual_override": {"severity": VisualIntent.WARNING, "icon_name": "bolt"},
}


# ============================================================================
# SECTION 2: ADAPTER CLASS
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

        Raises:
            KeyError: If an unmapped key is encountered in XAI_AESTHETICS_RULES.
                This is intentional Fail-Fast behavior indicating incomplete
                rules configuration.
            AppException: If domain validation fails.
        """
        blocks: list[AnySduiBlock] = []

        profile_cache = context.profile_cache
        profile = context.profile
        locale = context.locale

        if context.is_data_starved or not profile_cache or not profile_cache.xai_highlights:
            return blocks

        if profile.max_extension_items == 0:
            return blocks

        if not profile.visible_block_extensions:
            return blocks

        highlights = profile_cache.xai_highlights
        valid_highlights = []
        for h in highlights:
            if not h.extension_type or not h.content:
                continue
            try:
                ext_enum = XaiExtensionType(h.extension_type)
                if profile.visible_block_extensions and ext_enum in profile.visible_block_extensions:
                    valid_highlights.append(h)
            except ValueError:
                logger.warning("[XaiHighlightsAdapter] LLM hallucinated extension type: %s", h.extension_type)
                continue

        if not valid_highlights:
            return blocks

        max_lines_per_type = profile.max_extension_items if profile.max_extension_items is not None else 3
        num_visible_types = len(profile.visible_block_extensions) if profile.visible_block_extensions else 1
        max_total_items = max_lines_per_type * num_visible_types

        curated_highlights = ranked_round_robin_select(
            items=valid_highlights,
            group_key=lambda h: h.extension_type,
            rank_key=lambda h: len(h.content),
            max_items=max_total_items,
            reverse_rank=True,
        )

        global_exts: list[AccordionBlock] = []

        for item in curated_highlights:
            ext_type_str = item.extension_type
            content_str = item.content

            if not ext_type_str or not content_str:
                continue

            try:
                ext_enum = XaiExtensionType(ext_type_str)
            except ValueError:
                logger.warning("[XaiHighlightsAdapter] LLM hallucinated extension type: %s", ext_type_str)
                continue

            try:
                aesthetics = XAI_AESTHETICS_RULES[ext_type_str]
            except KeyError as e:
                logger.error(
                    "[XaiHighlightsAdapter] %s: Missing rule mapping for extension key: %s",
                    ErrorCodes.CONFIGURATION_ERROR.name,
                    ext_type_str,
                    exc_info=True,
                )
                raise AppException(
                    message=f"Missing rule mapping for extension key: {ext_type_str}",
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                ) from e

            label_str = LocalizationService.translate(f"xai_ext_{ext_type_str}", locale)

            if profile.visible_block_extensions and ext_enum in profile.visible_block_extensions:
                acc_severity = aesthetics["severity"]
                acc_icon = aesthetics["icon_name"]

                acc_severity_literal = cast(
                    Literal["info", "warning", "critical_override", "success", "error", "default"],
                    acc_severity.value,
                )

                max_lines = profile.max_extension_items or 3

                accordion = next(
                    (b for b in global_exts if b.title == label_str),
                    None,
                )
                if not accordion:
                    accordion = AccordionBlock(
                        title=label_str, severity=acc_severity_literal, icon_name=acc_icon, children=[]
                    )
                    global_exts.append(accordion)

                if len(accordion.children) < max_lines:
                    if not any(isinstance(c, AlertBlock) and c.text == content_str for c in accordion.children):
                        block = AlertBlock(
                            severity=VisualIntent.INFO,
                            text=content_str,
                            exact_quotes=[],
                            citations=[],
                        )
                        accordion.children.append(block)

        blocks.extend(cast(list[AnySduiBlock], global_exts))
        return blocks

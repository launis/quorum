"""XAI Highlights SDUI Adapter.

Transforms extracted XAI extensions into polymorphic AnySduiBlock components
for Server-Driven UI rendering. Visual rules are co-located as a module-level
XAI_AESTHETICS_RULES DTO to enforce separation of presentation from logic.
"""

from __future__ import annotations

import logging
from typing import Literal, cast

from fastapi import status

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.sdui_rules import XaiAestheticsItemDTO, XaiAestheticsRulesDTO
from backend_v2.models.dtos.synthesis import XaiHighlightItem
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
XAI_AESTHETICS_RULES: XaiAestheticsRulesDTO = XaiAestheticsRulesDTO(
    rules={
        "coaching": XaiAestheticsItemDTO(severity=VisualIntent.SUCCESS, icon_name="lightbulb"),
        "falsification": XaiAestheticsItemDTO(severity=VisualIntent.ERROR, icon_name="warning"),
        "risk_flag": XaiAestheticsItemDTO(severity=VisualIntent.ERROR, icon_name="flag"),
        "remediation_steps": XaiAestheticsItemDTO(severity=VisualIntent.WARNING, icon_name="build"),
        "missing_context": XaiAestheticsItemDTO(severity=VisualIntent.WARNING, icon_name="help_outline"),
        "emotional_sentiment": XaiAestheticsItemDTO(severity=VisualIntent.INFO, icon_name="mood"),
        "theory_link": XaiAestheticsItemDTO(severity=VisualIntent.INFO, icon_name="menu_book"),
        "justification": XaiAestheticsItemDTO(severity=VisualIntent.INFO, icon_name="fact_check"),
        "citation": XaiAestheticsItemDTO(severity=VisualIntent.INFO, icon_name="format_quote"),
        "confidence": XaiAestheticsItemDTO(severity=VisualIntent.INFO, icon_name="verified"),
        "source_id": XaiAestheticsItemDTO(severity=VisualIntent.INFO, icon_name="link"),
        "contextual_override": XaiAestheticsItemDTO(severity=VisualIntent.WARNING, icon_name="bolt"),
    }
)

_VALID_XAI_TYPES: frozenset[str] = frozenset(e.value for e in XaiExtensionType)


# ============================================================================
# SECTION 2: ADAPTER CLASS
# ============================================================================
class XaiHighlightsAdapter:
    """Transforms XAI highlights into SDUI visual blocks.

    Uses co-located XAI_AESTHETICS_RULES for all aesthetic decisions.
    Stateless: no instance state, no side effects.
    """

    @staticmethod
    def _filter_valid_highlights(
        highlights: list[XaiHighlightItem],
        visible_extensions: list[XaiExtensionType],
    ) -> list[XaiHighlightItem]:
        """Filter XAI highlights to non-empty items matching visible block extensions.

        Args:
            highlights: Raw extracted XAI highlight items from synthesis cache.
            visible_extensions: Configured visible block extension types from OutputProfile.

        Returns:
            Filtered list of valid XaiHighlightItem instances.
        """
        valid_highlights: list[XaiHighlightItem] = []
        for item in highlights:
            if not item.extension_type or not item.content:
                continue
            if item.extension_type not in _VALID_XAI_TYPES:
                logger.warning("[XaiHighlightsAdapter] LLM hallucinated extension type: %s", item.extension_type)
                continue
            ext_enum = XaiExtensionType(item.extension_type)
            if ext_enum in visible_extensions:
                valid_highlights.append(item)
        return valid_highlights

    @staticmethod
    def _resolve_aesthetics(ext_type_str: str) -> XaiAestheticsItemDTO:
        """Resolve visual styling rules for an XAI extension key.

        Args:
            ext_type_str: Validated extension type key string.

        Returns:
            Matched XaiAestheticsItemDTO for the extension type.

        Raises:
            AppException: If an unmapped key is encountered in XAI_AESTHETICS_RULES
                (ErrorCodes.CONFIGURATION_ERROR).
        """
        try:
            return XAI_AESTHETICS_RULES[ext_type_str]
        except KeyError as e:
            logger.error(
                "[XaiHighlightsAdapter] %s: Missing rule mapping for extension key: %s",
                ErrorCodes.CONFIGURATION_ERROR.name,
                ext_type_str,
                exc_info=True,
            )
            raise AppException(
                message=f"Missing rule mapping for extension key: {ext_type_str}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            ) from e

    @staticmethod
    def _append_highlight_block(
        accordions: list[AccordionBlock],
        item: XaiHighlightItem,
        max_lines: int,
        locale: str,
    ) -> None:
        """Append a curated XAI highlight item into its localized AccordionBlock group.

        Args:
            accordions: Accumulator list of grouped AccordionBlock instances.
            item: Curated XaiHighlightItem to insert.
            max_lines: Maximum children permitted per AccordionBlock.
            locale: Active presentation locale code.

        Raises:
            AppException: If an unmapped key is encountered in XAI_AESTHETICS_RULES
                (ErrorCodes.CONFIGURATION_ERROR).
        """
        ext_type_str = item.extension_type
        content_str = item.content
        aesthetics = XaiHighlightsAdapter._resolve_aesthetics(ext_type_str)
        label_str = LocalizationService.translate(f"xai_ext_{ext_type_str}", locale)

        acc_severity_literal = cast(
            Literal["info", "warning", "critical_override", "success", "error", "default"],
            aesthetics.severity.value,
        )

        accordion = next((b for b in accordions if b.title == label_str), None)
        if accordion is None:
            accordion = AccordionBlock(
                title=label_str,
                severity=acc_severity_literal,
                icon_name=aesthetics.icon_name,
                children=[],
            )
            accordions.append(accordion)

        if len(accordion.children) < max_lines:
            if not any(isinstance(c, AlertBlock) and c.text == content_str for c in accordion.children):
                accordion.children.append(
                    AlertBlock(
                        severity=VisualIntent.INFO,
                        text=content_str,
                        exact_quotes=[],
                        citations=[],
                    )
                )

    @staticmethod
    def build(context: AdapterContext) -> list[AnySduiBlock]:
        """Build SDUI blocks from the adapter context.

        Args:
            context: Frozen, immutable adapter context containing all
                required data for block construction.

        Returns:
            Ordered list of polymorphic SDUI blocks ready for rendering.

        Raises:
            AppException: If an unmapped key is encountered in XAI_AESTHETICS_RULES
                (ErrorCodes.CONFIGURATION_ERROR).
        """
        blocks: list[AnySduiBlock] = []

        profile_cache = context.profile_cache
        profile = context.profile

        if context.is_data_starved or not profile_cache or not profile_cache.xai_highlights:
            return blocks

        if profile.max_extension_items <= 0 or not profile.visible_block_extensions:
            return blocks

        valid_highlights = XaiHighlightsAdapter._filter_valid_highlights(
            highlights=profile_cache.xai_highlights,
            visible_extensions=profile.visible_block_extensions,
        )
        if not valid_highlights:
            return blocks

        max_lines_per_type = profile.max_extension_items
        max_total_items = max_lines_per_type * len(profile.visible_block_extensions)

        curated_highlights = ranked_round_robin_select(
            items=valid_highlights,
            group_key=lambda h: h.extension_type,
            rank_key=lambda h: len(h.content),
            max_items=max_total_items,
            reverse_rank=True,
        )

        global_exts: list[AccordionBlock] = []
        for item in curated_highlights:
            XaiHighlightsAdapter._append_highlight_block(
                accordions=global_exts,
                item=item,
                max_lines=max_lines_per_type,
                locale=context.locale,
            )

        blocks.extend(global_exts)
        return blocks

"""XAI Highlights SDUI Adapter.

Transforms extracted XAI extensions into polymorphic AnySduiBlock components
for Server-Driven UI rendering. Visual rules are co-located as a module-level
XAI_AESTHETICS_RULES dictionary to enforce separation of presentation from logic.
"""

import logging
from typing import Any, Literal, cast

from backend_v2.exceptions import AppException, ConfigurationError
from backend_v2.models.enums import VisualIntent, XaiExtensionType
from backend_v2.models.view.sdui import AccordionBlock, AlertBlock, AnySduiBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext

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
        """
        blocks: list[AnySduiBlock] = []

        if not context.profile_cache or not context.profile_cache.xai_highlights:
            return blocks

        profile = context.profile
        locale = context.locale

        global_exts: list[AccordionBlock] = []
        highlights = context.profile_cache.xai_highlights

        for item in highlights:
            ext_type_str = (
                item.get("extension_type") if isinstance(item, dict) else getattr(item, "extension_type", None)
            )
            content_str = item.get("content") if isinstance(item, dict) else getattr(item, "content", None)

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
                logger.error("[XaiHighlightsAdapter] Missing rule mapping for extension key: %s", ext_type_str, exc_info=True)
                raise AppException(
                    message=f"Missing rule mapping for extension key: {ext_type_str}",
                    status_code=500,
                    details={"error_code": "CONFIGURATION_ERROR"}
                ) from e

            label_obj = profile.extension_labels.get(ext_enum) if profile.extension_labels else None
            if not label_obj:
                raise ConfigurationError(
                    f"Missing extension label configuration for {ext_type_str} in profile SSOT",
                    details={"extension_key": ext_type_str},
                )

            if profile.visible_block_extensions and ext_enum in profile.visible_block_extensions:
                label_str = label_obj.resolve(locale)

                acc_severity = aesthetics["severity"]
                acc_icon = aesthetics["icon_name"]

                acc_severity_literal = cast(
                    Literal["info", "warning", "critical_override", "success", "error", "default"],
                    acc_severity.value,
                )

                max_lines = profile.max_extension_items if profile.max_extension_items else 999

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

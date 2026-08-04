"""Synthesis Text SDUI Adapter.

Transforms synthesis markdown into SDUI visual blocks
for Server-Driven UI rendering. Visual rules are co-located as a module-level
AESTHETICS_RULES dictionary to enforce separation of presentation from logic.
"""

import logging
import re

import bleach

from backend_v2.models.view.sdui import AnySduiBlock, MarkdownBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext

logger = logging.getLogger(__name__)


# ============================================================================
# SECTION 1: AESTHETICS RULES
# ============================================================================

SYNTHESIS_TEXT_RULES: dict[str, dict[str, str]] = {
    "default_text": {
        "mode": "standard",
    }
}


# ============================================================================
# SECTION 2: ADAPTER CLASS
# ============================================================================


class SynthesisTextAdapter:
    """Transforms synthesis markdown into SDUI visual blocks.

    Uses co-located SYNTHESIS_TEXT_RULES for all aesthetic decisions.
    Stateless: no instance state, no side effects.
    """

    @staticmethod
    def _apply_pii_masking(text: str) -> str:
        """Applies regex-based PII masking to text."""
        text = re.sub(r"[\w\.-]+@[\w\.-]+", "[REDACTED EMAIL]", text)
        text = re.sub(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "[REDACTED PHONE]", text)
        return text

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

        # 1. READ: Insert pre-defined content blocks from profile
        if context.profile and context.profile.content_blocks:
            for cb in context.profile.content_blocks:
                blocks.append(cb.model_copy(deep=True))

        # 2. TRANSFORM: Insert synthesis text
        if context.synthesis_md:
            text = context.synthesis_md

            # Apply PII masking if requested by profile layouts
            pii_masking = False
            if context.profile and hasattr(context.profile, "layouts") and context.profile.layouts:
                for layout in context.profile.layouts:
                    if getattr(layout, "pii_masking", False):
                        pii_masking = True
                        break

            if pii_masking:
                text = SynthesisTextAdapter._apply_pii_masking(text)

            # Apply HTML sanitization
            text = bleach.clean(
                text,
                tags=[
                    "b",
                    "i",
                    "strong",
                    "em",
                    "p",
                    "br",
                    "ul",
                    "ol",
                    "li",
                    "a",
                    "h1",
                    "h2",
                    "h3",
                    "h4",
                    "h5",
                    "h6",
                    "blockquote",
                    "code",
                    "pre",
                ],
                attributes={"a": ["href", "title"]},
                strip=True,
            )

            blocks.append(MarkdownBlock(text=text))

        return blocks

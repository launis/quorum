"""Penalties SDUI Adapter.

Transforms applied penalty strings into polymorphic AlertBlocks
for Server-Driven UI rendering. Visual rules are co-located as a module-level
AESTHETICS_RULES dictionary to enforce separation of presentation from logic.
"""

import logging
from typing import Any

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.enums import VisualIntent
from backend_v2.models.view.sdui import (
    AlertBlock,
    AnySduiBlock,
)
from backend_v2.services.localization import LocalizationService
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext

logger = logging.getLogger(__name__)


# ============================================================================
# SECTION 1: AESTHETICS RULES
# ============================================================================
# All visual decisions (severity, icon, label) are defined here as a flat
# dictionary. The adapter class below MUST NOT contain any if/elif/else
# chains for visual property selection.
# ============================================================================

PENALTIES_RULES: dict[str, dict[str, Any]] = {
    "PENALTY_SECURITY": {
        "severity": VisualIntent.CRITICAL_OVERRIDE,
        "title_key": "penalty_security_title",
        "desc_key": "penalty_security_description",
    },
    "PENALTY_POST_HOC": {
        "severity": VisualIntent.WARNING,
        "title_key": "penalty_post_hoc_title",
        "desc_key": "penalty_post_hoc_description",
    },
    "PENALTY_PASSIVITY": {
        "severity": VisualIntent.WARNING,
        "title_key": "penalty_passivity_title",
        "desc_key": "penalty_passivity_description",
    },
}


# ============================================================================
# SECTION 2: ADAPTER CLASS
# ============================================================================
# This class is a stateless transformer. It reads data from AdapterContext,
# looks up visual properties from SECTION 1, and assembles SDUI blocks.
# ============================================================================


class PenaltiesAdapter:
    """Transforms applied penalties into SDUI visual blocks.

    Uses co-located PENALTIES_RULES for all aesthetic decisions.
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
            AppException: If an unmapped penalty token is encountered in PENALTIES_RULES.
        """
        blocks: list[AnySduiBlock] = []

        source_data = context.penalties_applied

        if context.is_data_starved or not source_data:
            return blocks

        for p_str in source_data:
            if ":" in p_str:
                token, pct_str = p_str.split(":", 1)
            else:
                token, pct_str = p_str, None

            # Fail-Fast: strict key access, NO .get() fallback
            try:
                aesthetics = PENALTIES_RULES[token]
            except KeyError as e:
                msg = f"Missing rule mapping for penalty token: '{token}'"
                logger.error("[PenaltiesAdapter] CONFIGURATION_ERROR: %s", msg, exc_info=True)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                ) from e

            title = LocalizationService.translate(aesthetics["title_key"], context.locale)
            desc = LocalizationService.translate(aesthetics["desc_key"], context.locale)

            if pct_str is not None:
                pct_suffix = f" (-{pct_str} %)" if context.locale == "fi" else f" (-{pct_str}%)"
                header = f"{title}{pct_suffix}"
            else:
                header = title

            alert_text = f"{header}: {desc}"

            blocks.append(
                AlertBlock(
                    id=f"alert_penalty_{token.lower()}",
                    severity=aesthetics["severity"],
                    text=alert_text,
                    exact_quotes=[],
                    citations=[],
                )
            )

        return blocks

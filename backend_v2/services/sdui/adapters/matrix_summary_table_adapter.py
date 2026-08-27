"""Matrix Summary Table SDUI Adapter.

Transforms parsed matrix data into a polymorphic Matrix Table block.
Visual rules are co-located as a module-level MATRIX_SUMMARY_RULES dictionary to enforce separation of presentation from logic.
"""

import logging

from backend_v2.models.core_base import I18nText
from backend_v2.models.view.sdui import (
    AnySduiBlock,
    SduiMatrixTableBlock,
)
from backend_v2.services.localization import LocalizationService
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext

logger = logging.getLogger(__name__)

# ============================================================================
# SECTION 1: AESTHETICS RULES
# ============================================================================

MATRIX_SUMMARY_RULES: dict[str, dict[str, int]] = {
    "matrix_summary": {"min_axes": 1},
}

STANDARD_COLUMNS: list[str] = [
    "label",
    "distribution",
    "row_explanation",
    "quotes",
    "normalized_score",
    "score",
]


# ============================================================================
# SECTION 2: ADAPTER CLASS
# ============================================================================
class MatrixSummaryTableAdapter:
    """Transforms parsed matrix data into SDUI matrix table blocks.

    Uses co-located MATRIX_SUMMARY_RULES for structural validation.
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

        if context.is_data_starved or not context.parsed_matrices:
            return blocks

        axes = list(context.parsed_matrices.values())

        visible_columns = (
            context.profile.matrix_visible_columns if context.profile.matrix_visible_columns else STANDARD_COLUMNS
        )

        col_labels: dict[str, I18nText] = {}
        for col in visible_columns:
            key = f"matrix_col_{col}"
            col_labels[col] = I18nText(
                translations={
                    "fi": LocalizationService.translate(key, "fi"),
                    "en": LocalizationService.translate(key, "en"),
                }
            )

        blocks.append(
            SduiMatrixTableBlock(
                title=None,
                axes=axes,
                matrix_column_labels=col_labels,
                matrix_visible_columns=visible_columns,
                extension_labels={},
            )
        )

        return blocks

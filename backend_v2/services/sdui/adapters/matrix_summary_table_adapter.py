"""Matrix Summary Table SDUI Adapter.

Transforms parsed matrix data into a polymorphic Matrix Table block.
Visual rules are co-located as a module-level MATRIX_SUMMARY_RULES dictionary to enforce separation of presentation from logic.
"""

import logging
from typing import Any

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.view.sdui import (
    AnySduiBlock,
    ParagraphBlock,
    SduiMatrixTableBlock,
)
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext

logger = logging.getLogger(__name__)

# ============================================================================
# SECTION 1: AESTHETICS RULES
# ============================================================================
# All visual layout requirements for matrix summary table blocks are defined here.
# Minimum axes is strictly enforced per KI: Adapters MUST NOT fallback
# if structurally incompatible.
# ============================================================================

MATRIX_SUMMARY_RULES: dict[str, dict[str, Any]] = {
    "matrix_summary": {"min_axes": 1},
}


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

        Raises:
            AppException: If domain validation fails (e.g. incompatible axes count).
        """
        blocks: list[AnySduiBlock] = []

        if not context.profile.layouts:
            return blocks

        locale = context.locale
        all_parsed_matrices = context.parsed_matrices
        section_syntheses = context.profile_cache.section_syntheses if context.profile_cache else {}

        for idx, layout_def in enumerate(context.profile.layouts):
            preset_view = layout_def.preset_view

            if preset_view not in MATRIX_SUMMARY_RULES:
                continue

            try:
                rule = MATRIX_SUMMARY_RULES[preset_view]
            except KeyError as e:
                msg = f"Missing rule mapping for preset_view: {preset_view}"
                logger.error("[MatrixSummaryTableAdapter] CONFIGURATION_ERROR: %s", msg, exc_info=True)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": "CONFIGURATION_ERROR"},
                ) from e

            target_blocks = layout_def.target_blocks
            axes = []
            if target_blocks and "*" not in target_blocks:
                for target_k in target_blocks:
                    matched = next((axis for axis in all_parsed_matrices.values() if axis.block_id == target_k), None)
                    if matched:
                        axes.append(matched)
            else:
                axes = list(all_parsed_matrices.values())

            # Fail-fast structural validation
            if len(axes) < rule["min_axes"]:
                msg = f"Structurally incompatible: layout '{preset_view}' requires at least {rule['min_axes']} axes, found {len(axes)}."
                logger.error(
                    "[MatrixSummaryTableAdapter] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, exc_info=True
                )
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )

            if axes or layout_def.synthesis:
                synthesis_config = layout_def.synthesis
                layout_id = f"layout_{idx}_{preset_view}"

                section_blocks: list[AnySduiBlock] | None = None
                if synthesis_config and layout_id in section_syntheses:
                    section_blocks = list(section_syntheses[layout_id])

                if layout_def.description:
                    blocks.append(
                        ParagraphBlock(text=layout_def.description.resolve(locale), exact_quotes=[], citations=[])
                    )

                if section_blocks:
                    blocks.extend(section_blocks)

                blocks.append(
                    SduiMatrixTableBlock(
                        title=layout_def.title,
                        axes=axes,
                        matrix_column_labels=layout_def.matrix_column_labels,
                        matrix_visible_columns=layout_def.matrix_visible_columns,
                        extension_labels=context.profile.extension_labels,
                    )
                )

        return blocks

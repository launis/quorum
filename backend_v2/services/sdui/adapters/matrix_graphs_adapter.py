"""Matrix Graphs SDUI Adapter.

Transforms parsed matrix data into polymorphic graph blocks (Radar, Scatter, Metrics).
Visual rules are co-located as a module-level MATRIX_GRAPHS_RULES dictionary to enforce separation of presentation from logic.
"""

import logging
from typing import Any

from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.models.view.sdui import (
    AnySduiBlock,
    ParagraphBlock,
    SduiMetrics1DBlock,
    SduiRadarChartBlock,
    SduiScatterPlotBlock,
)
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext

logger = logging.getLogger(__name__)

# ============================================================================
# SECTION 1: AESTHETICS RULES
# ============================================================================
# All visual layout requirements for graph blocks are defined here.
# Minimum axes is strictly enforced per KI: Adapters MUST NOT fallback
# if structurally incompatible.
# ============================================================================

MATRIX_GRAPHS_RULES: dict[str, dict[str, Any]] = {
    "3d_matrix": {"min_axes": 3},
    "2d_compare": {"min_axes": 2},
    "1d_metrics": {"min_axes": 1},
    "text_only": {"min_axes": 0},
}


# ============================================================================
# SECTION 2: ADAPTER CLASS
# ============================================================================
class MatrixGraphsAdapter:
    """Transforms parsed matrix data into SDUI graph blocks.

    Uses co-located MATRIX_GRAPHS_RULES for structural validation.
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
            ConfigurationError: If output profile specifies an invalid text delivery mode.
        """
        blocks: list[AnySduiBlock] = []

        if not context.profile.layouts:
            return blocks

        locale = context.locale
        all_parsed_matrices = context.parsed_matrices
        section_syntheses = context.profile_cache.section_syntheses if context.profile_cache else {}

        for idx, layout_def in enumerate(context.profile.layouts):
            preset_view = layout_def.preset_view

            # Only handle graph preset views
            if preset_view not in MATRIX_GRAPHS_RULES:
                continue

            text_delivery_mode = layout_def.text_delivery_mode
            if text_delivery_mode not in ("full", "titles_only", "none"):
                raise ConfigurationError(
                    f"Unrecognized text_delivery_mode: '{text_delivery_mode}'. Must be 'full', 'titles_only', or 'none'.",
                    details={"text_delivery_mode": text_delivery_mode},
                )

            target_blocks = layout_def.target_blocks
            axes = []
            if target_blocks and "*" not in target_blocks:
                for target_k in target_blocks:
                    matched = next((axis for axis in all_parsed_matrices.values() if axis.block_id == target_k), None)
                    if matched:
                        axes.append(matched)
            else:
                axes = list(all_parsed_matrices.values())

            # Fail-fast validation based on AESTHETICS RULES
            try:
                rule = MATRIX_GRAPHS_RULES[preset_view]
            except KeyError as e:
                msg = f"Missing rule mapping for preset_view: {preset_view}"
                logger.error("[MatrixGraphsAdapter] CONFIGURATION_ERROR: %s", msg, exc_info=True)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": "CONFIGURATION_ERROR"},
                ) from e

            if len(axes) < rule["min_axes"]:
                msg = f"Structurally incompatible: layout '{preset_view}' requires at least {rule['min_axes']} axes, found {len(axes)}."
                logger.error("[MatrixGraphsAdapter] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, exc_info=True)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )

            if text_delivery_mode in ["titles_only", "none"]:
                axes = [axis.model_copy(update={"inner_sdui_blocks": []}) for axis in axes]

            if axes or preset_view == "text_only" or layout_def.synthesis:
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

                if preset_view in ["3d_matrix", "2d_compare"] or text_delivery_mode != "none":
                    if preset_view == "3d_matrix":
                        blocks.append(SduiRadarChartBlock(title=layout_def.title, axes=axes))
                    elif preset_view == "2d_compare":
                        blocks.append(SduiScatterPlotBlock(title=layout_def.title, axes=axes))
                    elif preset_view in ["1d_metrics", "text_only"]:
                        blocks.append(SduiMetrics1DBlock(title=layout_def.title, axes=axes))

        return blocks

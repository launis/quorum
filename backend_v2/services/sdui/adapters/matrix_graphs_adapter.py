"""Matrix Graphs SDUI Adapter.

Transforms parsed matrix data into polymorphic graph blocks (Radar, Scatter, Metrics).
Visual rules are co-located as a module-level MATRIX_GRAPHS_RULES dictionary to enforce separation of presentation from logic.
"""

import logging
from typing import Any

from backend_v2.exceptions import AppException, ConfigurationError
from backend_v2.models.view.sdui import (
    AnySduiBlock,
    MarkdownBlock,
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
    "1d_metrics": {"min_axes": 0},
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
        seen_axes: set[str] = set()

        if context.is_data_starved or not context.profile.layouts:
            return blocks

        locale = context.locale
        all_parsed_matrices = context.parsed_matrices
        section_syntheses = context.profile_cache.section_syntheses if context.profile_cache else {}

        layouts_with_idx = list(enumerate(context.profile.layouts))

        for original_idx, layout_def in layouts_with_idx:
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
            consumes_axes = preset_view != "text_only" or text_delivery_mode != "none"
            axes = []
            if target_blocks and "*" not in target_blocks:
                for target_k in target_blocks:
                    matched = next((axis for axis in all_parsed_matrices.values() if axis.block_id == target_k), None)
                    if matched and matched.block_id not in seen_axes:
                        axes.append(matched)
                        if consumes_axes:
                            seen_axes.add(matched.block_id)
            else:
                for axis in all_parsed_matrices.values():
                    if axis.block_id not in seen_axes:
                        axes.append(axis)
                        if consumes_axes:
                            seen_axes.add(axis.block_id)

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
                original_preset = preset_view
                if len(axes) == 2:
                    preset_view = "2d_compare"
                else:
                    preset_view = "1d_metrics"

                msg = f"Gracefully degrading layout '{original_preset}' to '{preset_view}' because it requires at least {rule['min_axes']} axes, but found {len(axes)}."
                logger.warning("[MatrixGraphsAdapter] GRACEFUL_DEGRADATION: %s", msg)

            if text_delivery_mode in ["titles_only", "none"]:
                axes = [axis.model_copy(update={"inner_sdui_blocks": []}) for axis in axes]

            layout_id = f"layout_{original_idx}_{preset_view}"

            section_blocks: list[AnySduiBlock] | None = None
            if layout_def.is_synthesis_enabled and layout_id in section_syntheses:
                section_blocks = list(section_syntheses[layout_id])

            has_renderable_content = bool(
                axes or section_blocks or (preset_view == "text_only" and text_delivery_mode != "none")
            )

            if has_renderable_content:
                if layout_def.title:
                    blocks.append(MarkdownBlock(text=f"### {layout_def.title.resolve(locale)}"))
                if layout_def.description:
                    blocks.append(
                        ParagraphBlock(text=layout_def.description.resolve(locale), exact_quotes=[], citations=[])
                    )

                if section_blocks:
                    blocks.extend(section_blocks)

                if preset_view == "3d_matrix" and axes:
                    blocks.append(SduiRadarChartBlock(title=None, axes=axes))
                elif preset_view == "2d_compare" and axes:
                    blocks.append(SduiScatterPlotBlock(title=None, axes=axes))
                elif preset_view == "1d_metrics" and axes:
                    blocks.append(SduiMetrics1DBlock(title=None, axes=axes))
                elif preset_view == "text_only" and text_delivery_mode != "none":
                    for axis in axes:
                        if text_delivery_mode in ["full", "titles_only"]:
                            blocks.append(ParagraphBlock(text=f"**{axis.name}**", exact_quotes=[], citations=[]))
                        if text_delivery_mode == "full" and axis.row_explanation:
                            blocks.append(MarkdownBlock(text=axis.row_explanation))

        return blocks

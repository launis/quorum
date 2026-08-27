"""Matrix Graphs SDUI Adapter.

Transforms parsed matrix data into polymorphic graph blocks (Radar, Scatter, Metrics).
Visual rules are co-located as a module-level MATRIX_GRAPHS_RULES dictionary to enforce separation of presentation from logic.
"""

import logging

from backend_v2.models.view.sdui import (
    AnySduiBlock,
    MarkdownBlock,
    SduiMetrics1DBlock,
    SduiRadarChartBlock,
    SduiScatterPlotBlock,
)
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext

__all__ = ["MATRIX_GRAPHS_RULES", "MatrixGraphsAdapter"]

logger = logging.getLogger(__name__)

# ============================================================================
# SECTION 1: AESTHETICS RULES
# ============================================================================

MATRIX_GRAPHS_RULES: dict[str, dict[str, int]] = {
    "radar": {"min_axes": 3},
    "scatter": {"min_axes": 2},
    "metrics": {"min_axes": 1},
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
        """
        blocks: list[AnySduiBlock] = []
        seen_axes: set[str] = set()

        if context.is_data_starved or not context.profile.matrix_synthesis_groups:
            return blocks

        locale = context.locale
        all_parsed_matrices = context.parsed_matrices
        section_syntheses = context.profile_cache.section_syntheses if context.profile_cache else {}

        for grp in context.profile.matrix_synthesis_groups:
            target_blocks = grp.target_blocks
            axes = []
            if target_blocks and "*" not in target_blocks:
                for target_k in target_blocks:
                    matched = next((axis for axis in all_parsed_matrices.values() if axis.block_id == target_k), None)
                    if matched and matched.block_id not in seen_axes:
                        axes.append(matched)
                        seen_axes.add(matched.block_id)
            else:
                for axis in all_parsed_matrices.values():
                    if axis.block_id not in seen_axes:
                        axes.append(axis)
                        seen_axes.add(axis.block_id)

            group_id = grp.id
            section_blocks: list[AnySduiBlock] | None = None
            if group_id in section_syntheses:
                section_blocks = list(section_syntheses[group_id])

            has_renderable_content = bool(axes or section_blocks)

            if has_renderable_content:
                if grp.title:
                    blocks.append(MarkdownBlock(text=f"### {grp.title.resolve(locale)}"))

                if section_blocks:
                    blocks.extend(section_blocks)

                # Route graph block emission by deterministic view_type
                view_type = grp.view_type
                if view_type in ("3d_matrix", "matrix3d") and len(axes) >= 3:
                    blocks.append(SduiRadarChartBlock(title=None, axes=axes))
                elif view_type in ("2d_compare", "compare2d") and len(axes) >= 2:
                    blocks.append(SduiScatterPlotBlock(title=None, axes=axes[:2]))
                elif view_type in ("text_only", "textOnly"):
                    # Text-only synthesis group does not emit visual chart blocks
                    pass
                elif len(axes) >= 3:
                    blocks.append(SduiRadarChartBlock(title=None, axes=axes))
                elif len(axes) == 2:
                    blocks.append(SduiScatterPlotBlock(title=None, axes=axes[:2]))
                elif len(axes) == 1:
                    blocks.append(SduiMetrics1DBlock(title=None, axes=axes[:1]))

        return blocks

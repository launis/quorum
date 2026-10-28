"""Matrix Graphs SDUI Adapter.

Transforms parsed matrix data into polymorphic graph blocks (Radar, Scatter, Metrics).
Visual rules are co-located as a module-level MATRIX_GRAPHS_RULES instance to enforce
separation of presentation from logic.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.synthesis import MatrixSynthesisGroup
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO
from backend_v2.models.dtos.sdui_rules import MatrixGraphMinAxesDTO, MatrixGraphsAestheticsDTO
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

MATRIX_GRAPHS_RULES: MatrixGraphsAestheticsDTO = MatrixGraphsAestheticsDTO(
    rules={
        "radar": MatrixGraphMinAxesDTO(min_axes=3),
        "scatter": MatrixGraphMinAxesDTO(min_axes=2),
        "metrics": MatrixGraphMinAxesDTO(min_axes=1),
    }
)


# ============================================================================
# SECTION 2: ADAPTER CLASS
# ============================================================================
class MatrixGraphsAdapter:
    """Transforms parsed matrix data into SDUI graph blocks.

    Uses co-located MATRIX_GRAPHS_RULES for structural validation.
    Stateless: no instance state, no side effects.
    """

    @staticmethod
    def _resolve_axes(
        target_blocks: list[str],
        all_parsed_matrices: Mapping[str, MatrixScorecardRowDTO],
    ) -> list[MatrixScorecardRowDTO]:
        """Resolve matrix scorecard axes matching the synthesis group's target blocks.

        Args:
            target_blocks: List of target prompt block IDs or wildcard '*'.
            all_parsed_matrices: Mapping of composite or block keys to parsed matrix rows.

        Returns:
            Ordered list of matched MatrixScorecardRowDTO axes.
        """
        axes: list[MatrixScorecardRowDTO] = []
        if target_blocks and "*" not in target_blocks:
            for target_k in target_blocks:
                matched = next((axis for axis in all_parsed_matrices.values() if axis.block_id == target_k), None)
                if matched is not None:
                    axes.append(matched)
        else:
            for axis in all_parsed_matrices.values():
                axes.append(axis)
        return axes

    @staticmethod
    def _resolve_graph_block(
        grp: MatrixSynthesisGroup,
        axes: list[MatrixScorecardRowDTO],
    ) -> AnySduiBlock | None:
        """Route and construct the polymorphic SDUI graph block for a synthesis group.

        Args:
            grp: Matrix synthesis group configuration.
            axes: Resolved matrix scorecard axes for the group.

        Returns:
            Constructed SDUI graph block if minimum axis threshold is met, else None.

        Raises:
            AppException: If grp.view_type is unsupported (ErrorCodes.CONFIGURATION_ERROR).
        """
        view_type = grp.view_type
        match view_type:
            case "3d_matrix" | "matrix3d":
                if len(axes) >= MATRIX_GRAPHS_RULES["radar"].min_axes:
                    return SduiRadarChartBlock(title=grp.title, axes=axes)
                return None
            case "2d_compare" | "compare2d":
                if len(axes) >= MATRIX_GRAPHS_RULES["scatter"].min_axes:
                    return SduiScatterPlotBlock(title=grp.title, axes=axes[:2])
                return None
            case "1d_metrics" | "metrics1d" | "metrics":
                if len(axes) >= MATRIX_GRAPHS_RULES["metrics"].min_axes:
                    return SduiMetrics1DBlock(title=grp.title, axes=axes[:1])
                return None
            case "text_only" | "textOnly":
                # Text-only synthesis group does not emit visual chart blocks
                return None
            case _:
                logger.error(
                    "[MatrixGraphsAdapter] %s: Unsupported matrix graph view_type '%s'.",
                    ErrorCodes.CONFIGURATION_ERROR.name,
                    view_type,
                    extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "view_type": str(view_type)},
                    exc_info=True,
                )
                raise AppException(
                    message=f"Unsupported matrix graph view_type: {grp.view_type}",
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
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
            AppException: If a synthesis group specifies an unsupported view_type
                (ErrorCodes.CONFIGURATION_ERROR).
        """
        blocks: list[AnySduiBlock] = []

        if context.is_data_starved or not context.profile.matrix_synthesis_groups:
            return blocks

        all_parsed_matrices = context.parsed_matrices
        section_syntheses: Mapping[str, Sequence[AnySduiBlock]] = {}
        if context.profile_cache is not None and context.profile_cache.section_syntheses:
            section_syntheses = context.profile_cache.section_syntheses

        for grp in context.profile.matrix_synthesis_groups:
            axes = MatrixGraphsAdapter._resolve_axes(grp.target_blocks, all_parsed_matrices)
            group_id = grp.id
            section_blocks: list[AnySduiBlock] = []
            if group_id in section_syntheses:
                section_blocks = list(section_syntheses[group_id])

            if len(axes) > 0 or len(section_blocks) > 0:
                graph_block = MatrixGraphsAdapter._resolve_graph_block(grp, axes)
                if graph_block is not None:
                    blocks.append(graph_block)
                elif grp.title is not None and len(section_blocks) > 0:
                    blocks.append(MarkdownBlock(text=f"### {grp.title.resolve(context.locale)}"))

                if len(section_blocks) > 0:
                    blocks.extend(section_blocks)

        return blocks

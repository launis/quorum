"""Synthesis prompt registry for declarative SDUI block and view directive mappings.

Single Source of Truth (SSOT) mapping TargetBlockType enums and PresetView types
to static synthesis prompt directives.
"""

from typing import Final

from backend_v2.models.enums import PresetView, TargetBlockType
from backend_v2.models.prompts.synthesis_directives import (
    EXECUTIVE_SUMMARY_DIRECTIVE,
    MATRIX_1D_SYNTHESIS_DIRECTIVE,
    MATRIX_2D_SYNTHESIS_DIRECTIVE,
    MATRIX_3D_SYNTHESIS_DIRECTIVE,
    MATRIX_TEXT_SYNTHESIS_DIRECTIVE,
    ROW_EXPLANATION_DIRECTIVE,
    VARIANCE_EXPLANATION_DIRECTIVE,
    XAI_EXPLANATIONS_DIRECTIVE,
)

__all__ = ["SynthesisPromptRegistry"]


class SynthesisPromptRegistry:
    """Declarative registry mapping SDUI target blocks and preset views to prompt directives."""

    TARGET_BLOCK_DIRECTIVES: Final[dict[TargetBlockType, str]] = {
        TargetBlockType.EXECUTIVE_SUMMARY_BLOCK: EXECUTIVE_SUMMARY_DIRECTIVE,
        TargetBlockType.SYNTHESIS_TEXT_BLOCK: MATRIX_TEXT_SYNTHESIS_DIRECTIVE,
        TargetBlockType.VARIANCE_VALIDATION_BLOCK: VARIANCE_EXPLANATION_DIRECTIVE,
        TargetBlockType.AUTHENTICITY_EVALUATION_BLOCK: VARIANCE_EXPLANATION_DIRECTIVE,
        TargetBlockType.GROUPED_EXTENSIONS_BLOCK: XAI_EXPLANATIONS_DIRECTIVE,
    }

    PRESET_VIEW_DIRECTIVES: Final[dict[str, str]] = {
        PresetView.METRICS_1D.value: MATRIX_1D_SYNTHESIS_DIRECTIVE,
        "1d_metrics": MATRIX_1D_SYNTHESIS_DIRECTIVE,
        "metrics1d": MATRIX_1D_SYNTHESIS_DIRECTIVE,
        PresetView.COMPARE_2D.value: MATRIX_2D_SYNTHESIS_DIRECTIVE,
        "2d_compare": MATRIX_2D_SYNTHESIS_DIRECTIVE,
        "compare2d": MATRIX_2D_SYNTHESIS_DIRECTIVE,
        PresetView.MATRIX_3D.value: MATRIX_3D_SYNTHESIS_DIRECTIVE,
        "3d_matrix": MATRIX_3D_SYNTHESIS_DIRECTIVE,
        "matrix3d": MATRIX_3D_SYNTHESIS_DIRECTIVE,
        PresetView.TEXT_ONLY.value: MATRIX_TEXT_SYNTHESIS_DIRECTIVE,
        "text_only": MATRIX_TEXT_SYNTHESIS_DIRECTIVE,
        "textonly": MATRIX_TEXT_SYNTHESIS_DIRECTIVE,
    }

    DEFAULT_VIEW_DIRECTIVE: Final[str] = MATRIX_2D_SYNTHESIS_DIRECTIVE

    @classmethod
    def get_section_directive(
        cls,
        view_type_or_block: PresetView | TargetBlockType | str | None = None,
    ) -> str:
        """Resolve a static prompt directive for a given preset view, block type, or string key.

        Args:
            view_type_or_block: The PresetView, TargetBlockType, or string view identifier.

        Returns:
            The corresponding static synthesis directive string.
        """
        if view_type_or_block is None:
            return cls.DEFAULT_VIEW_DIRECTIVE

        # Check TargetBlockType enum mapping
        if isinstance(view_type_or_block, TargetBlockType):
            if view_type_or_block in cls.TARGET_BLOCK_DIRECTIVES:
                return cls.TARGET_BLOCK_DIRECTIVES[view_type_or_block]
            return cls.DEFAULT_VIEW_DIRECTIVE

        # Check PresetView enum mapping
        if isinstance(view_type_or_block, PresetView):
            if view_type_or_block.value in cls.PRESET_VIEW_DIRECTIVES:
                return cls.PRESET_VIEW_DIRECTIVES[view_type_or_block.value]
            return cls.DEFAULT_VIEW_DIRECTIVE

        # String-based lookup: check target block matches first
        key_str = str(view_type_or_block).strip()
        for block_type, directive in cls.TARGET_BLOCK_DIRECTIVES.items():
            if key_str == block_type.value or key_str.lower() == block_type.value.lower():
                return directive

        # String-based lookup: check preset view matches
        normalized_view = key_str.lower()
        if normalized_view in cls.PRESET_VIEW_DIRECTIVES:
            return cls.PRESET_VIEW_DIRECTIVES[normalized_view]

        return cls.DEFAULT_VIEW_DIRECTIVE

    @classmethod
    def get_row_explanation_directive(cls) -> str:
        """Return the canonical row explanation prompt directive.

        Returns:
            The static ROW_EXPLANATION_DIRECTIVE string.
        """
        return ROW_EXPLANATION_DIRECTIVE

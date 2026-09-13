"""Executive Summary SDUI Adapter.

Transforms user role classifications from evaluated target matrix into polymorphic AnySduiBlock components
for Server-Driven UI rendering. Zero Fallback Architecture: if user_role_target_block is unset or not found,
role badge is omitted without legacy fallbacks.
"""

import logging

from backend_v2.models.enums import TargetBlockType
from backend_v2.models.view.sdui import AnySduiBlock, ParagraphBlock
from backend_v2.services.localization import LocalizationService
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext

__all__ = ["ExecutiveSummaryAdapter"]

logger = logging.getLogger(__name__)


class ExecutiveSummaryAdapter:
    """Transforms executive summary role logic and syntheses into SDUI visual blocks.

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

        # 1. READ: Extract only the data this adapter needs from the context
        profile_cache = context.profile_cache
        profile = context.profile
        locale = context.locale

        if context.is_data_starved:
            return blocks

        if not profile_cache and not profile.user_role_target_block:
            return blocks

        # 2. TRANSFORM: Strict deterministic lookup of user role badge from evaluated target matrix
        role_val: str | None = None

        if profile.user_role_target_block:
            target_matrix = next(
                (axis for axis in context.parsed_matrices.values() if axis.block_id == profile.user_role_target_block),
                None,
            )
            if target_matrix is not None and target_matrix.score is not None and target_matrix.level_names:
                min_scale = int(target_matrix.scale_min) if target_matrix.scale_min is not None else 1
                max_scale = int(target_matrix.scale_max) if target_matrix.scale_max is not None else 5
                int_score = max(min_scale, min(max_scale, int(round(target_matrix.score))))

                int_key = str(int_score)
                float_key = str(float(int_score))
                if int_key in target_matrix.level_names:
                    role_val = target_matrix.level_names[int_key]
                elif float_key in target_matrix.level_names:
                    role_val = target_matrix.level_names[float_key]

        # 3. ASSEMBLE: Construct role badge block if role was deterministically resolved
        if role_val:
            if profile.user_role_label:
                prefix = profile.user_role_label.resolve(locale)
            else:
                prefix = LocalizationService.translate("user_role_label", locale)

            blocks.append(
                ParagraphBlock(
                    text=f"**{prefix}:** {role_val}",
                    exact_quotes=[],
                    citations=[],
                )
            )

        # 4. DYNAMIC SYNTHESES: Append executive summary section syntheses if present
        if profile_cache and profile_cache.section_syntheses:
            target_key = TargetBlockType.EXECUTIVE_SUMMARY_BLOCK.value
            if target_key in profile_cache.section_syntheses:
                for sb in profile_cache.section_syntheses[target_key]:
                    blocks.append(sb.model_copy(deep=True))

        return blocks

"""Executive Summary SDUI Adapter.

Transforms user role classifications into polymorphic AnySduiBlock components
for Server-Driven UI rendering. Visual rules are co-located as a module-level
AESTHETICS_RULES dictionary to enforce separation of presentation from logic.
"""

import logging

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.enums import RoleClassification, TargetBlockType
from backend_v2.models.view.sdui import AnySduiBlock, ParagraphBlock
from backend_v2.services.localization import LocalizationService
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext

__all__ = ["EXECUTIVE_SUMMARY_RULES", "ExecutiveSummaryAdapter"]

logger = logging.getLogger(__name__)


# ============================================================================
# SECTION 1: AESTHETICS RULES
# ============================================================================
# All visual decisions (severity, icon, label) are defined here as a flat
# dictionary. The adapter class below MUST NOT contain any if/elif/else
# chains for visual property selection.
#
# To add a new visual variant:  Add a key to this dictionary.
# To change a color or icon:   Edit the value in this dictionary.
# To understand the logic:     Read SECTION 2 below.
# ============================================================================

EXECUTIVE_SUMMARY_RULES: dict[RoleClassification, str] = {
    RoleClassification.PASSENGER: "rolePassenger",
    RoleClassification.NAVIGATOR: "roleNavigator",
    RoleClassification.DRIVER: "roleDriver",
    RoleClassification.ARCHITECT: "roleArchitect",
}


# ============================================================================
# SECTION 2: ADAPTER CLASS
# ============================================================================
# This class is a stateless transformer. It reads data from AdapterContext,
# looks up visual properties from SECTION 1, and assembles SDUI blocks.
# It MUST NOT:
#   - Import or access any repository or database
#   - Contain if/elif/else chains for visual property selection
#   - Mutate the context object
#   - Use .get() for AESTHETICS_RULES lookups
# ============================================================================


class ExecutiveSummaryAdapter:
    """Transforms executive summary role logic into SDUI visual blocks.

    Uses co-located EXECUTIVE_SUMMARY_RULES for all aesthetic decisions.
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
            KeyError: If an unmapped key is encountered in EXECUTIVE_SUMMARY_RULES.
                This is intentional Fail-Fast behavior indicating incomplete
                rules configuration.
            ValueError: If an invalid role classification is encountered.
            AppException: If domain validation fails.
        """
        blocks: list[AnySduiBlock] = []

        # 1. READ: Extract only the data this adapter needs from the context
        profile_cache = context.profile_cache
        profile = context.profile
        locale = context.locale

        if context.is_data_starved or not profile_cache:
            return blocks

        # 2. TRANSFORM: Strict validation and lookup of user role badge if present
        if profile_cache.user_role:
            try:
                parsed_role = RoleClassification(profile_cache.user_role)
            except ValueError as e:
                msg = f"Invalid user_role '{profile_cache.user_role}'"
                logger.error("[ExecutiveSummaryAdapter] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from e

            # Fail-Fast: strict key access, NO .get() fallback
            try:
                _ = EXECUTIVE_SUMMARY_RULES[parsed_role]
            except KeyError as e:
                msg = f"Missing role mapping for {parsed_role}"
                logger.error(
                    "[ExecutiveSummaryAdapter] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, exc_info=True
                )
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                ) from e

            # 3. ASSEMBLE: Resolve translation and construct role badge block
            role_key = parsed_role.value.lower()
            role_val = LocalizationService.translate(role_key, locale)

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
        if profile_cache.section_syntheses:
            target_key = TargetBlockType.EXECUTIVE_SUMMARY_BLOCK.value
            if target_key in profile_cache.section_syntheses:
                for sb in profile_cache.section_syntheses[target_key]:
                    blocks.append(sb.model_copy(deep=True))

        return blocks

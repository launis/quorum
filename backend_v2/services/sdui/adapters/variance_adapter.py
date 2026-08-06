"""Variance Validation SDUI Adapter.

Transforms variance data into polymorphic AnySduiBlock components
for Server-Driven UI rendering. Visual rules are co-located as a module-level
AESTHETICS_RULES dictionary to enforce separation of presentation from logic.
"""

import logging

from pydantic import ValidationError

import backend_v2.utils.scoring.variance_engine as variance_engine
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.linguistics import LinguisticsResultDTO
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
from backend_v2.models.enums import VisualIntent, XaiExtensionType
from backend_v2.models.v2_core import MatrixScorecardRowDTO
from backend_v2.models.view.sdui import (
    AlertBlock,
    AnySduiBlock,
    MarkdownBlock,
    ParagraphBlock,
    SduiGridBlock,
    SduiMetrics1DBlock,
)
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext

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

VARIANCE_RULES: dict[str, dict[str, VisualIntent]] = {
    "aligned": {
        "severity": VisualIntent.INFO,
    },
    "misaligned": {
        "severity": VisualIntent.WARNING,
    },
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


class VarianceAdapter:
    """Transforms Variance Validation into SDUI visual blocks.

    Uses co-located VARIANCE_RULES for all aesthetic decisions.
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
            KeyError: If an unmapped key is encountered in VARIANCE_RULES.
                This is intentional Fail-Fast behavior indicating incomplete
                rules configuration.
            AppException: If domain validation fails.
        """
        blocks: list[AnySduiBlock] = []

        # 1. READ: Extract only the data this adapter needs from the context
        if (
            not context.profile.visible_workflow_extensions
            or XaiExtensionType.VARIANCE_VALIDATION not in context.profile.visible_workflow_extensions
        ):
            return blocks

        if context.execution is None:
            msg = "Strict Fail-Fast: context.execution cannot be None for variance calculation."
            logger.error(
                "[VarianceAdapter] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        cv = context.execution.context_variables
        if cv is None:
            msg = "Fail-Fast: context_variables cannot be None in ExecutionRecord."
            logger.error(
                "[VarianceAdapter] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        authenticity_score: float | None = None
        performative_phrases_count: int | None = None

        step_det = cv.get("step_detector")
        if step_det is not None:
            try:
                det_out = LightweightMatrixOutput.model_validate(step_det, strict=False)
                if det_out.raw_score is not None:
                    authenticity_score = float(det_out.raw_score)
            except ValidationError as ve:
                logger.warning("[VarianceAdapter] Non-fatal schema mismatch in step_detector payload: %s", ve)

        if authenticity_score is None:
            perf_step_id = context.profile.performativity_detector_step_id
            if perf_step_id:
                from backend_v2.models.dtos.trace import TraceEventMetadataEnvelope, TraceMatrixPayloadDTO

                for event in reversed(context.execution.execution_trace):
                    try:
                        env = TraceEventMetadataEnvelope.model_validate(event.content, strict=False)
                        if event.step_name == perf_step_id or (
                            env.step_metadata and env.step_metadata.task_blueprint == perf_step_id
                        ):
                            for key, val in event.content.items():
                                if key == "_step_metadata":
                                    continue
                                try:
                                    payload = TraceMatrixPayloadDTO.model_validate(val, strict=False)
                                    if payload.raw_score is not None:
                                        authenticity_score = float(payload.raw_score)
                                        break
                                except ValidationError:
                                    pass
                            if authenticity_score is not None:
                                break
                    except ValidationError as ve:
                        logger.warning("[VarianceAdapter] Non-fatal schema mismatch in execution trace payload: %s", ve)

        step_ling = cv.get("step_linguistics")
        if step_ling is not None:
            try:
                ling_out = LinguisticsResultDTO.model_validate(step_ling, strict=False)
                patterns = ling_out.performative_patterns
                if isinstance(patterns, list):
                    performative_phrases_count = len(patterns)
            except ValidationError as ve:
                logger.warning("[VarianceAdapter] Non-fatal schema mismatch in step_linguistics payload: %s", ve)

        if performative_phrases_count is None:
            for event in reversed(context.execution.execution_trace):
                if event.event_type == "decision" and "step_linguistics" in event.content:
                    try:
                        ling_out = LinguisticsResultDTO.model_validate(event.content["step_linguistics"], strict=False)
                        if isinstance(ling_out.performative_patterns, list):
                            performative_phrases_count = len(ling_out.performative_patterns)
                            break
                    except ValidationError as ve:
                        logger.warning(
                            "[VarianceAdapter] Non-fatal schema mismatch in execution trace step_linguistics payload: %s",
                            ve,
                        )

        if authenticity_score is None or performative_phrases_count is None:
            msg = (
                "Strict Fail-Fast Enforced: 'variance_validation' requested but authenticity_score "
                f"({authenticity_score}) or performative_phrases_count ({performative_phrases_count}) is missing."
            )
            logger.error("[VarianceAdapter] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        variance_res = variance_engine.calculate_mechanical_cognitive_variance(
            llm_authenticity_score=authenticity_score,
            performative_phrases_count=performative_phrases_count,
        )

        def get_metric_label(key: str) -> str:
            lbl = context.profile.metric_mappings.get(key)
            if not lbl:
                msg = f"Strict Fail-Fast: Missing metric_mappings translation for '{key}'."
                logger.error("[VarianceAdapter] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )
            return lbl.resolve(context.locale)

        lbl_mech = get_metric_label("variance_mechanical")
        lbl_cog = get_metric_label("variance_cognitive")
        lbl_var = get_metric_label("variance_total")
        lbl_align = get_metric_label("alignment_verdict")

        auth_score_rounded = float(f"{float(authenticity_score):.2f}")
        var_score_rounded = float(f"{float(variance_res['variance_score']):.2f}")
        is_aligned = str(variance_res["alignment_verdict"]) == "ALIGNED"

        lvl_key = "aligned" if is_aligned else "misaligned"
        align_val = get_metric_label(f"alignment_{lvl_key}")

        # 2. TRANSFORM: Iterate, look up visual rules, assemble blocks
        try:
            aesthetics = VARIANCE_RULES[lvl_key]
        except KeyError as e:
            msg = f"Missing rule mapping for type_key: {lvl_key}"
            logger.error("[VarianceAdapter] CONFIGURATION_ERROR: %s", msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": "CONFIGURATION_ERROR"},
            ) from e

        alert_severity = aesthetics["severity"]

        grid_block = SduiGridBlock(
            items=[
                ParagraphBlock(text=f"{lbl_mech}: {performative_phrases_count}", exact_quotes=[], citations=[]),
                ParagraphBlock(text=f"{lbl_cog}: {auth_score_rounded}", exact_quotes=[], citations=[]),
                ParagraphBlock(text=f"{lbl_var}: {var_score_rounded}", exact_quotes=[], citations=[]),
            ]
        )
        alert_block = AlertBlock(
            severity=alert_severity,
            text=f"{lbl_align}: {align_val}",
            exact_quotes=[],
            citations=[],
        )

        llm_explanation = ""
        if context.profile_cache and hasattr(context.profile_cache, "row_explanations"):
            llm_explanation = context.profile_cache.row_explanations.get("variance_validation", "")

        if not llm_explanation:
            fallback_template = get_metric_label("variance_fallback_explanation")
            llm_explanation = fallback_template.format(performative_phrases_count, auth_score_rounded)

        variance_label = context.profile.extension_labels.get(XaiExtensionType.VARIANCE_VALIDATION)
        if not variance_label:
            msg = f"Strict Fail-Fast: Missing extension_labels mapping for {XaiExtensionType.VARIANCE_VALIDATION.value} in OutputProfile."
            logger.error("[VarianceAdapter] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        title_str = variance_label.resolve(context.locale)
        variance_text = (
            f"**{title_str}:** {auth_score_rounded}/100  \n**{lbl_align}:** {align_val}\n\n{llm_explanation}"
        )

        variance_kwargs = {
            "block_id": "variance_metrics_row",
            "name": "Variance Metrics",
            "label_i18n": variance_label,
            "row_explanation": "Variance metrics dashboard",
            "is_evaluative": False,
            "inner_sdui_blocks": [grid_block, alert_block],
        }
        row_dto = MatrixScorecardRowDTO.model_validate(variance_kwargs, strict=False)

        blocks.append(ParagraphBlock(text=f"**{title_str}**", exact_quotes=[], citations=[]))
        blocks.append(SduiMetrics1DBlock(axes=[row_dto]))
        blocks.append(MarkdownBlock(text=variance_text))

        return blocks

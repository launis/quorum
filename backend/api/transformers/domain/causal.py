import logging
from typing import Any

from backend.exceptions import AppException
from backend.models.domain import CausalOutput
from backend.models.enums import TitleKey
from backend.models.state import WorkflowState

# UVM: Use strict extensions
from backend.models.view.semantic_models import BlockType, CausalDisplay, SemanticBlock

# Deprecated: from backend.models.view.semantic_models_extensions import CausalDisplay as LegacyCausalDisplay
from ..base import BaseTransformer

logger = logging.getLogger(__name__)


class CausalDomainTransformer(BaseTransformer):
    def _adapt_legacy_trace(self, data: dict[str, Any]) -> dict[str, Any]:
        """Helper to adapt legacy reasoning_trace string to strict ReasoningTraceDTO."""
        if "reasoning_trace" in data and "thought_process" not in data:
            data = data.copy()
            data["thought_process"] = data.pop("reasoning_trace")
            data["conclusion"] = "Implicit in Analysis"
            data["confidence_score"] = 1.0
        return data

    def _extract_causal_section(self, state: WorkflowState) -> SemanticBlock | None:
        model = state.step_causal

        # Fallback to Panel
        if not model:
            panel = state.step_panel
            if panel and getattr(panel, "causal_analysis", None):
                model = CausalOutput(
                    causal_analysis=panel.causal_analysis,
                    thought_process=panel.thought_process,
                    conclusion=panel.conclusion,
                    confidence_score=panel.confidence_score,
                )

        if not model:
            return None

        try:
            display_model = self._transform_causal_data(model)
            return SemanticBlock(id="causal-analysis",
                type=BlockType.CARD,
                label=self._get_title(TitleKey.CAUSAL),
                value=display_model,  # Return model directly
            )
        except Exception as e:
            from fastapi import status
            from backend.exceptions import AppException, ErrorCodes
            import logging
            logger = logging.getLogger(__name__)

            logger.error(f"[CausalDomainTransformer] {ErrorCodes.REPORT_GENERATION_FAILED.name}: Error: {e}", exc_info=True)
            raise AppException(
                message=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.REPORT_GENERATION_FAILED.name},
            ) from e

    def _transform_causal_data(self, model: CausalOutput) -> CausalDisplay:
        """Flattens CausalOutput for SDUI (Strict UVM)."""
        data = model.causal_analysis

        # Abductive Reasoning
        abd_score = data.abductive_score

        # Calculate percent (1-3 scale)
        abd_pct: float | None = (abd_score / 3.0 * 100) if abd_score is not None else None

        # Counterfactual & Plausibility
        cf = data.counterfactual_test
        plaus_score = cf.plausibility_numeric
        plaus_pct: float | None = (plaus_score / 3.0) * 100 if plaus_score is not None else None

        return CausalDisplay(
            # Abductive
            abductive_score=abd_score,
            abductive_score_display=f"{abd_score:.1f}" if abd_score is not None else None,
            abductive_percent=abd_pct,
            abductive_percent_display=f"{abd_pct:.1f}" if abd_pct is not None else None,
            abductive_conclusion=self._t(data.abductive_conclusion.value, data.abductive_conclusion.name.title().replace("_", " ")),
            abductive_help=self._t("help.abductive", "Abduktiivinen päättely arvioi selityksen voimaa."),
            # Counterfactual / Plausibility
            plausibility_score=plaus_score,
            plausibility_score_display=f"{plaus_score:.1f}" if plaus_score is not None else None,
            plausibility_percent=plaus_pct,
            plausibility_percent_display=f"{plaus_pct:.1f}" if plaus_pct is not None else None,
            plausibility_label=self._t(cf.plausibility_score.value, cf.plausibility_score.name.title().replace("_", " ")),
            counterfactual_actual=cf.actual_scenario,
            counterfactual_simulated=cf.simulation_result,
            observation=data.observation,
            hypothesis=data.hypothesis,
            # Generic
            score=abd_score,  # Use abductive as main score?
            verdict=self._t(data.abductive_conclusion.value, data.abductive_conclusion.name.title().replace("_", " ")),
        )



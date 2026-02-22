import logging

from pydantic import ValidationError

from backend.models.domain import CausalAnalysis, CausalOutput
from backend.models.enums import TitleKey

# UVM: Use strict extensions
from backend.models.view import CausalDisplay, SectionType, UiSection

# Deprecated: from backend.models.view_extensions import CausalDisplay as LegacyCausalDisplay
from ..base import BaseTransformer

logger = logging.getLogger(__name__)


class CausalDomainTransformer(BaseTransformer):
    def _adapt_legacy_trace(self, data: dict) -> dict:
        """Helper to adapt legacy reasoning_trace string to strict ReasoningTraceDTO."""
        if "reasoning_trace" in data and "thought_process" not in data:
            data = data.copy()
            data["thought_process"] = data.pop("reasoning_trace")
            data["conclusion"] = "Implicit in Analysis"
            data["confidence_score"] = 1.0
        return data

    def _extract_causal_section(self, steps: dict) -> UiSection | None:
        step = steps.get("step_causal")

        # Fallback to Panel
        if not step:
            panel = steps.get("step_panel", {})
            step = panel.get("causal_analysis") or panel.get("kausaalinen_analyysi")

        if not step:
            return None

        # STRICT VALIDATION: CausalOutput
        try:
            # Handle wrapped vs flat
            if "causal_analysis" in step:
                model = CausalOutput(**self._adapt_legacy_trace(step))
            elif "abductive_score" in step or "abductive_conclusion" in step:
                # It's CausalAnalysis (inner), needs wrapping?
                # No, if it has 'thought_process', it might be Output
                if "thought_process" in step or "reasoning_trace" in step:
                    model = CausalOutput(**self._adapt_legacy_trace(step))
                else:
                    inner = CausalAnalysis(**step)
                    model = CausalOutput(
                        causal_analysis=inner,
                        thought_process="[Aggregated Panel Analysis]",
                        conclusion="N/A",
                        confidence_score=1.0,
                    )
            else:
                model = CausalOutput(**self._adapt_legacy_trace(step))

        except ValidationError as e:
            from backend.exceptions import AppException, ErrorCodes, status

            error_code = ErrorCodes.VALIDATION_FAILED
            logger.error(f"[ReportTransformer] {error_code.name}: Causal validation failed: {e}", exc_info=True)
            raise AppException(
                message=f"Causal validation failed: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": error_code.value, "original_error": str(e)},
            ) from e
        except Exception as e:
            from backend.exceptions import AppException, ErrorCodes, status

            error_code = ErrorCodes.REPORT_GENERATION_FAILED
            logger.error(f"[ReportTransformer] {error_code.name}: Causal transform failed: {e}", exc_info=True)
            raise AppException(
                message=f"Causal transform failed: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": error_code.value, "original_error": str(e)},
            ) from e

        try:
            display_model = self._transform_causal_data(model)
            return UiSection(
                id="causal-analysis",
                type=SectionType.CAUSAL_ANALYSIS,
                title=self._get_title(TitleKey.CAUSAL),
                data=display_model,  # Return model directly
            )
        except Exception as e:
            raise AppException(f"Failed to transform Causal display: {e}", 500) from e

    def _transform_causal_data(self, model: CausalOutput) -> CausalDisplay:
        """Flattens CausalOutput for SDUI (Strict UVM)."""
        data = model.causal_analysis

        # Abductive Reasoning
        abd_score = data.abductive_score

        # Calculate percent (1-3 scale)
        abd_percent = (abd_score / 3.0 * 100) if abd_score else 0.0

        # Counterfactual & Plausibility
        cf = data.counterfactual_test
        plaus_score = cf.plausibility_numeric
        plaus_percent = (plaus_score / 3.0 * 100) if plaus_score else 0.0

        return CausalDisplay(
            # Abductive
            abductive_score=abd_score,
            abductive_score_display=f"{abd_score:.1f}" if abd_score is not None else "N/A",
            abductive_percent=abd_percent,
            abductive_percent_display=f"{int(abd_percent)}%",
            abductive_conclusion=str(data.abductive_conclusion.value),
            abductive_help=self._t("help.abductive", "Abduktiivinen päättely arvioi selityksen voimaa."),
            # Counterfactual / Plausibility
            plausibility_score=plaus_score,
            plausibility_score_display=f"{plaus_score:.1f}" if plaus_score is not None else "N/A",
            plausibility_percent=plaus_percent,
            plausibility_percent_display=f"{int(plaus_percent)}%",
            plausibility_label=str(cf.plausibility_score.value),
            counterfactual_actual=cf.actual_scenario,
            counterfactual_simulated=cf.simulation_result,
            observation=data.observation,
            hypothesis=data.hypothesis,
            # Generic
            score=abd_score,  # Use abductive as main score?
            verdict=str(data.abductive_conclusion.value),
        )

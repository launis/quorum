
import logging

from pydantic import ValidationError

from backend.exceptions import AppException
from backend.models.domain import FalsifierData, FalsifierOutput
from backend.models.enums import TitleKey
from backend.models.view import SectionType, UiSection

# UVM: Use strict extensions
from backend.models.view import StressTestDisplay, StressFindingDisplay, FidelityAudit
from backend.models.view_extensions import StressDisplay as LegacyStressDisplay # Deprecated

from ..base import BaseTransformer

logger = logging.getLogger(__name__)

class FalsificationDomainTransformer(BaseTransformer):
    def _adapt_legacy_trace(self, data: dict) -> dict:
        """Helper to adapt legacy reasoning_trace string to strict ReasoningTraceDTO."""
        if "reasoning_trace" in data and "thought_process" not in data:
            data = data.copy()
            data["thought_process"] = data.pop("reasoning_trace")
            data["conclusion"] = "Implicit in Analysis"
            data["confidence_score"] = 1.0
        return data

    def _extract_falsifier_section(self, steps: dict) -> UiSection | None:
        step = steps.get("step_falsifier")

        # Fallback to Panel
        if not step:
            panel = steps.get("step_panel", {})
            step = panel.get("falsifier_data") or panel.get("falsifiointi_auditointi")

        if not step:
            return None

        # STRICT VALIDATION: FalsifierOutput
        try:
            if "falsifier_data" in step:
                 model = FalsifierOutput(**self._adapt_legacy_trace(step))
            else:
                # Wrap inner data
                if "falsifier_data" not in step and "stress_test_findings" in step:
                     # It's FalsifierData (inner)
                     inner = FalsifierData(**step)
                     model = FalsifierOutput(
                        falsifier_data=inner,
                        thought_process="[Aggregated Panel Analysis]",
                        conclusion="N/A",
                        confidence_score=1.0
                     )
                else:
                    # It's FalsifierOutput
                     model = FalsifierOutput(**self._adapt_legacy_trace(step))

        except ValidationError as e:
            from backend.exceptions import AppException, ErrorCodes, status
            error_code = ErrorCodes.VALIDATION_FAILED
            logger.error(f"[ReportTransformer] {error_code.name}: Falsifier validation failed: {e}", exc_info=True)
            raise AppException(
                message=f"Falsifier validation failed: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={
                    "error_code": error_code.value,
                    "original_error": str(e)
                }
            ) from e
        except Exception as e:
            from backend.exceptions import AppException, ErrorCodes, status
            error_code = ErrorCodes.REPORT_GENERATION_FAILED
            logger.error(f"[ReportTransformer] {error_code.name}: Falsifier transform failed: {e}", exc_info=True)
            raise AppException(
                message=f"Falsifier transform failed: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={
                    "error_code": error_code.value,
                    "original_error": str(e)
                }
            ) from e

        try:
            display_model = self._transform_falsifier_data(model)
            return UiSection(
                id="stress-test",
                type=SectionType.STRESS_TEST,
                title=self._get_title(TitleKey.FALSIFIER),
                data=display_model # Return model directly
            )
        except Exception as e:
             logger.warning(f"Failed to transform Stress display: {e}")
             return None

    def _transform_falsifier_data(self, model: FalsifierOutput) -> StressTestDisplay:
        """Flattens FalsifierOutput for SDUI (Strict UVM)."""
        data = model.falsifier_data

        # Findings
        findings = []
        for f in data.stress_test_findings:
            # Map domain findings to view findings
            findings.append(StressFindingDisplay(
                question=f.question,
                result_label="VER_HELD" if f.evidence_held else "VER_BROKEN",
                is_held=f.evidence_held,
                observation=f.observation,
                color_class="finding-held" if f.evidence_held else "finding-broken",
                text_class="text-held" if f.evidence_held else "text-broken"
            ))

        # Fidelity
        fid_audit = data.fidelity_audit
        fidelity_dict = None
        if fid_audit:
             # Use the View Model FidelityAudit to structure the dict
             fid_view = FidelityAudit(
                 fidelity_score_display=f"{fid_audit.fidelity_numeric:.1f}" if fid_audit.fidelity_numeric is not None else "N/A",
                 fidelity_percent=(
                     (fid_audit.fidelity_numeric / 3.0 * 100)
                     if fid_audit.fidelity_numeric else None
                 ),
                 fidelity_label=str(fid_audit.fidelity_score.value),
                 post_hoc_rationalization_suspected=fid_audit.post_hoc_rationalization,
                 reasoning=fid_audit.justification
             )
             fidelity_dict = fid_view.model_dump()

        return StressTestDisplay(
            fidelity_audit=fidelity_dict,
            fidelity_help=self._t("help.fidelity", "Uskottavuus arvioi päättelyn laatua."),
            findings=findings,
            
            # Explicitly set missing fields to None (as this transformer doesn't know about them)
            # They might be merged later or remain None
            abductive_score=None,
            abductive_percent=None,
            abductive_conclusion=None,
            abductive_help=None,
            
            counterfactual_actual=None,
            counterfactual_simulated=None,
            plausibility_score=None,
            plausibility_percent=None,
            plausibility_help=None
        )

import logging
from typing import Any

from backend.models.domain import FalsifierOutput
from backend.models.enums import TitleKey
from backend.models.state import WorkflowState

# UVM: Use strict extensions
from backend.models.view.semantic_models import (
    BlockType,
    FidelityAudit,
    SemanticBlock,
    StressFindingDisplay,
    StressTestDisplay,
)

from ..base import BaseTransformer

logger = logging.getLogger(__name__)


class FalsificationDomainTransformer(BaseTransformer):
    def _adapt_legacy_trace(self, data: dict[str, Any]) -> dict[str, Any]:
        """Helper to adapt legacy reasoning_trace string to strict ReasoningTraceDTO."""
        if "reasoning_trace" in data and "thought_process" not in data:
            data = data.copy()
            data["thought_process"] = data.pop("reasoning_trace")
            data["conclusion"] = "Implicit in Analysis"
            data["confidence_score"] = 1.0
        return data

    def _extract_falsifier_section(self, state: WorkflowState) -> SemanticBlock | None:
        model = state.step_falsifier

        # Fallback to Panel
        if not model:
            panel = state.step_panel
            if panel and getattr(panel, "falsifier_data", None):
                model = FalsifierOutput(
                    falsifier_data=panel.falsifier_data,
                    thought_process=panel.thought_process,
                    conclusion=panel.conclusion,
                    confidence_score=panel.confidence_score,
                )

        if not model:
            return None

        try:
            display_model = self._transform_falsifier_data(model)
            return SemanticBlock(id="stress-test",
                type=BlockType.CARD,
                label=self._get_title(TitleKey.FALSIFIER),
                value=display_model,  # Return model directly
            )
        except Exception as e:
            from fastapi import status
            from backend.exceptions import AppException, ErrorCodes
            import logging
            logger = logging.getLogger(__name__)

            logger.error(f"[FalsificationDomainTransformer] {ErrorCodes.REPORT_GENERATION_FAILED.name}: Error: {e}", exc_info=True)
            raise AppException(
                message=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.REPORT_GENERATION_FAILED.name},
            ) from e

    def _transform_falsifier_data(self, model: FalsifierOutput) -> StressTestDisplay:
        """Flattens FalsifierOutput for SDUI (Strict UVM)."""
        data = model.falsifier_data

        # Findings
        findings = []
        for f in data.stress_test_findings:
            # Map domain findings to view findings
            findings.append(
                StressFindingDisplay(
                    question=f.question,
                    result_label="VER_HELD" if f.evidence_held else "VER_BROKEN",
                    is_held=f.evidence_held,
                    observation=f.observation,
                    color_class="finding-held" if f.evidence_held else "finding-broken",
                    text_class="text-held" if f.evidence_held else "text-broken",
                )
            )

        # Fidelity
        fid_audit = data.fidelity_audit
        fidelity_dict = None
        if fid_audit:
            # Format percentage as string beforehand to comply with No-Math logic
            fid_pct = (fid_audit.fidelity_numeric / 3.0 * 100) if fid_audit.fidelity_numeric else None
            fid_pct_display = f"{fid_pct:.1f}" if fid_pct is not None else None

            # Use the View Model FidelityAudit to structure the dict
            fid_view = FidelityAudit(
                fidelity_score_display=f"{fid_audit.fidelity_numeric:.1f}"
                if fid_audit.fidelity_numeric is not None
                else None,
                fidelity_percent=fid_pct,
                fidelity_percent_display=fid_pct_display,
                fidelity_label=str(fid_audit.fidelity_score.value),
                post_hoc_rationalization_suspected=fid_audit.post_hoc_rationalization,
                reasoning=fid_audit.justification,
            )
            fidelity_dict = fid_view

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
            plausibility_help=None,
        )



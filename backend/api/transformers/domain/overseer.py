
import logging

from backend.exceptions import AppException
from backend.models.domain import OverseerData, OverseerOutput
from backend.models.enums import HelpTextKey, TitleKey
# UVM Refactor: Use strict extensions
from backend.models.view import FactCheckDisplay, VerifiedFactDisplay, EthicalIssueDisplay, SectionType, UiSection
# Deprecated: from backend.models.view_extensions import FactCheckDisplay, VerifiedFact, EthicalIssue

from ..base import BaseTransformer

logger = logging.getLogger(__name__)

class OverseerDomainTransformer(BaseTransformer):
    def _extract_overseer_section(self, steps: dict) -> UiSection | None:
        step = steps.get("step_overseer")

        # Fallback to Panel
        if not step:
            panel = steps.get("step_panel", {})
            step = panel.get("overseer_data") or panel.get("valvonta_data")

        if not step:
            return None

            # STRICT VALIDATION: Schema First
        try:
            if "overseer_data" in step:
                # Adapt legacy reasoning_trace
                if "reasoning_trace" in step and "thought_process" not in step:
                    step = step.copy()
                    step["thought_process"] = step.pop("reasoning_trace")
                    step["conclusion"] = "Implicit in Analysis"
                    step["confidence_score"] = 1.0

                model = OverseerOutput(**step)
            else:
                inner = OverseerData(**step)
                model = OverseerOutput(
                    overseer_data=inner,
                    thought_process="[Aggregated Panel Analysis]",
                    conclusion="N/A",
                    confidence_score=1.0
                )
        except Exception as e:
            error_code = "OVERSEER_VALIDATION_FAILED"
            logger.error(f"{error_code}: {e}", exc_info=True)
            raise AppException(
                message=str(e),
                status_code=500,
                details={"error_code": error_code}
            ) from e

        try:
            # UVM: Return strict model directly
            # Note: We return UiSection with data=FactCheckDisplay
            display_model = self._transform_overseer_data(model)
            
            return UiSection(
                id="fact-check-grid",
                type=SectionType.FACT_CHECK,
                title=self._get_title(TitleKey.OVERSEER),
                data=display_model
            )
        except Exception as e:
             raise AppException(f"Failed to transform Overseer display: {e}", 500) from e

    def _transform_overseer_data(self, model: OverseerOutput) -> FactCheckDisplay:
        """Flattens OverseerOutput for SDUI (Strict UVM)."""
        data = model.overseer_data

        # Facts
        facts = []
        for check in data.fact_checks:
            # Domain: FactCheckRFI
            verdict = check.verification_result # "Verified", "Debunked", "Unverified"
            
            # Logic: Color & Logic
            color = "orange"
            if verdict == "Verified":
                color = "green"
            elif verdict == "Debunked":
                color = "red"
            
            facts.append(VerifiedFactDisplay(
                label=verdict.upper(),
                label_key=f"VERIFICATION_{verdict.upper()}",
                claim=check.claim,
                source=check.source_or_reasoning or "Unknown",
                color=color,
                verification_result=verdict,
                is_verified=check.is_verified
            ))

        # Ethical Issues
        ethical_issues = [] 
        for issue in data.ethical_issues:
            # Domain: EthicalObservation
            severity = issue.severity # "None", "Warning", "Critical"
            
            # Logic: Color
            color = "green"
            if severity == "Critical":
                color = "red"
            elif severity == "Warning":
                color = "orange"

            ethical_issues.append(EthicalIssueDisplay(
                issue_type=issue.issue_type,
                description=issue.description,
                color=color,
                label_key=f"ETHICS_{severity.upper()}",
                label=severity.upper(),
                is_critical=issue.is_critical,
                severity=severity
            ))

        return FactCheckDisplay(
            verified_facts=facts,
            ethical_issues=ethical_issues
        )

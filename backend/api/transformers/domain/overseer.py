
import logging

from pydantic import ValidationError

from backend.exceptions import AppException
from backend.models.domain import OverseerData, OverseerOutput
from backend.models.enums import HelpTextKey, TitleKey
# UVM Refactor: Use strict extensions
from backend.models.view import FactCheckDisplay, VerifiedFactDisplay, EthicalIssueDisplay, SectionType, UiSection
# Deprecated: from backend.models.view_extensions import FactCheckDisplay, VerifiedFact, EthicalIssue

from ..base import BaseTransformer

logger = logging.getLogger(__name__)

class OverseerDomainTransformer(BaseTransformer):
    def _adapt_legacy_trace(self, data: dict) -> dict:
        """Helper to adapt legacy reasoning_trace string to strict ReasoningTraceDTO."""
        if "reasoning_trace" in data and "thought_process" not in data:
            data = data.copy()
            data["thought_process"] = data.pop("reasoning_trace")
            data["conclusion"] = "Implicit in Analysis"
            data["confidence_score"] = 1.0
        return data

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
                 model = OverseerOutput(**self._adapt_legacy_trace(step))
            # Check if it's the inner data (list of facts) - heuristic
            elif "fact_checks" in step and "overseer_data" not in step:
                inner = OverseerData(**step)
                model = OverseerOutput(
                    overseer_data=inner,
                    thought_process="[Aggregated Panel Analysis]",
                    conclusion="N/A",
                    confidence_score=1.0
                )
            else:
                 model = OverseerOutput(**self._adapt_legacy_trace(step))
                 
        except ValidationError as e:
            error_code = "OVERSEER_VALIDATION_FAILED"
            logger.error(f"{error_code}: {e}", exc_info=True)
            raise AppException(
                message=f"Overseer validation failed: {e}",
                status_code=500,
                details={"error_code": error_code, "errors": e.errors()}
            ) from e
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
                source=check.source_or_reasoning,
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

import logging

from pydantic import ValidationError

from backend.models.domain import OverseerData, OverseerOutput
from backend.models.enums import TitleKey

# UVM Refactor: Use strict extensions
from backend.models.view import EthicalIssueDisplay, FactCheckDisplay, SectionType, UiSection, VerifiedFactDisplay

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

    def _extract_overseer_section(self, state: 'WorkflowState') -> UiSection | None:
        model = state.step_overseer

        # Fallback to Panel
        if not model:
            panel = state.step_panel
            if panel and getattr(panel, "overseer_data", None):
                model = OverseerOutput(
                    overseer_data=panel.overseer_data,
                    thought_process="[Aggregated Panel Analysis]",
                    conclusion="N/A",
                    confidence_score=1.0,
                )

        if not model:
            return None

        try:
            # UVM: Return strict model directly
            # Note: We return UiSection with data=FactCheckDisplay
            display_model = self._transform_overseer_data(model)

            return UiSection(
                id="fact-check-grid",
                type=SectionType.FACT_CHECK,
                title=self._get_title(TitleKey.OVERSEER),
                data=display_model,
            )
        except Exception as e:
            from backend.exceptions import AppException
            raise AppException(f"Failed to transform Overseer display: {e}", 500) from e

    def _transform_overseer_data(self, model: OverseerOutput) -> FactCheckDisplay:
        """Flattens OverseerOutput for SDUI (Strict UVM)."""
        data = model.overseer_data

        # Facts
        facts = []
        for check in data.fact_checks:
            # Domain: FactCheckRFI
            verdict = check.verification_result  # "Verified", "Debunked", "Unverified"

            # Logic: Color & Logic
            color = "orange"
            if verdict == "Verified":
                color = "green"
            elif verdict == "Debunked":
                color = "red"

            facts.append(
                VerifiedFactDisplay(
                    label=verdict.upper(),
                    label_key=f"VERIFICATION_{verdict.upper()}",
                    claim=check.claim,
                    source=check.source_or_reasoning,
                    color=color,
                    verification_result=verdict,
                    is_verified=check.is_verified,
                )
            )

        # Ethical Issues
        ethical_issues = []
        for issue in data.ethical_issues:
            # Domain: EthicalObservation
            severity = issue.severity  # "None", "Warning", "Critical"

            # Logic: Color
            color = "green"
            if severity == "Critical":
                color = "red"
            elif severity == "Warning":
                color = "orange"

            ethical_issues.append(
                EthicalIssueDisplay(
                    issue_type=issue.issue_type,
                    description=issue.description,
                    color=color,
                    label_key=f"ETHICS_{severity.upper()}",
                    label=severity.upper(),
                    is_critical=issue.is_critical,
                    severity=severity,
                )
            )

        return FactCheckDisplay(fact_checks=facts, ethical_issues=ethical_issues)

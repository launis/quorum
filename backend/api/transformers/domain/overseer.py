import logging
from typing import Any

from backend.models.domain import OverseerOutput
from backend.models.enums import TitleKey
from backend.models.state import WorkflowState

# UVM Refactor: Use strict extensions
from backend.models.view.semantic_models import (
    BlockType,
    EthicalIssueDisplay,
    FactCheckDisplay,
    SemanticBlock,
    VerifiedFactDisplay,
)

# Deprecated: from backend.models.view.semantic_models_extensions import FactCheckDisplay, VerifiedFact, EthicalIssue
from ..base import BaseTransformer

logger = logging.getLogger(__name__)


class OverseerDomainTransformer(BaseTransformer):
    def _adapt_legacy_trace(self, data: dict[str, Any]) -> dict[str, Any]:
        """Helper to adapt legacy reasoning_trace string to strict ReasoningTraceDTO."""
        if "reasoning_trace" in data and "thought_process" not in data:
            data = data.copy()
            data["thought_process"] = data.pop("reasoning_trace")
            data["conclusion"] = "Implicit in Analysis"
            data["confidence_score"] = 1.0
        return data

    def _extract_overseer_section(self, state: WorkflowState) -> SemanticBlock | None:
        model = state.step_overseer

        # Fallback to Panel
        if not model:
            panel = state.step_panel
            if panel and getattr(panel, "overseer_data", None):
                model = OverseerOutput(
                    overseer_data=panel.overseer_data,
                    thought_process=panel.thought_process,
                    conclusion=panel.conclusion,
                    confidence_score=panel.confidence_score,
                )

        if not model:
            return None

        try:
            # UVM: Return strict model directly
            # Note: We return SemanticBlock with data=FactCheckDisplay
            display_model = self._transform_overseer_data(model)

            return SemanticBlock(id="fact-check-grid",
                type=BlockType.CARD,
                label=self._get_title(TitleKey.OVERSEER),
                value=display_model,
            )
        except Exception as e:
            from fastapi import status
            from backend.exceptions import AppException, ErrorCodes
            import logging
            logger = logging.getLogger(__name__)

            logger.error(f"[OverseerDomainTransformer] {ErrorCodes.REPORT_GENERATION_FAILED.name}: Error: {e}", exc_info=True)
            raise AppException(
                message=str(e),
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.REPORT_GENERATION_FAILED.name},
            ) from e

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



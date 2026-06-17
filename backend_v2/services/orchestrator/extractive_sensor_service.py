from pydantic import BaseModel, ConfigDict

from backend_v2.models.v2_core import TDAAssertion
from backend_v2.services.orchestrator.anchor_validation_service import AnchorValidationService


class PreFlightResult(BaseModel):
    """Result of the deterministric pre-flight evaluation."""

    model_config = ConfigDict(frozen=True)

    decided: bool
    result: str | None = None
    exact_quotes: list[str] | None = None


class ExtractiveSensorService:
    """TDD-testable service for deterministic pre-flight extraction rules.

    Enforces the Zero-Reasoning Mandate for syntactic anchors.
    """

    @staticmethod
    def pre_evaluate(tda: TDAAssertion, source_text: str) -> PreFlightResult:
        """Evaluates TDA against source text without LLM if pre-flight is enabled.

        Acts as an EARLY EXIT:
        - If the required syntactic anchors are MISSING, we can definitively FAIL the extraction
          without invoking the LLM (decided=True, exact_quotes=None).
        - If the anchors ARE FOUND, we CANNOT pass or fail it definitively here because we must
          allow the LLM to evaluate complex Bounding Box and Negative Conditions (decided=False).
        """
        if not tda.enforce_pre_flight or not tda.syntactic_anchors:
            return PreFlightResult(decided=False)

        found = [a for a in tda.syntactic_anchors if AnchorValidationService.strict_match(source_text, [a])]

        # Early exit logic:
        # If we need AT LEAST ONE anchor (EXISTS) but found ZERO -> Definitive FAIL
        if tda.aggregation_mode == "EXISTS" and len(found) == 0:
            return PreFlightResult(
                decided=True,
                result="PASS" if tda.inverse_evidence else "FAIL",
                exact_quotes=None,
            )

        # If we need ALL anchors (ALL_MUST_COMPLY) but are MISSING ANY -> Definitive FAIL
        if tda.aggregation_mode == "ALL_MUST_COMPLY" and len(found) < len(tda.syntactic_anchors):
            return PreFlightResult(
                decided=True,
                result="PASS" if tda.inverse_evidence else "FAIL",
                exact_quotes=None,
            )

        # Anchors WERE found. We MUST delegate to LLM to evaluate contextual conditions.
        return PreFlightResult(decided=False)

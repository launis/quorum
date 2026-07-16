import logging
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field
from rapidfuzz import fuzz

from backend_v2.exceptions import AppException
from backend_v2.llm.client import LLMClient
from backend_v2.models.dtos.dag_models import LinkedAtomGraph
from backend_v2.models.dtos.quote_evidence import LLMExtractedQuote
from backend_v2.models.enums import ExecutionStatus, get_lexical_fuzz_threshold
from backend_v2.models.v2_core import TDAAssertion
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.anchor_validation_service import AnchorValidationService


class PreFlightResult(BaseModel):
    """Result of the deterministic pre-flight evaluation."""

    model_config = ConfigDict(frozen=True)

    decided: bool
    result: str | None = None
    exact_quotes: list[LLMExtractedQuote] | None = None


class ExtractiveSensorService:
    """TDD-testable service for deterministic pre-flight extraction rules.

    Enforces the Zero-Reasoning Mandate for syntactic anchors.
    """

    @staticmethod
    def _fuzzy_match(source_text: str, anchor: str, locale: str | None = None) -> bool:
        """Fuzzy match tolerating minor typos/OCR issues in the source text.

        Checks strict match first, then falls back to rapidfuzz partial ratio
        against the language-dependent threshold.

        Args:
            source_text: The complete raw text context.
            anchor: The syntactic anchor string to look for.
            locale: Optional target locale/language code.

        Returns:
            True if the anchor is matched strictly or fuzzily within the text,
            otherwise False.
        """
        if AnchorValidationService.strict_match(source_text, [anchor]):
            return True
        threshold = get_lexical_fuzz_threshold(locale)
        return fuzz.partial_ratio(anchor.lower(), source_text.lower()) >= threshold

    @staticmethod
    def pre_evaluate(tda: TDAAssertion, source_text: str, locale: str | None = None) -> PreFlightResult:
        """Evaluates TDA against source text without LLM if pre-flight is enabled.

        Acts as an EARLY EXIT:
        - If the required syntactic anchors are MISSING, we can definitively FAIL the extraction
          without invoking the LLM (decided=True, exact_quotes=None).
        - If the anchors ARE FOUND, we CANNOT pass or fail it definitively here because we must
          allow the LLM to evaluate complex Bounding Box and Negative Conditions (decided=False).

        Args:
            tda: The TDAAssertion definition containing anchors and constraints.
            source_text: The raw source text.
            locale: Optional language code for dynamic fuzzy thresholding.

        Returns:
            A PreFlightResult indicating if the decision was resolved early.
        """
        logger = logging.getLogger(__name__)

        if not tda.enforce_pre_flight or not tda.syntactic_anchors:
            return PreFlightResult(decided=False)

        found = [a for a in tda.syntactic_anchors if ExtractiveSensorService._fuzzy_match(source_text, a, locale)]
        logger.info(
            "[ExtractiveSensor] TDA %s | Anchors: %s | Found: %s | Aggregation: %s",
            tda.tda_id,
            tda.syntactic_anchors,
            found,
            tda.aggregation_mode,
        )

        # Early exit logic:
        # If we need AT LEAST ONE anchor (EXISTS) but found ZERO -> Definitive FAIL
        if tda.aggregation_mode == "EXISTS" and len(found) == 0:
            res = "PASS" if tda.inverse_evidence else "FAIL"
            logger.info(
                "[ExtractiveSensor] TDA %s early exit triggered: decided=True, result=%s (aggregation=EXISTS, found=0)",
                tda.tda_id,
                res,
            )
            return PreFlightResult(
                decided=True,
                result=res,
                exact_quotes=None,
            )

        # If we need ALL anchors (ALL_MUST_COMPLY) but are MISSING ANY -> Definitive FAIL
        if tda.aggregation_mode == "ALL_MUST_COMPLY" and len(found) < len(tda.syntactic_anchors):
            res = "PASS" if tda.inverse_evidence else "FAIL"
            logger.info(
                "[ExtractiveSensor] TDA %s early exit triggered: decided=True, result=%s (aggregation=ALL_MUST_COMPLY, missing anchors)",
                tda.tda_id,
                res,
            )
            return PreFlightResult(
                decided=True,
                result=res,
                exact_quotes=None,
            )

        # Anchors WERE found. We MUST delegate to LLM to evaluate contextual conditions.
        logger.info("[ExtractiveSensor] TDA %s | Anchors found, delegating to LLM for context evaluation", tda.tda_id)
        return PreFlightResult(decided=False)

    @staticmethod
    async def evaluate_atom_boolean(
        node: LinkedAtomGraph,
        executor: LLMTaskExecutor,
        client: LLMClient,
        context_text: str,
    ) -> tuple[ExecutionStatus, str | None, dict[str, str]]:
        """Evaluates an atom's claim against the source text using an LLM.

        Args:
            node: The LinkedAtomGraph node to evaluate.
            executor: The LLMTaskExecutor to run the query.
            client: The LLMClient instance.
            context_text: The source document text.

        Returns:
            ExecutionStatus.PASSED if the claim is verified, FAILED otherwise.
            ExecutionStatus.SYSTEM_ERROR if the evaluation crashes.
        """
        logger = logging.getLogger(__name__)

        class BooleanEvaluationResult(BaseModel):
            model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
            reasoning: Annotated[str, Field(description="Chain-of-thought: Evaluate if the text confirms the claim.")]
            is_true: Annotated[bool, Field(description="True if the text confirms the claim, False otherwise.")]
            coaching: Annotated[
                str | None, Field(description="Provide a coaching tip if the claim failed.", default=None)
            ] = None
            falsification: Annotated[
                str | None, Field(description="Provide a falsification argument if the claim failed.", default=None)
            ] = None
            remediation_steps: Annotated[
                list[str] | None, Field(description="Step-by-step remediation if the claim failed.", default=None)
            ] = None

        prompt = (
            "Evaluate if the following claim is true based strictly on the provided context.\n\n"
            f"<claim>\n{node.atom.resolved_claim}\n</claim>\n\n"
            f"<context>\n{context_text}\n</context>"
        )

        try:
            result, _ = await executor.execute_structured_task(
                client=client,
                messages=[{"role": "user", "content": prompt}],
                response_model=BooleanEvaluationResult,
            )

            extensions: dict[str, str] = {}
            if result.coaching:
                extensions["coaching"] = result.coaching
            if result.falsification:
                extensions["falsification"] = result.falsification
            if result.remediation_steps:
                extensions["remediation_steps"] = "\n".join(f"- {step}" for step in result.remediation_steps)

            status = ExecutionStatus.PASSED if result.is_true else ExecutionStatus.FAILED
            return status, result.reasoning, extensions
        except AppException as e:
            logger.error("Boolean evaluation failed for TDA %s: %s", node.atom.tda_id, str(e))
            return ExecutionStatus.SYSTEM_ERROR, f"EVALUATION_CRASH: {str(e)}", {}

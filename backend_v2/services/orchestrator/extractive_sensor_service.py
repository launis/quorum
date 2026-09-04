"""Extractive Sensor Service for TDD deterministic evaluation and Bo3 LLM voting."""

import asyncio
import logging
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator
from rapidfuzz import fuzz

from backend_v2.exceptions import AgentExecutionError
from backend_v2.llm.client import LLMClient
from backend_v2.llm.provider import _is_transient_llm_error
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.dag_models import (
    AtomEvaluationResultDTO,
    AtomExecutionState,
    ExtractedAtom,
    LinkedAtomGraph,
)
from backend_v2.models.dtos.engine import MatrixEvaluationContext
from backend_v2.models.dtos.quote_evidence import LLMExtractedQuote
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.v2_core import TDAAssertion
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.anchor_validation_service import AnchorValidationService
from backend_v2.services.orchestrator.prompts.matrix_sensor_prompt_builder import MatrixSensorPromptBuilder
from backend_v2.settings import get_lexical_fuzz_threshold, get_settings
from backend_v2.utils.alias_engine import AliasEngine


class PreFlightResult(BaseModel):
    """Result of the deterministic pre-flight evaluation."""

    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)

    decided: bool
    result: ExecutionStatus | None = None
    exact_quotes: list[LLMExtractedQuote] | None = None
    source_quote: str | None = None


class BooleanEvaluationResult(BaseModel):
    """Schema for a single boolean evaluation result from LLM."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
    alias: Annotated[str, Field(description="The alias assigned to the claim (e.g., 'a0', 'a1').")]
    reasoning: Annotated[str, Field(description="Chain-of-thought: Evaluate if the text confirms the claim.")]
    is_true: Annotated[bool, Field(description="True if the text confirms the claim, False otherwise.")]
    source_quote: Annotated[
        str | None,
        Field(
            default=None,
            max_length=500,
            description=(
                "Exact verbatim sentence or clause extracted directly from the context text in its original language, "
                "substantiating or violating this claim, or null if absent."
            ),
        ),
    ] = None
    contextual_override: Annotated[bool | None, Field(default=None, description="True if bypass was used.")] = None
    coaching: Annotated[str | None, Field(description="Provide a coaching tip if the claim failed.", default=None)] = (
        None
    )
    falsification: Annotated[
        str | None, Field(description="Provide a falsification argument if the claim failed.", default=None)
    ] = None
    remediation_steps: Annotated[
        list[str] | None, Field(description="Step-by-step remediation if the claim failed.", default=None)
    ] = None

    @field_validator("source_quote", mode="before")
    @classmethod
    def truncate_source_quote_at_sentence(cls, v: str | None) -> str | None:
        """Truncate oversized quote at the nearest sentence boundary under 500 chars."""
        if v is not None and len(v) > 500:
            truncated = v[:500]
            last_dot = truncated.rfind(".")
            return (truncated[: last_dot + 1]) if last_dot > 100 else truncated
        return v


class BatchEvaluationResponse(BaseModel):
    """Schema for the batch boolean evaluation result."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
    results: list[BooleanEvaluationResult]


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
    def pre_evaluate(
        tda: TDAAssertion | ExtractedAtom,
        source_text: str,
        locale: str | None = None,
        allow_contextual_override: bool = False,
    ) -> PreFlightResult:
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
            allow_contextual_override: Flag indicating whether contextual overrides are permitted during pre-flight.

        Returns:
            A PreFlightResult indicating if the decision was resolved early.
        """
        logger = logging.getLogger(__name__)

        if isinstance(tda, ExtractedAtom):
            quote = tda.source_quote
            if not quote or quote.lower() in ["none", "n/a", "null", ""]:
                return PreFlightResult(decided=False)

            if ExtractiveSensorService._fuzzy_match(source_text, quote, locale):
                return PreFlightResult(decided=False)

            return PreFlightResult(
                decided=True,
                result=ExecutionStatus.FAILED,
                exact_quotes=None,
            )

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
            if allow_contextual_override:
                logger.info(
                    "[ExtractiveSensor] TDA %s bypassed early exit due to allow_contextual_override=True", tda.tda_id
                )
                return PreFlightResult(decided=False)
            res = ExecutionStatus.PASSED if tda.inverse_evidence else ExecutionStatus.FAILED
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
            if allow_contextual_override:
                logger.info(
                    "[ExtractiveSensor] TDA %s bypassed early exit due to allow_contextual_override=True", tda.tda_id
                )
                return PreFlightResult(decided=False)
            res = ExecutionStatus.PASSED if tda.inverse_evidence else ExecutionStatus.FAILED
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
    def _batch_fuzzy_match(
        nodes: list[LinkedAtomGraph],
        source_text: str,
        locale: str | None = None,
        allow_contextual_override: bool = False,
    ) -> tuple[dict[str, AtomEvaluationResultDTO], list[LinkedAtomGraph]]:
        """Synchronous batch fuzzy matching to determine pre-flight status.

        Args:
            nodes: The list of LinkedAtomGraph nodes.
            source_text: The source document text.
            locale: Optional target locale.
            allow_contextual_override: Whether to permit contextual overrides in pre-evaluation.

        Returns:
            Tuple containing decided results and undecided nodes.
        """
        decided_results: dict[str, AtomEvaluationResultDTO] = {}
        undecided_nodes: list[LinkedAtomGraph] = []

        for node in nodes:
            pre_result = ExtractiveSensorService.pre_evaluate(
                node.atom, source_text, locale, allow_contextual_override=allow_contextual_override
            )
            if pre_result.decided:
                if pre_result.result == ExecutionStatus.PASSED:
                    decided_results[node.atom.tda_id] = AtomEvaluationResultDTO(
                        status=ExecutionStatus.PASSED,
                        reasoning="PRE_FLIGHT_DETERMINISTIC_PASS",
                        source_quote=pre_result.source_quote,
                        extensions={},
                    )
                else:
                    decided_results[node.atom.tda_id] = AtomEvaluationResultDTO(
                        status=ExecutionStatus.FAILED,
                        reasoning="PRE_FLIGHT_DETERMINISTIC_REJECT",
                        source_quote=None,
                        extensions={},
                    )
            else:
                undecided_nodes.append(node)

        return decided_results, undecided_nodes

    @staticmethod
    async def batch_pre_evaluate(
        nodes: list[LinkedAtomGraph],
        source_text: str,
        locale: str | None = None,
        allow_contextual_override: bool = False,
    ) -> tuple[dict[str, AtomEvaluationResultDTO], list[LinkedAtomGraph]]:
        """Asynchronous wrapper that offloads CPU-bound batch fuzzy matching to a thread.

        Args:
            nodes: The list of LinkedAtomGraph nodes.
            source_text: The source document text.
            locale: Optional target locale.
            allow_contextual_override: Whether to permit contextual overrides in pre-evaluation.

        Returns:
            Tuple containing decided results and undecided nodes.
        """
        return await asyncio.to_thread(
            ExtractiveSensorService._batch_fuzzy_match, nodes, source_text, locale, allow_contextual_override
        )

    @staticmethod
    def resolve_majority_vote(
        expected_tda_ids: list[str], results: list[dict[str, AtomEvaluationResultDTO] | None]
    ) -> dict[str, AtomEvaluationResultDTO]:
        """Resolves Best-of-Three ensemble voting.

        Args:
            expected_tda_ids: The full list of expected atom IDs for this batch.
            results: The list of response dictionaries from the ensemble calls. None if a call failed transiently.

        Returns:
            The consolidated dictionary mapping TDA IDs to their majority status.

        Raises:
            AgentExecutionError: If insufficient valid Bo3 results.
        """
        settings = get_settings()
        min_consensus = settings.ensemble_min_consensus

        valid_results = [r for r in results if r is not None]

        if len(valid_results) < min_consensus:
            # Transient API failure split (< 2 valid results total)
            raise AgentExecutionError(
                detail=f"Insufficient valid Bo3 results ({len(valid_results)} < {min_consensus}) due to transient API failures.",
                status_code=503,
            )

        final_results: dict[str, AtomEvaluationResultDTO] = {}

        for tda_id in expected_tda_ids:
            tally: dict[ExecutionStatus, int] = {}
            first_seen: dict[ExecutionStatus, AtomEvaluationResultDTO] = {}

            for res in valid_results:
                if tda_id in res:
                    vote = res[tda_id]
                    status = vote.status
                    if status not in tally:
                        tally[status] = 0
                    tally[status] += 1
                    if status not in first_seen:
                        first_seen[status] = vote

            elected = False
            for status, count in tally.items():
                if count >= min_consensus:
                    final_results[tda_id] = first_seen[status]
                    elected = True
                    break

            if not elected:
                # Semantic split or hallucinated drop
                final_results[tda_id] = AtomEvaluationResultDTO(
                    status=ExecutionStatus.SYSTEM_ERROR,
                    reasoning="INSUFFICIENT_CONSENSUS",
                    source_quote=None,
                    extensions={},
                )

        return final_results

    @staticmethod
    async def evaluate_atom_boolean_batch(
        nodes: list[LinkedAtomGraph],
        executor: LLMTaskExecutor,
        client: LLMClient,
        context_text: str,
        matrix_context: MatrixEvaluationContext | None = None,
        current_states: dict[str, AtomExecutionState] | None = None,
    ) -> tuple[dict[str, AtomEvaluationResultDTO], TokenUsage]:
        """Evaluates a batch of atom claims against the source text using an LLM.

        Args:
            nodes: The list of LinkedAtomGraph nodes to evaluate.
            executor: The LLMTaskExecutor to run the query.
            client: The LLMClient instance.
            context_text: The source document text.
            matrix_context: Optional evaluation context for matrix-level overrides.
            current_states: Optional dictionary of current atom execution states.

        Returns:
            A tuple of:
            - A dictionary mapping tda_id to its AtomEvaluationResultDTO.
            - Aggregated TokenUsage across all ensemble calls.

        Raises:
            AgentExecutionError: If insufficient valid Bo3 results or LLM failure.
        """
        logger = logging.getLogger(__name__)
        settings = get_settings()
        parallelism = settings.ensemble_parallelism

        logger.info("Evaluating atom batch with parallelism: %d", parallelism)

        alias_engine = AliasEngine()
        requested_aliases: set[str] = set()
        alias_to_tda_id: dict[str, str] = {}
        tda_id_to_alias: dict[str, str] = {}

        for node in nodes:
            tda_id = node.atom.tda_id
            alias = alias_engine.register(tda_id, prefix="a")
            requested_aliases.add(alias)
            alias_to_tda_id[alias] = tda_id
            tda_id_to_alias[tda_id] = alias

        atom_status_map: dict[str, ExecutionStatus] = {}
        if current_states:
            atom_status_map = {tda_id: state.status for tda_id, state in current_states.items()}

        compiled_prompt = MatrixSensorPromptBuilder.build_compiled_prompt(
            context_text=context_text,
            nodes=nodes,
            tda_id_to_alias=tda_id_to_alias,
            matrix_context=matrix_context,
            atom_status_map=atom_status_map,
        )

        semaphore = asyncio.Semaphore(parallelism)

        async def _single_ensemble_call() -> tuple[dict[str, AtomEvaluationResultDTO] | None, TokenUsage]:
            async with semaphore:
                try:
                    result, usage = await executor.execute_structured_task(
                        client=client,
                        messages=compiled_prompt,
                        response_model=BatchEvaluationResponse,
                    )

                    call_results: dict[str, AtomEvaluationResultDTO] = {}
                    returned_aliases: set[str] = set()

                    for eval_result in result.results:
                        alias = eval_result.alias
                        if alias not in requested_aliases:
                            continue

                        returned_aliases.add(alias)
                        call_tda_id = alias_engine.resolve_alias(alias)

                        extensions: dict[str, str] = {}
                        if eval_result.coaching:
                            extensions["coaching"] = eval_result.coaching
                        if eval_result.contextual_override is not None:
                            extensions["contextual_override"] = str(eval_result.contextual_override)
                        if eval_result.falsification:
                            extensions["falsification"] = eval_result.falsification
                        if eval_result.remediation_steps:
                            extensions["remediation_steps"] = "\n".join(
                                f"- {step}" for step in eval_result.remediation_steps
                            )

                        is_inverse = False
                        if matrix_context and matrix_context.matrix_assertions:
                            for a in matrix_context.matrix_assertions:
                                if a.atom_id == call_tda_id:
                                    is_inverse = a.is_inverse
                                    break

                        if is_inverse:
                            status = ExecutionStatus.FAILED if eval_result.is_true else ExecutionStatus.PASSED
                        else:
                            status = ExecutionStatus.PASSED if eval_result.is_true else ExecutionStatus.FAILED

                        call_results[call_tda_id] = AtomEvaluationResultDTO(
                            status=status,
                            reasoning=eval_result.reasoning,
                            source_quote=eval_result.source_quote,
                            extensions=extensions,
                        )

                    return call_results, usage
                except Exception as e:
                    if isinstance(e, AgentExecutionError) or _is_transient_llm_error(e):
                        logger.warning("Transient error in Bo3 ensemble call: %s", e)
                        return None, TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
                    raise

        task_outputs: list[tuple[dict[str, AtomEvaluationResultDTO] | None, TokenUsage]] = []
        try:
            async with asyncio.TaskGroup() as tg:
                tasks = [tg.create_task(_single_ensemble_call()) for _ in range(parallelism)]

            task_outputs = [t.result() for t in tasks]
        except ExceptionGroup as eg:
            raise eg.exceptions[0] from eg

        results: list[dict[str, AtomEvaluationResultDTO] | None] = []
        total_usage = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
        for res, usage in task_outputs:
            results.append(res)
            total_usage = total_usage + usage

        expected_tda_ids = [node.atom.tda_id for node in nodes]
        majority_results = ExtractiveSensorService.resolve_majority_vote(expected_tda_ids, results)
        return majority_results, total_usage

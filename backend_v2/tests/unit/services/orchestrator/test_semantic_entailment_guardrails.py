"""Unit tests for semantic entailment and modality alignment guardrails.

Enforces ISTQB Equivalence Partitioning across declarative affirmations,
interrogative inquiries, counterfactual speculations, and schema boundaries.
"""

from unittest.mock import AsyncMock, patch

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.dag_models import ExtractedAtom, LinkedAtomGraph
from backend_v2.models.dtos.engine import FlattenedAtom, MatrixEvaluationContext
from backend_v2.models.enums import ExecutionStatus
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.extractive_sensor_service import (
    BatchEvaluationResponse,
    BooleanEvaluationResult,
    ExtractiveSensorService,
)
from backend_v2.settings import get_settings


def _create_test_node(tda_id: str, claim: str) -> LinkedAtomGraph:
    """Helper creating an empirical atom graph node for testing."""
    atom = ExtractedAtom(
        tda_id=tda_id,
        reasoning="Test atom reasoning.",
        resolved_claim=claim,
        source_quote="Initial quote anchor",
        is_logical_deduction=False,
        source_id="chunk_0",
        source_sequence_index=0,
    )
    return LinkedAtomGraph(atom=atom, depends_on=[])


@pytest.mark.asyncio
async def test_positive_partition_declarative_affirmation_entails_claim() -> None:
    """Positive Partition: Declarative affirmation strictly entailing affirmative claim passes with quote."""
    tda_id = "tda_11111111111111111111111111111111"
    node = _create_test_node(tda_id, "Requires at least two explicitly named distinct alternatives.")
    context_text = (
        "Palvelussa tarjotaan kaksi erillistä toteutusvaihtoehtoa: nopea pilvitoteutus ja kattava on-premise ratkaisu."
    )
    valid_quote = (
        "Palvelussa tarjotaan kaksi erillistä toteutusvaihtoehtoa: nopea pilvitoteutus ja kattava on-premise ratkaisu."
    )

    executor = AsyncMock(spec=LLMTaskExecutor)
    client = AsyncMock(spec=LLMClient)

    mock_result = BooleanEvaluationResult(
        alias="a0",
        reasoning="Teksti toteaa nimenomaisesti kaksi erillistä toteutusvaihtoehtoa.",
        is_true=True,
        source_quote=valid_quote,
    )
    executor.execute_structured_task.return_value = (
        BatchEvaluationResponse(results=[mock_result]),
        TokenUsage(prompt_tokens=40, completion_tokens=20, total_tokens=60),
    )

    with (
        patch("backend_v2.services.orchestrator.extractive_sensor_service.AliasEngine.register", return_value="a0"),
        patch(
            "backend_v2.services.orchestrator.extractive_sensor_service.AliasEngine.resolve_alias",
            return_value=tda_id,
        ),
    ):
        results, usage = await ExtractiveSensorService.evaluate_atom_boolean_batch(
            nodes=[node],
            executor=executor,
            client=client,
            context_text=context_text,
            target_locale="fi",
        )

        assert tda_id in results
        assert results[tda_id].status == ExecutionStatus.PASSED
        assert results[tda_id].source_quote == valid_quote
        assert "kaksi erillistä toteutusvaihtoehtoa" in str(results[tda_id].reasoning)
        assert usage.total_tokens == 60 * get_settings().ensemble_parallelism


@pytest.mark.asyncio
async def test_negative_partition_interrogative_inquiry_rejected_under_null_hypothesis() -> None:
    """Negative Partition 1: Interrogative inquiry does not entail affirmative action; defaults to Null Hypothesis."""
    tda_id = "tda_22222222222222222222222222222222"
    node = _create_test_node(tda_id, "Requires at least two explicitly named distinct alternatives.")
    context_text = "Riittääkö yksi läsnäolopäivä? Mikä puoltaisi esim. kahta tai useampaa läsnäolopäivää?"

    executor = AsyncMock(spec=LLMTaskExecutor)
    client = AsyncMock(spec=LLMClient)

    # In accordance with <semantic_entailment_protocol>, interrogatives fail to entail positive claims
    mock_result = BooleanEvaluationResult(
        alias="a0",
        reasoning="Avoin kysymys tai pohdinta ei osoita päätöstä tai vaihtoehtojen toteutumista.",
        is_true=False,
        source_quote=None,
    )
    executor.execute_structured_task.return_value = (
        BatchEvaluationResponse(results=[mock_result]),
        TokenUsage(prompt_tokens=45, completion_tokens=15, total_tokens=60),
    )

    with (
        patch("backend_v2.services.orchestrator.extractive_sensor_service.AliasEngine.register", return_value="a0"),
        patch(
            "backend_v2.services.orchestrator.extractive_sensor_service.AliasEngine.resolve_alias",
            return_value=tda_id,
        ),
    ):
        results, usage = await ExtractiveSensorService.evaluate_atom_boolean_batch(
            nodes=[node],
            executor=executor,
            client=client,
            context_text=context_text,
            target_locale="fi",
        )

        assert tda_id in results
        assert results[tda_id].status == ExecutionStatus.FAILED
        assert results[tda_id].source_quote is None
        assert "pohdinta ei osoita" in str(results[tda_id].reasoning)


@pytest.mark.asyncio
async def test_negative_partition_counterfactual_refuted_premise_rejected() -> None:
    """Negative Partition 2: Counterfactual speculation and refuted premise fail to substantiate claim."""
    tda_id = "tda_33333333333333333333333333333333"
    node = _create_test_node(tda_id, "Implements dual operating models.")
    context_text = "Jos toteuttaisimme toisen toimintamallin, kustannukset karkaisivat, joten sitä ei toteuteta."

    executor = AsyncMock(spec=LLMTaskExecutor)
    client = AsyncMock(spec=LLMClient)

    mock_result = BooleanEvaluationResult(
        alias="a0",
        reasoning="Hypoteettinen ja hylätty vaihtoehto ei toteuta väitettä.",
        is_true=False,
        source_quote=None,
    )
    executor.execute_structured_task.return_value = (
        BatchEvaluationResponse(results=[mock_result]),
        TokenUsage(prompt_tokens=40, completion_tokens=20, total_tokens=60),
    )

    with (
        patch("backend_v2.services.orchestrator.extractive_sensor_service.AliasEngine.register", return_value="a0"),
        patch(
            "backend_v2.services.orchestrator.extractive_sensor_service.AliasEngine.resolve_alias",
            return_value=tda_id,
        ),
    ):
        results, usage = await ExtractiveSensorService.evaluate_atom_boolean_batch(
            nodes=[node],
            executor=executor,
            client=client,
            context_text=context_text,
            target_locale="fi",
        )

        assert tda_id in results
        assert results[tda_id].status == ExecutionStatus.FAILED
        assert results[tda_id].source_quote is None


@pytest.mark.asyncio
async def test_negative_partition_inverse_evidence_refutes_defect_without_quote() -> None:
    """Negative Partition 3: Inverse evidence refutes error; absence of error yields PASSED with null quote."""
    tda_id = "tda_44444444444444444444444444444444"
    node = _create_test_node(tda_id, "Commits hasty generalization without empirical validation.")
    context_text = "Kaikki johtopäätökset perustuvat kattavaan kolmivaiheiseen kenttäkokeeseen."

    executor = AsyncMock(spec=LLMTaskExecutor)
    client = AsyncMock(spec=LLMClient)

    mock_result = BooleanEvaluationResult(
        alias="a0",
        reasoning="Teksti ei sisällä hätiköityä yleistystä, vaan perustuu kenttäkokeeseen.",
        is_true=False,
        source_quote=None,
    )
    executor.execute_structured_task.return_value = (
        BatchEvaluationResponse(results=[mock_result]),
        TokenUsage(prompt_tokens=50, completion_tokens=20, total_tokens=70),
    )

    flattened = FlattenedAtom(
        atom_id=tda_id,
        question="Defect presence question.",
        extraction_rule="",
        anchor_target="",
        is_inverse=True,
        depends_on=(),
    )
    matrix_context = MatrixEvaluationContext(matrix_assertions=[flattened])

    with (
        patch("backend_v2.services.orchestrator.extractive_sensor_service.AliasEngine.register", return_value="a0"),
        patch(
            "backend_v2.services.orchestrator.extractive_sensor_service.AliasEngine.resolve_alias",
            return_value=tda_id,
        ),
    ):
        results, usage = await ExtractiveSensorService.evaluate_atom_boolean_batch(
            nodes=[node],
            executor=executor,
            client=client,
            context_text=context_text,
            target_locale="fi",
            matrix_context=matrix_context,
        )

        assert tda_id in results
        assert results[tda_id].status == ExecutionStatus.PASSED
        assert results[tda_id].source_quote is None


@pytest.mark.asyncio
@pytest.mark.parametrize("invalid_locale", ["", "   ", None])
async def test_boundary_partition_invalid_locale_fails_fast(invalid_locale: str | None) -> None:
    """Boundary Partition 1: Empty or whitespace locale raises AppException with VALIDATION_FAILED."""
    node = _create_test_node("tda_55555555555555555555555555555555", "Any claim.")
    executor = AsyncMock(spec=LLMTaskExecutor)
    client = AsyncMock(spec=LLMClient)

    with pytest.raises(AppException) as exc_info:
        await ExtractiveSensorService.evaluate_atom_boolean_batch(
            nodes=[node],
            executor=executor,
            client=client,
            context_text="Valid document context.",
            target_locale=invalid_locale,  # type: ignore[arg-type]
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_boundary_partition_boolean_evaluation_result_extra_forbid() -> None:
    """Boundary Partition 2: BooleanEvaluationResult rejects arbitrary unknown fields via ConfigDict(extra='forbid')."""
    with pytest.raises(ValidationError):
        BooleanEvaluationResult.model_validate(
            {
                "alias": "a0",
                "reasoning": "Some reasoning.",
                "is_true": True,
                "hallucinated_field": "disallowed",
            }
        )

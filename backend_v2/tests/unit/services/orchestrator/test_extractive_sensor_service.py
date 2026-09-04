from unittest.mock import AsyncMock, patch

import pytest
from pydantic import BaseModel

from backend_v2.exceptions import AgentExecutionError
from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.dag_models import (
    AtomEvaluationResultDTO,
    ExtractedAtom,
    LinkedAtomGraph,
)
from backend_v2.models.dtos.engine import FlattenedAtom, MatrixEvaluationContext
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.v2_core import TDAAssertion
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.extractive_sensor_service import (
    BooleanEvaluationResult,
    ExtractiveSensorService,
)


def test_extractive_sensor_service_fallback_llm() -> None:
    """Varmistaa että fallback tapahtuu jos enforce_pre_flight=False tai ankkureita ei ole."""
    tda = TDAAssertion(
        enforce_pre_flight=False,
        evaluation_track="EXTRACTIVE_SENSOR",
        facts_to_find=["Fakta"],
        logical_expression="Fakta",
        concept_description="Concept description valid",
        inverse_evidence=False,
        aggregation_mode="EXISTS",
        depends_on=(),
    )

    result = ExtractiveSensorService.pre_evaluate(tda, "Test text")
    assert not result.decided


def test_extractive_sensor_service_aggregation_exists_delegate() -> None:
    """Varmistaa että EXISTS -aggregaatio palauttaa decided=False (delegoi LLM:lle), jos ankkuri LÖYTYY."""
    tda = TDAAssertion(
        enforce_pre_flight=True,
        syntactic_anchors=["must_find_this", "or_this"],
        aggregation_mode="EXISTS",
        evaluation_track="EXTRACTIVE_SENSOR",
        facts_to_find=["Fakta"],
        logical_expression="Fakta",
        concept_description="Concept description valid",
        inverse_evidence=False,
        depends_on=(),
    )

    # Ankkuri löytyy -> Ei voida tehdä pre-flight päätöstä (pitää antaa LLM arvioida Bounding Box)
    result = ExtractiveSensorService.pre_evaluate(tda, "Some text where must_find_this is located.")
    assert not result.decided


def test_extractive_sensor_service_aggregation_exists_fail() -> None:
    """Varmistaa että EXISTS -aggregaatio palauttaa decided=True ja FAIL, jos MITÄÄN ankkuria ei löydy."""
    tda = TDAAssertion(
        enforce_pre_flight=True,
        syntactic_anchors=["anchor1", "anchor2"],
        aggregation_mode="EXISTS",
        evaluation_track="EXTRACTIVE_SENSOR",
        facts_to_find=["Fakta"],
        logical_expression="Fakta",
        concept_description="Concept description valid",
        inverse_evidence=False,
        depends_on=(),
    )

    # Yhtäkään ankkuria ei löydy -> Voidaan hylätä suoraan ilman LLM:ää
    result = ExtractiveSensorService.pre_evaluate(tda, "Completely different text.")
    assert result.decided
    assert result.result == ExecutionStatus.FAILED
    assert result.exact_quotes is None


def test_extractive_sensor_service_aggregation_all_must_comply_fail() -> None:
    """Varmistaa että ALL_MUST_COMPLY -aggregaatio epäonnistuu suoraan, jos yksikin puuttuu."""
    tda = TDAAssertion(
        enforce_pre_flight=True,
        syntactic_anchors=["anchor1", "anchor2"],
        aggregation_mode="ALL_MUST_COMPLY",
        evaluation_track="EXTRACTIVE_SENSOR",
        facts_to_find=["Fakta"],
        logical_expression="Fakta",
        concept_description="Concept description valid",
        inverse_evidence=False,
        depends_on=(),
    )

    result = ExtractiveSensorService.pre_evaluate(tda, "Text with only anchor1 present.")
    assert result.decided
    assert result.result == ExecutionStatus.FAILED


def test_extractive_sensor_service_inverse_evidence_early_exit() -> None:
    """Varmistaa että negaatio kääntää tuloksen (myrkyn etsintä) kun päätös voidaan tehdä."""
    tda = TDAAssertion(
        enforce_pre_flight=True,
        syntactic_anchors=["poison"],
        aggregation_mode="EXISTS",
        inverse_evidence=True,
        evaluation_track="EXTRACTIVE_SENSOR",
        facts_to_find=["Fakta"],
        logical_expression="Fakta",
        concept_description="Concept description valid",
        depends_on=(),
    )

    # Poison ei löydy -> Voidaan päättää heti. Koska se on inverse, puuttuminen on PASS.
    result = ExtractiveSensorService.pre_evaluate(tda, "Clean text here.")
    assert result.decided
    assert result.result == ExecutionStatus.PASSED

    # Poison löytyy -> Ei voida päättää (saattaa olla ettei ehto silti täyty esim contextin takia)
    result2 = ExtractiveSensorService.pre_evaluate(tda, "Text with poison inside.")
    assert not result2.decided


def test_extractive_sensor_service_fuzzy_match() -> None:
    """Varmistaa että sumea mätsäys toimii lokaalipohjaisella kynnysarvolla."""
    tda = TDAAssertion(
        enforce_pre_flight=True,
        syntactic_anchors=["must_find_this"],
        aggregation_mode="EXISTS",
        evaluation_track="EXTRACTIVE_SENSOR",
        facts_to_find=["Fakta"],
        logical_expression="Fakta",
        concept_description="Concept description valid",
        inverse_evidence=False,
        depends_on=(),
    )

    # 1. Pitäisi delegoida LLM:lle (decided=False), koska ankkuri "löytyy" sumeasti (typo "must_fiind_this")
    result_fi = ExtractiveSensorService.pre_evaluate(tda, "Some text where must_fiind_this is located.", locale="fi")
    assert not result_fi.decided

    # 2. Pitäisi failata early exitillä, jos typoja on liikaa (esim. "must_fxxnd_this")
    result_fail = ExtractiveSensorService.pre_evaluate(tda, "Some text where must_fxxnd_this is located.", locale="en")
    assert result_fail.decided
    assert result_fail.result == ExecutionStatus.FAILED


def test_extractive_sensor_service_extracted_atom_pre_evaluate_empty_quote() -> None:

    atom = ExtractedAtom(
        tda_id="tda_11111111111111111111111111111111",
        reasoning="reason",
        resolved_claim="claim",
        source_quote="None",
        source_id="src",
        source_sequence_index=0,
    )
    result = ExtractiveSensorService.pre_evaluate(atom, "Some text")
    assert not result.decided


def test_extractive_sensor_service_extracted_atom_pre_evaluate_fail() -> None:

    atom = ExtractedAtom(
        tda_id="tda_11111111111111111111111111111111",
        reasoning="reason",
        resolved_claim="claim",
        source_quote="Very specific quote that is not here",
        source_id="src",
        source_sequence_index=0,
    )
    result = ExtractiveSensorService.pre_evaluate(atom, "Completely different text")
    assert result.decided
    assert result.result == ExecutionStatus.FAILED


@pytest.mark.asyncio
async def test_extractive_sensor_service_batch_pre_evaluate() -> None:

    # 1. Undecided
    atom_undecided = ExtractedAtom(
        tda_id="tda_11111111111111111111111111111111",
        reasoning="reason",
        resolved_claim="claim",
        source_quote="undecided_quote",
        source_id="src",
        source_sequence_index=0,
    )
    node_undecided = LinkedAtomGraph(atom=atom_undecided, depends_on=[])

    # 2. Decided Fail
    atom_fail = ExtractedAtom(
        tda_id="tda_22222222222222222222222222222222",
        reasoning="reason",
        resolved_claim="claim",
        source_quote="fail_quote",
        source_id="src",
        source_sequence_index=0,
    )
    node_fail = LinkedAtomGraph(atom=atom_fail, depends_on=[])

    decided, undecided = await ExtractiveSensorService.batch_pre_evaluate(
        [node_undecided, node_fail], source_text="This text contains undecided_quote"
    )

    assert len(undecided) == 1
    assert undecided[0].atom.tda_id == "tda_11111111111111111111111111111111"

    assert "tda_22222222222222222222222222222222" in decided
    assert decided["tda_22222222222222222222222222222222"].status == ExecutionStatus.FAILED


def test_extractive_sensor_service_resolve_majority_vote() -> None:

    # Success case (2 PASS)
    results: list[dict[str, AtomEvaluationResultDTO] | None] = [
        {
            "tda_11111111111111111111111111111111": AtomEvaluationResultDTO(
                status=ExecutionStatus.PASSED, reasoning="r1"
            )
        },
        {
            "tda_11111111111111111111111111111111": AtomEvaluationResultDTO(
                status=ExecutionStatus.FAILED, reasoning="r2"
            )
        },
        {
            "tda_11111111111111111111111111111111": AtomEvaluationResultDTO(
                status=ExecutionStatus.PASSED, reasoning="r3"
            )
        },
    ]
    resolved = ExtractiveSensorService.resolve_majority_vote(["tda_11111111111111111111111111111111"], results)
    assert resolved["tda_11111111111111111111111111111111"].status == ExecutionStatus.PASSED

    # Insufficient valid results
    with pytest.raises(AgentExecutionError):
        ExtractiveSensorService.resolve_majority_vote(
            ["tda_11111111111111111111111111111111"],
            [
                {
                    "tda_11111111111111111111111111111111": AtomEvaluationResultDTO(
                        status=ExecutionStatus.PASSED, reasoning="r1"
                    )
                }
            ],
        )

    # Split vote without consensus (if min_consensus was 2, but we only have 3 different? Actually booleans only have 2 states)
    # But if an atom was missing from responses
    results_split: list[dict[str, AtomEvaluationResultDTO] | None] = [
        {
            "tda_11111111111111111111111111111111": AtomEvaluationResultDTO(
                status=ExecutionStatus.PASSED, reasoning="r1"
            )
        },
        {
            "tda_22222222222222222222222222222222": AtomEvaluationResultDTO(
                status=ExecutionStatus.FAILED, reasoning="r2"
            )
        },
        {
            "tda_33333333333333333333333333333333": AtomEvaluationResultDTO(
                status=ExecutionStatus.PASSED, reasoning="r3"
            )
        },
    ]
    resolved_split = ExtractiveSensorService.resolve_majority_vote(
        ["tda_11111111111111111111111111111111"], results_split
    )
    assert resolved_split["tda_11111111111111111111111111111111"].status == ExecutionStatus.SYSTEM_ERROR


def test_extractive_sensor_service_resolve_majority_vote_tie_breaker() -> None:
    """Verifies Null Hypothesis tie-breaker logic across 6 ISTQB equivalence partitions."""
    tda_id = "tda_11111111111111111111111111111111"

    # 1. Partition A (Positive Claim Split: 1 PASSED, 1 FAILED, is_inverse=False -> FAILED)
    results_split: list[dict[str, AtomEvaluationResultDTO] | None] = [
        {tda_id: AtomEvaluationResultDTO(status=ExecutionStatus.PASSED, reasoning="r1", source_quote="quote 1")},
        {tda_id: AtomEvaluationResultDTO(status=ExecutionStatus.FAILED, reasoning="r2", source_quote=None)},
        None,  # 3rd call failed transiently
    ]
    res_pos = ExtractiveSensorService.resolve_majority_vote(
        [tda_id], results_split, is_inverse_map={tda_id: False}
    )
    assert res_pos[tda_id].status == ExecutionStatus.FAILED
    assert res_pos[tda_id].source_quote is None
    assert "EPISTEMIC_TIE_BREAKER" in (res_pos[tda_id].reasoning or "")

    # 2. Partition B (Inverse Claim Split: 1 PASSED, 1 FAILED, is_inverse=True -> PASSED)
    res_inv = ExtractiveSensorService.resolve_majority_vote(
        [tda_id], results_split, is_inverse_map={tda_id: True}
    )
    assert res_inv[tda_id].status == ExecutionStatus.PASSED
    assert res_inv[tda_id].source_quote is None
    assert "EPISTEMIC_TIE_BREAKER" in (res_inv[tda_id].reasoning or "")

    # 3. Partition C (Missing Polarity Map: 1 PASSED, 1 FAILED, is_inverse_map=None -> SYSTEM_ERROR)
    res_no_map = ExtractiveSensorService.resolve_majority_vote(
        [tda_id], results_split, is_inverse_map=None
    )
    assert res_no_map[tda_id].status == ExecutionStatus.SYSTEM_ERROR
    assert res_no_map[tda_id].reasoning == "INSUFFICIENT_CONSENSUS"

    # 4. Partition D (Unregistered TDA Fallback: 1 PASSED, 1 FAILED, tda_id missing from map -> SYSTEM_ERROR)
    res_unreg = ExtractiveSensorService.resolve_majority_vote(
        [tda_id], results_split, is_inverse_map={"tda_other": False}
    )
    assert res_unreg[tda_id].status == ExecutionStatus.SYSTEM_ERROR
    assert res_unreg[tda_id].reasoning == "INSUFFICIENT_CONSENSUS"

    # 5. Partition E (Unanimous Consensus: 2 PASSED, 1 FAILED -> PASSED regardless of is_inverse)
    results_consensus: list[dict[str, AtomEvaluationResultDTO] | None] = [
        {tda_id: AtomEvaluationResultDTO(status=ExecutionStatus.PASSED, reasoning="r1", source_quote="valid quote")},
        {tda_id: AtomEvaluationResultDTO(status=ExecutionStatus.FAILED, reasoning="r2", source_quote=None)},
        {tda_id: AtomEvaluationResultDTO(status=ExecutionStatus.PASSED, reasoning="r3", source_quote="valid quote")},
    ]
    res_consensus = ExtractiveSensorService.resolve_majority_vote(
        [tda_id], results_consensus, is_inverse_map={tda_id: False}
    )
    assert res_consensus[tda_id].status == ExecutionStatus.PASSED
    assert res_consensus[tda_id].source_quote == "valid quote"

    # 6. Partition F (Zero Votes Cast: atom missing from all responses -> SYSTEM_ERROR)
    results_empty: list[dict[str, AtomEvaluationResultDTO] | None] = [
        {"tda_other": AtomEvaluationResultDTO(status=ExecutionStatus.PASSED, reasoning="r1")},
        {"tda_other": AtomEvaluationResultDTO(status=ExecutionStatus.PASSED, reasoning="r2")},
    ]
    res_zero = ExtractiveSensorService.resolve_majority_vote(
        [tda_id], results_empty, is_inverse_map={tda_id: True}
    )
    assert res_zero[tda_id].status == ExecutionStatus.SYSTEM_ERROR
    assert "UNRETURNED_BY_MODEL" in (res_zero[tda_id].reasoning or "")



@pytest.mark.asyncio
async def test_extractive_sensor_service_evaluate_atom_boolean_batch() -> None:

    atom = ExtractedAtom(
        tda_id="tda_11111111111111111111111111111111",
        reasoning="reason",
        resolved_claim="claim",
        source_quote="quote",
        source_id="src",
        source_sequence_index=0,
    )
    node = LinkedAtomGraph(atom=atom, depends_on=[])

    executor = AsyncMock(spec=LLMTaskExecutor)
    client = AsyncMock(spec=LLMClient)

    # We must mock executor.execute_structured_task to return a BatchEvaluationResponse-like dict or model
    # The actual BatchEvaluationResponse is defined inside evaluate_atom_boolean_batch, so we can't easily import it.
    # We will use a mock that has a `results` attribute
    class MockResult(BaseModel):
        alias: str
        reasoning: str
        is_true: bool
        source_quote: str | None = None
        contextual_override: bool | None = None
        coaching: str | None = None
        falsification: str | None = None
        remediation_steps: list[str] | None = None

    class MockResponse(BaseModel):
        results: list[MockResult]

    executor.execute_structured_task.return_value = (
        MockResponse(
            results=[MockResult(alias="a1", reasoning="ok", is_true=True, contextual_override=True, coaching="tip")]
        ),
        TokenUsage(prompt_tokens=50, completion_tokens=10, total_tokens=60),
    )

    with (
        patch("backend_v2.services.orchestrator.extractive_sensor_service.AliasEngine.register", return_value="a1"),
        patch(
            "backend_v2.services.orchestrator.extractive_sensor_service.AliasEngine.resolve_alias",
            return_value="tda_11111111111111111111111111111111",
        ),
    ):
        results, usage = await ExtractiveSensorService.evaluate_atom_boolean_batch([node], executor, client, "context")

        assert "tda_11111111111111111111111111111111" in results
        assert results["tda_11111111111111111111111111111111"].status == ExecutionStatus.PASSED
        assert results["tda_11111111111111111111111111111111"].extensions["coaching"] == "tip"
        assert results["tda_11111111111111111111111111111111"].extensions["contextual_override"] == "True"
        assert usage.total_tokens == 180


def test_extractive_sensor_service_allow_contextual_override() -> None:
    """Varmistaa että pre-flight ohitetaan jos allow_contextual_override on True."""
    tda = TDAAssertion(
        enforce_pre_flight=True,
        syntactic_anchors=["anchor_missing"],
        aggregation_mode="EXISTS",
        evaluation_track="EXTRACTIVE_SENSOR",
        facts_to_find=["Fakta"],
        logical_expression="Fakta",
        concept_description="Concept description valid",
        inverse_evidence=False,
        depends_on=(),
    )

    # 1. strictly set to False -> early fail
    result_fail = ExtractiveSensorService.pre_evaluate(
        tda, "Completely different text.", allow_contextual_override=False
    )
    assert result_fail.decided
    assert result_fail.result == ExecutionStatus.FAILED

    # 2. strictly set to True -> delegated
    result_delegate = ExtractiveSensorService.pre_evaluate(
        tda, "Completely different text.", allow_contextual_override=True
    )
    assert not result_delegate.decided


@pytest.mark.asyncio
async def test_extractive_sensor_service_evaluate_atom_boolean_batch_null_theory_grounding() -> None:
    """Varmistaa että LLM pystyy käsittelemään atomit turvallisesti vaikka theory_grounding puuttuu matriisikontekstista."""
    atom = ExtractedAtom(
        tda_id="tda_11111111111111111111111111111111",
        reasoning="reason",
        resolved_claim="claim",
        source_quote="quote",
        source_id="src",
        source_sequence_index=0,
    )
    node = LinkedAtomGraph(atom=atom, depends_on=[])

    executor = AsyncMock(spec=LLMTaskExecutor)
    client = AsyncMock(spec=LLMClient)

    class MockResult(BaseModel):
        alias: str
        reasoning: str
        is_true: bool
        source_quote: str | None = None
        contextual_override: bool | None = None
        coaching: str | None = None
        falsification: str | None = None
        remediation_steps: list[str] | None = None

    class MockResponse(BaseModel):
        results: list[MockResult]

    executor.execute_structured_task.return_value = (
        MockResponse(results=[MockResult(alias="a1", reasoning="ok", is_true=True)]),
        TokenUsage(prompt_tokens=50, completion_tokens=10, total_tokens=60),
    )

    # Context without theory_grounding
    matrix_context = MatrixEvaluationContext(
        allow_contextual_override=True,
    )

    with (
        patch("backend_v2.services.orchestrator.extractive_sensor_service.AliasEngine.register", return_value="a1"),
        patch(
            "backend_v2.services.orchestrator.extractive_sensor_service.AliasEngine.resolve_alias",
            return_value="tda_11111111111111111111111111111111",
        ),
    ):
        results, usage = await ExtractiveSensorService.evaluate_atom_boolean_batch(
            [node], executor, client, "context", matrix_context=matrix_context
        )

        assert "tda_11111111111111111111111111111111" in results
        assert results["tda_11111111111111111111111111111111"].status == ExecutionStatus.PASSED
        assert usage.total_tokens == 180


@pytest.mark.asyncio
async def test_extractive_sensor_service_evaluate_atom_boolean_batch_inverse_evidence_passed() -> None:
    """Verifies that an atom with is_inverse=True results in ExecutionStatus.PASSED when is_true=False (no penalty)."""
    tda_id = "tda_11111111111111111111111111111111"
    atom = ExtractedAtom(
        tda_id=tda_id,
        reasoning="Negative condition evaluated.",
        resolved_claim="Penalty claim.",
        source_quote=None,
        is_logical_deduction=True,
        source_id="src",
        source_sequence_index=0,
    )
    node = LinkedAtomGraph(atom=atom, depends_on=[])

    executor = AsyncMock(spec=LLMTaskExecutor)
    client = AsyncMock(spec=LLMClient)

    class MockResult(BaseModel):
        alias: str
        reasoning: str
        is_true: bool
        source_quote: str | None = None
        contextual_override: bool | None = None
        coaching: str | None = None
        falsification: str | None = None
        remediation_steps: list[str] | None = None

    class MockResponse(BaseModel):
        results: list[MockResult]

    # LLM confirms poison/penalty is FALSE -> should map to PASSED for inverse_evidence
    executor.execute_structured_task.return_value = (
        MockResponse(results=[MockResult(alias="a1", reasoning="No penalty found", is_true=False)]),
        TokenUsage(prompt_tokens=50, completion_tokens=10, total_tokens=60),
    )

    flattened = FlattenedAtom(
        atom_id=tda_id,
        question="Penalty claim question.",
        extraction_rule="",
        anchor_target="",
        is_inverse=True,
        depends_on=(),
    )
    matrix_context = MatrixEvaluationContext(
        matrix_assertions=[flattened],
    )

    with (
        patch("backend_v2.services.orchestrator.extractive_sensor_service.AliasEngine.register", return_value="a1"),
        patch(
            "backend_v2.services.orchestrator.extractive_sensor_service.AliasEngine.resolve_alias",
            return_value=tda_id,
        ),
    ):
        results, usage = await ExtractiveSensorService.evaluate_atom_boolean_batch(
            [node], executor, client, "context", matrix_context=matrix_context
        )

        assert tda_id in results
        assert results[tda_id].status == ExecutionStatus.PASSED
        assert results[tda_id].reasoning == "No penalty found"
        assert usage.total_tokens == 180


@pytest.mark.asyncio
async def test_extractive_sensor_service_evaluate_atom_boolean_batch_inverse_evidence_failed() -> None:
    """Verifies that an atom with is_inverse=True results in ExecutionStatus.FAILED when is_true=True (penalty detected)."""
    tda_id = "tda_11111111111111111111111111111111"
    atom = ExtractedAtom(
        tda_id=tda_id,
        reasoning="Negative condition evaluated.",
        resolved_claim="Penalty claim.",
        source_quote=None,
        is_logical_deduction=True,
        source_id="src",
        source_sequence_index=0,
    )
    node = LinkedAtomGraph(atom=atom, depends_on=[])

    executor = AsyncMock(spec=LLMTaskExecutor)
    client = AsyncMock(spec=LLMClient)

    class MockResult(BaseModel):
        alias: str
        reasoning: str
        is_true: bool
        source_quote: str | None = None
        contextual_override: bool | None = None
        coaching: str | None = None
        falsification: str | None = None
        remediation_steps: list[str] | None = None

    class MockResponse(BaseModel):
        results: list[MockResult]

    # LLM confirms poison/penalty is TRUE -> should map to FAILED for inverse_evidence
    executor.execute_structured_task.return_value = (
        MockResponse(results=[MockResult(alias="a1", reasoning="Penalty detected in text", is_true=True)]),
        TokenUsage(prompt_tokens=50, completion_tokens=10, total_tokens=60),
    )

    flattened = FlattenedAtom(
        atom_id=tda_id,
        question="Penalty claim question.",
        extraction_rule="",
        anchor_target="",
        is_inverse=True,
        depends_on=(),
    )
    matrix_context = MatrixEvaluationContext(
        matrix_assertions=[flattened],
    )

    with (
        patch("backend_v2.services.orchestrator.extractive_sensor_service.AliasEngine.register", return_value="a1"),
        patch(
            "backend_v2.services.orchestrator.extractive_sensor_service.AliasEngine.resolve_alias",
            return_value=tda_id,
        ),
    ):
        results, usage = await ExtractiveSensorService.evaluate_atom_boolean_batch(
            [node], executor, client, "context", matrix_context=matrix_context
        )

        assert tda_id in results
        assert results[tda_id].status == ExecutionStatus.FAILED
        assert results[tda_id].reasoning == "Penalty detected in text"
        assert usage.total_tokens == 180


def test_boolean_evaluation_result_sentence_boundary_truncation() -> None:
    """Verifies that BooleanEvaluationResult truncates oversized quotes (>500 chars) at sentence boundary."""
    long_quote = "Ensimmäinen lause tekstissä. " * 20  # ~580 chars
    res = BooleanEvaluationResult(
        alias="a0",
        reasoning="Test reasoning",
        is_true=True,
        source_quote=long_quote,
    )
    assert res.source_quote is not None
    assert len(res.source_quote) <= 500
    assert res.source_quote.endswith(".")


def test_extractive_sensor_service_majority_vote_preserves_quote() -> None:
    """Verifies that resolve_majority_vote preserves winning vote's source_quote."""
    tda_id = "tda_11111111111111111111111111111111"
    results: list[dict[str, AtomEvaluationResultDTO] | None] = [
        {
            tda_id: AtomEvaluationResultDTO(
                status=ExecutionStatus.PASSED,
                reasoning="Vahvistettu",
                source_quote="Tämä on suora lainaus lähteestä.",
            )
        },
        {
            tda_id: AtomEvaluationResultDTO(
                status=ExecutionStatus.PASSED,
                reasoning="Sama havainto",
                source_quote="Tämä on toinen suora lainaus.",
            )
        },
        {
            tda_id: AtomEvaluationResultDTO(
                status=ExecutionStatus.FAILED,
                reasoning="Eri mieltä",
                source_quote=None,
            )
        },
    ]
    resolved = ExtractiveSensorService.resolve_majority_vote([tda_id], results)
    assert resolved[tda_id].status == ExecutionStatus.PASSED
    assert resolved[tda_id].source_quote == "Tämä on suora lainaus lähteestä."


@pytest.mark.asyncio
async def test_extractive_sensor_service_evaluate_batch_extracts_source_quote() -> None:
    """Verifies that evaluate_atom_boolean_batch extracts and transits source_quote in original language."""
    tda_id = "tda_11111111111111111111111111111111"
    atom = ExtractedAtom(
        tda_id=tda_id,
        reasoning="reason",
        resolved_claim="claim",
        source_quote="Initial static claim",
        source_id="src",
        source_sequence_index=0,
    )
    node = LinkedAtomGraph(atom=atom, depends_on=[])

    executor = AsyncMock(spec=LLMTaskExecutor)
    client = AsyncMock(spec=LLMClient)

    class MockResult(BaseModel):
        alias: str
        reasoning: str
        is_true: bool
        source_quote: str | None = None
        contextual_override: bool | None = None
        coaching: str | None = None
        falsification: str | None = None
        remediation_steps: list[str] | None = None

    class MockResponse(BaseModel):
        results: list[MockResult]

    original_quote = "Tämä on alkuperäiskielinen todisteaineisto."
    executor.execute_structured_task.return_value = (
        MockResponse(
            results=[
                MockResult(
                    alias="a1",
                    reasoning="Löydetty suora sitaatti",
                    is_true=True,
                    source_quote=original_quote,
                )
            ]
        ),
        TokenUsage(prompt_tokens=50, completion_tokens=10, total_tokens=60),
    )

    with (
        patch("backend_v2.services.orchestrator.extractive_sensor_service.AliasEngine.register", return_value="a1"),
        patch(
            "backend_v2.services.orchestrator.extractive_sensor_service.AliasEngine.resolve_alias",
            return_value=tda_id,
        ),
    ):
        results, usage = await ExtractiveSensorService.evaluate_atom_boolean_batch([node], executor, client, "Teksti")

        assert tda_id in results
        assert results[tda_id].status == ExecutionStatus.PASSED
        assert results[tda_id].source_quote == original_quote

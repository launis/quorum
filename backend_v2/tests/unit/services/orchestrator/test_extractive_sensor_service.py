from backend_v2.models.v2_core import TDAAssertion
from backend_v2.services.orchestrator.extractive_sensor_service import (
    ExtractiveSensorService,
)
from unittest.mock import patch
import pytest


def test_extractive_sensor_service_fallback_llm() -> None:
    """Varmistaa että fallback tapahtuu jos enforce_pre_flight=False tai ankkureita ei ole."""
    tda = TDAAssertion(
        enforce_pre_flight=False,
        evaluation_track="EXTRACTIVE_SENSOR",
        facts_to_find=["Fakta"],
        logical_expression="Fakta",
        concept_description="desc",
        inverse_evidence=False,
        aggregation_mode="EXISTS",
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
        concept_description="desc",
        inverse_evidence=False,
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
        concept_description="desc",
        inverse_evidence=False,
    )

    # Yhtäkään ankkuria ei löydy -> Voidaan hylätä suoraan ilman LLM:ää
    result = ExtractiveSensorService.pre_evaluate(tda, "Completely different text.")
    assert result.decided
    assert result.result == "FAIL"
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
        concept_description="desc",
        inverse_evidence=False,
    )

    result = ExtractiveSensorService.pre_evaluate(tda, "Text with only anchor1 present.")
    assert result.decided
    assert result.result == "FAIL"


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
        concept_description="desc",
    )

    # Poison ei löydy -> Voidaan päättää heti. Koska se on inverse, puuttuminen on PASS.
    result = ExtractiveSensorService.pre_evaluate(tda, "Clean text here.")
    assert result.decided
    assert result.result == "PASS"

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
        concept_description="desc",
        inverse_evidence=False,
    )

    # 1. Pitäisi delegoida LLM:lle (decided=False), koska ankkuri "löytyy" sumeasti (typo "must_fiind_this")
    result_fi = ExtractiveSensorService.pre_evaluate(tda, "Some text where must_fiind_this is located.", locale="fi")
    assert not result_fi.decided

    # 2. Pitäisi failata early exitillä, jos typoja on liikaa (esim. "must_fxxnd_this")
    result_fail = ExtractiveSensorService.pre_evaluate(tda, "Some text where must_fxxnd_this is located.", locale="en")
    assert result_fail.decided
    assert result_fail.result == "FAIL"


def test_extractive_sensor_service_extracted_atom_pre_evaluate_empty_quote() -> None:
    from backend_v2.models.dtos.dag_models import ExtractedAtom
    atom = ExtractedAtom(
        tda_id="tda_11111111111111111111111111111111",
        reasoning="reason",
        resolved_claim="claim",
        source_quote="None",
        source_id="src"
    )
    result = ExtractiveSensorService.pre_evaluate(atom, "Some text")
    assert not result.decided


def test_extractive_sensor_service_extracted_atom_pre_evaluate_fail() -> None:
    from backend_v2.models.dtos.dag_models import ExtractedAtom
    atom = ExtractedAtom(
        tda_id="tda_11111111111111111111111111111111",
        reasoning="reason",
        resolved_claim="claim",
        source_quote="Very specific quote that is not here",
        source_id="src"
    )
    result = ExtractiveSensorService.pre_evaluate(atom, "Completely different text")
    assert result.decided
    assert result.result == "FAIL"


@pytest.mark.asyncio
async def test_extractive_sensor_service_batch_pre_evaluate() -> None:
    from backend_v2.models.dtos.dag_models import ExtractedAtom, LinkedAtomGraph
    from backend_v2.models.enums import ExecutionStatus
    
    # 1. Undecided
    atom_undecided = ExtractedAtom(tda_id="tda_11111111111111111111111111111111", reasoning="reason", resolved_claim="claim", source_quote="undecided_quote", source_id="src")
    node_undecided = LinkedAtomGraph(atom=atom_undecided, depends_on=[])
    
    # 2. Decided Fail
    atom_fail = ExtractedAtom(tda_id="tda_22222222222222222222222222222222", reasoning="reason", resolved_claim="claim", source_quote="fail_quote", source_id="src")
    node_fail = LinkedAtomGraph(atom=atom_fail, depends_on=[])
    
    decided, undecided = await ExtractiveSensorService.batch_pre_evaluate(
        [node_undecided, node_fail],
        source_text="This text contains undecided_quote"
    )
    
    assert len(undecided) == 1
    assert undecided[0].atom.tda_id == "tda_11111111111111111111111111111111"
    
    assert "tda_22222222222222222222222222222222" in decided
    assert decided["tda_22222222222222222222222222222222"][0] == ExecutionStatus.FAILED


def test_extractive_sensor_service_resolve_majority_vote() -> None:
    from backend_v2.models.enums import ExecutionStatus
    from backend_v2.exceptions import AgentExecutionError
    
    # Success case (2 PASS)
    results = [
        {"tda_11111111111111111111111111111111": (ExecutionStatus.PASSED, "r1", {})},
        {"tda_11111111111111111111111111111111": (ExecutionStatus.FAILED, "r2", {})},
        {"tda_11111111111111111111111111111111": (ExecutionStatus.PASSED, "r3", {})},
    ]
    resolved = ExtractiveSensorService.resolve_majority_vote(["tda_11111111111111111111111111111111"], results)
    assert resolved["tda_11111111111111111111111111111111"][0] == ExecutionStatus.PASSED
    
    # Insufficient valid results
    with pytest.raises(AgentExecutionError):
        ExtractiveSensorService.resolve_majority_vote(["tda_11111111111111111111111111111111"], [{"tda_11111111111111111111111111111111": (ExecutionStatus.PASSED, "r1", {})}])
        
    # Split vote without consensus (if min_consensus was 2, but we only have 3 different? Actually booleans only have 2 states)
    # But if an atom was missing from responses
    results_split = [
        {"tda_11111111111111111111111111111111": (ExecutionStatus.PASSED, "r1", {})},
        {"tda_22222222222222222222222222222222": (ExecutionStatus.FAILED, "r2", {})},
        {"tda_33333333333333333333333333333333": (ExecutionStatus.PASSED, "r3", {})},
    ]
    resolved_split = ExtractiveSensorService.resolve_majority_vote(["tda_11111111111111111111111111111111"], results_split)
    assert resolved_split["tda_11111111111111111111111111111111"][0] == ExecutionStatus.SYSTEM_ERROR


@pytest.mark.asyncio
async def test_extractive_sensor_service_evaluate_atom_boolean_batch() -> None:
    from backend_v2.models.dtos.dag_models import ExtractedAtom, LinkedAtomGraph
    from backend_v2.models.enums import ExecutionStatus
    from backend_v2.services.llm_task_executor import LLMTaskExecutor
    from backend_v2.llm.client import LLMClient
    from unittest.mock import AsyncMock, MagicMock
    from pydantic import BaseModel
    
    atom = ExtractedAtom(tda_id="tda_11111111111111111111111111111111", reasoning="reason", resolved_claim="claim", source_quote="quote", source_id="src")
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
        coaching: str | None = None
        falsification: str | None = None
        remediation_steps: list[str] | None = None
        
    class MockResponse(BaseModel):
        results: list[MockResult]
        
    executor.execute_structured_task.return_value = (
        MockResponse(results=[MockResult(alias="a1", reasoning="ok", is_true=True, coaching="tip")]),
        {"total_tokens": 10}
    )
    
    from backend_v2.utils.alias_engine import AliasEngine
    with patch("backend_v2.services.orchestrator.extractive_sensor_service.AliasEngine.register", return_value="a1"), \
         patch("backend_v2.services.orchestrator.extractive_sensor_service.AliasEngine.resolve_alias", return_value="tda_11111111111111111111111111111111"):
        results = await ExtractiveSensorService.evaluate_atom_boolean_batch([node], executor, client, "context")
        
        assert "tda_11111111111111111111111111111111" in results
        assert results["tda_11111111111111111111111111111111"][0] == ExecutionStatus.PASSED
        assert results["tda_11111111111111111111111111111111"][2]["coaching"] == "tip"

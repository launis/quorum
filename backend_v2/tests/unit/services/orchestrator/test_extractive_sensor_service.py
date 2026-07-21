from unittest.mock import AsyncMock
from backend_v2.models.v2_core import TDAAssertion
from backend_v2.services.orchestrator.extractive_sensor_service import (
    ExtractiveSensorService,
)


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

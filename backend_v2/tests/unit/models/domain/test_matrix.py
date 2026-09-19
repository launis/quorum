"""Unit tests for matrix domain models."""

import pytest
from pydantic import ValidationError

from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.matrix import (
    AcceptanceCriterion,
    AntiPattern,
    ContrastivePairDTO,
    MatrixClaim,
    MatrixRow,
    MatrixScale,
    TDAAssertion,
    TheoryGrounding,
)
from backend_v2.models.dtos.dag_models import CausalEdge


def test_theory_grounding() -> None:
    tg = TheoryGrounding(source_url="https://example.com/theory", citation_reference="Section 4.2")
    assert tg.source_url == "https://example.com/theory"
    assert tg.citation_reference == "Section 4.2"


def test_contrastive_pair_valid() -> None:
    cp = ContrastivePairDTO(
        acceptable="This is an acceptable exemplar that meets requirements.",
        rejected="This is a rejected exemplar that fails boundaries.",
    )
    assert len(cp.acceptable) >= 10
    assert len(cp.rejected) >= 10


def test_contrastive_pair_identical_raises() -> None:
    with pytest.raises(ValueError, match="cannot be identical"):
        ContrastivePairDTO(
            acceptable="This is identical text here.",
            rejected="This is identical text here.",
        )


def test_tda_assertion_valid() -> None:
    tda = TDAAssertion(
        inverse_evidence=False,
        aggregation_mode="ALL_MUST_COMPLY",
        concept_description="Concept description that is at least 10 chars.",
        acceptance_criteria=[AcceptanceCriterion(instruction="At least five chars long")],
        anti_patterns=[AntiPattern(pattern="Anti pattern five chars")],
        depends_on=(
            CausalEdge(
                tda_id="tda_0123456789abcdef0123456789abcdef",
                source_id="chk_0123456789abcdef",
                edge_reasoning="Causal dependency exists because X implies Y",
            ),
        ),
    )
    assert tda.inverse_evidence is False
    assert tda.aggregation_mode == "ALL_MUST_COMPLY"
    assert len(tda.depends_on) == 1



def test_tda_assertion_inverse_evidence_requires_exists() -> None:
    with pytest.raises(ValueError, match="strictly requires 'EXISTS' aggregation mode"):
        TDAAssertion(
            inverse_evidence=True,
            aggregation_mode="ALL_MUST_COMPLY",
            concept_description="Concept description that is at least 10 chars.",
        )


def test_matrix_claim_and_scale() -> None:
    claim = MatrixClaim(
        label=I18nText(translations={"en": "Test Claim"}),
        tda_assertions=[
            TDAAssertion(
                inverse_evidence=False,
                aggregation_mode="EXISTS",
                concept_description="Concept description that is at least 10 chars.",
            )
        ],
    )
    scale = MatrixScale(
        score=5,
        name=I18nText(translations={"en": "High"}),
        ai_label="HIGH_PERFORMANCE",
        claims=[claim],
    )
    assert scale.score == 5
    assert scale.ai_label == "HIGH_PERFORMANCE"
    assert len(scale.claims) == 1


def test_matrix_row() -> None:
    row = MatrixRow(
        label=I18nText(translations={"en": "Empathy"}),
        ai_description="Evaluate candidate empathy throughout conversation.",
    )
    assert row.label.translations["en"] == "Empathy"
    assert "empathy" in row.ai_description.lower()


def test_tda_assertion_depends_on_list_coercion() -> None:
    edge = CausalEdge(
        tda_id="tda_0123456789abcdef0123456789abcdef",
        source_id="chk_0123456789abcdef",
        edge_reasoning="Causal reason",
    )
    tda = TDAAssertion(
        inverse_evidence=False,
        aggregation_mode="ALL_MUST_COMPLY",
        concept_description="Concept description that is at least 10 chars.",
        depends_on=[edge],  # type: ignore[arg-type]
    )
    assert isinstance(tda.depends_on, tuple)
    assert len(tda.depends_on) == 1


def test_tda_assertion_enforce_pre_flight_requires_anchors() -> None:
    with pytest.raises(ValueError, match="requires at least one syntactic anchor"):
        TDAAssertion(
            inverse_evidence=False,
            aggregation_mode="ALL_MUST_COMPLY",
            concept_description="Concept description that is at least 10 chars.",
            enforce_pre_flight=True,
            syntactic_anchors=[],
        )


def test_tda_assertion_acceptance_criteria_length() -> None:
    with pytest.raises(ValueError, match="must be at least 5 characters long"):
        TDAAssertion(
            inverse_evidence=False,
            aggregation_mode="ALL_MUST_COMPLY",
            concept_description="Concept description that is at least 10 chars.",
            acceptance_criteria=[AcceptanceCriterion(instruction="abc")],
        )


def test_tda_assertion_anti_pattern_length() -> None:
    with pytest.raises(ValueError, match="must be at least 5 characters long"):
        TDAAssertion(
            inverse_evidence=False,
            aggregation_mode="ALL_MUST_COMPLY",
            concept_description="Concept description that is at least 10 chars.",
            anti_patterns=[AntiPattern(pattern="bad")],
        )


def test_tda_assertion_extractive_sensor_validation() -> None:
    # Missing facts
    with pytest.raises(ValueError, match="requires at least one fact"):
        TDAAssertion(
            inverse_evidence=False,
            aggregation_mode="ALL_MUST_COMPLY",
            concept_description="Concept description that is at least 10 chars.",
            evaluation_track="EXTRACTIVE_SENSOR",
            facts_to_find=[],
            logical_expression="fact1 and fact2",
        )

    # Missing logical expression
    with pytest.raises(ValueError, match="requires a defined logical_expression"):
        TDAAssertion(
            inverse_evidence=False,
            aggregation_mode="ALL_MUST_COMPLY",
            concept_description="Concept description that is at least 10 chars.",
            evaluation_track="EXTRACTIVE_SENSOR",
            facts_to_find=["fact1"],
            logical_expression="",
        )

    # Valid extractive sensor
    tda = TDAAssertion(
        inverse_evidence=False,
        aggregation_mode="ALL_MUST_COMPLY",
        concept_description="Concept description that is at least 10 chars.",
        evaluation_track="EXTRACTIVE_SENSOR",
        facts_to_find=["fact1"],
        logical_expression="fact1",
    )
    assert tda.evaluation_track == "EXTRACTIVE_SENSOR"


"""Unit tests for matrix domain models."""

import pytest
from pydantic import ValidationError

from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.matrix import (
    AcceptanceCriterion,
    AntiPattern,
    ContrastivePairDTO,
    FlattenedAtom,
    MatrixClaim,
    MatrixRow,
    MatrixScale,
    TDAAssertion,
    TheoryGrounding,
)
from backend_v2.models.dtos.dag_models import CausalEdge

VALID_TDA_ID = "tda_0195f3a0000070008123456789abcdef"


def test_theory_grounding() -> None:
    """Verifies TheoryGrounding instantiation with source URL and citation reference."""
    tg = TheoryGrounding(source_url="https://example.com/theory", citation_reference="Section 4.2")
    assert tg.source_url == "https://example.com/theory"
    assert tg.citation_reference == "Section 4.2"


def test_contrastive_pair_valid() -> None:
    """Verifies ContrastivePairDTO accepts distinct exemplars meeting minimum length."""
    cp = ContrastivePairDTO(
        acceptable="This is an acceptable exemplar that meets requirements.",
        rejected="This is a rejected exemplar that fails boundaries.",
    )
    assert len(cp.acceptable) >= 10
    assert len(cp.rejected) >= 10


def test_contrastive_pair_identical_invalid_error() -> None:
    """Verifies ContrastivePairDTO rejects identical acceptable and rejected strings."""
    with pytest.raises(ValueError, match="cannot be identical"):
        ContrastivePairDTO(
            acceptable="This is identical text here.",
            rejected="This is identical text here.",
        )


def test_tda_assertion_valid() -> None:
    """Verifies TDAAssertion instantiation with valid criteria, anti-patterns, and causal edges."""
    tda = TDAAssertion(
        tda_id=VALID_TDA_ID,
        inverse_evidence=False,
        aggregation_mode="ALL_MUST_COMPLY",
        facts_to_find=[],
        concept_description="Concept description that is at least 10 chars.",
        acceptance_criteria=[AcceptanceCriterion(instruction="At least five chars long")],
        anti_patterns=[AntiPattern(pattern="Anti pattern five chars")],
        syntactic_anchors=[],
        depends_on=(
            CausalEdge(
                tda_id="tda_0123456789abcdef0123456789abcdef",
                source_id="chk_0195f3a0000070008123456789abcdef",
                edge_reasoning="Causal dependency exists because X implies Y",
            ),
        ),
    )
    assert tda.inverse_evidence is False
    assert tda.aggregation_mode == "ALL_MUST_COMPLY"
    assert len(tda.depends_on) == 1


def test_tda_assertion_inverse_evidence_invalid_mode_error() -> None:
    """Verifies TDAAssertion rejects inverse_evidence=True when aggregation_mode is ALL_MUST_COMPLY."""
    with pytest.raises(ValueError, match="strictly requires 'EXISTS' aggregation mode"):
        TDAAssertion(
            tda_id=VALID_TDA_ID,
            inverse_evidence=True,
            aggregation_mode="ALL_MUST_COMPLY",
            facts_to_find=[],
            concept_description="Concept description that is at least 10 chars.",
            acceptance_criteria=[],
            anti_patterns=[],
            syntactic_anchors=[],
            depends_on=(),
        )


def test_matrix_claim_and_scale() -> None:
    """Verifies MatrixClaim and MatrixScale composition."""
    claim = MatrixClaim(
        label=I18nText(translations={"en": "Test Claim"}),
        tda_assertions=[
            TDAAssertion(
                tda_id=VALID_TDA_ID,
                inverse_evidence=False,
                aggregation_mode="EXISTS",
                facts_to_find=[],
                concept_description="Concept description that is at least 10 chars.",
                acceptance_criteria=[],
                anti_patterns=[],
                syntactic_anchors=[],
                depends_on=(),
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
    """Verifies MatrixRow localized label and AI description fields."""
    row = MatrixRow(
        label=I18nText(translations={"en": "Empathy"}),
        ai_description="Evaluate candidate empathy throughout conversation.",
    )
    assert row.label.translations["en"] == "Empathy"
    assert "empathy" in row.ai_description.lower()


def test_tda_assertion_depends_on_list_coercion() -> None:
    """Verifies _coerce_to_tuple converts JSON list inputs into an immutable tuple on TDAAssertion."""
    edge = CausalEdge(
        tda_id="tda_0123456789abcdef0123456789abcdef",
        source_id="chk_0195f3a0000070008123456789abcdef",
        edge_reasoning="Causal reason",
    )
    tda = TDAAssertion.model_validate_json(
        '{"inverse_evidence": false, "aggregation_mode": "ALL_MUST_COMPLY", '
        '"concept_description": "Concept description that is at least 10 chars.", '
        f'"depends_on": [{edge.model_dump_json()}]}}'
    )
    assert isinstance(tda.depends_on, tuple)
    assert len(tda.depends_on) == 1
    assert tda.tda_id.startswith("tda_")


def test_tda_assertion_enforce_pre_flight_requires_anchors_error() -> None:
    """Verifies enforce_pre_flight=True fails fast when syntactic_anchors is empty."""
    with pytest.raises(ValueError, match="requires at least one syntactic anchor"):
        TDAAssertion(
            tda_id=VALID_TDA_ID,
            inverse_evidence=False,
            aggregation_mode="ALL_MUST_COMPLY",
            facts_to_find=[],
            concept_description="Concept description that is at least 10 chars.",
            acceptance_criteria=[],
            anti_patterns=[],
            enforce_pre_flight=True,
            syntactic_anchors=[],
            depends_on=(),
        )


def test_tda_assertion_acceptance_criteria_length_invalid() -> None:
    """Verifies acceptance_criteria instructions shorter than 5 characters fail validation."""
    with pytest.raises(ValueError, match="must be at least 5 characters long"):
        TDAAssertion(
            tda_id=VALID_TDA_ID,
            inverse_evidence=False,
            aggregation_mode="ALL_MUST_COMPLY",
            facts_to_find=[],
            concept_description="Concept description that is at least 10 chars.",
            acceptance_criteria=[AcceptanceCriterion(instruction="abc")],
            anti_patterns=[],
            syntactic_anchors=[],
            depends_on=(),
        )


def test_tda_assertion_anti_pattern_length_invalid() -> None:
    """Verifies anti_patterns descriptions shorter than 5 characters fail validation."""
    with pytest.raises(ValueError, match="must be at least 5 characters long"):
        TDAAssertion(
            tda_id=VALID_TDA_ID,
            inverse_evidence=False,
            aggregation_mode="ALL_MUST_COMPLY",
            facts_to_find=[],
            concept_description="Concept description that is at least 10 chars.",
            acceptance_criteria=[],
            anti_patterns=[AntiPattern(pattern="bad")],
            syntactic_anchors=[],
            depends_on=(),
        )


def test_tda_assertion_extractive_sensor_validation_error() -> None:
    """Verifies EXTRACTIVE_SENSOR track requires non-empty facts_to_find and logical_expression."""
    with pytest.raises(ValueError, match="requires at least one fact"):
        TDAAssertion(
            tda_id=VALID_TDA_ID,
            inverse_evidence=False,
            aggregation_mode="ALL_MUST_COMPLY",
            concept_description="Concept description that is at least 10 chars.",
            evaluation_track="EXTRACTIVE_SENSOR",
            facts_to_find=[],
            logical_expression="fact1 and fact2",
            acceptance_criteria=[],
            anti_patterns=[],
            syntactic_anchors=[],
            depends_on=(),
        )

    with pytest.raises(ValueError, match="requires a defined logical_expression"):
        TDAAssertion(
            tda_id=VALID_TDA_ID,
            inverse_evidence=False,
            aggregation_mode="ALL_MUST_COMPLY",
            concept_description="Concept description that is at least 10 chars.",
            evaluation_track="EXTRACTIVE_SENSOR",
            facts_to_find=["fact1"],
            logical_expression="",
            acceptance_criteria=[],
            anti_patterns=[],
            syntactic_anchors=[],
            depends_on=(),
        )

    tda = TDAAssertion(
        tda_id=VALID_TDA_ID,
        inverse_evidence=False,
        aggregation_mode="ALL_MUST_COMPLY",
        concept_description="Concept description that is at least 10 chars.",
        evaluation_track="EXTRACTIVE_SENSOR",
        facts_to_find=["fact1"],
        logical_expression="fact1",
        acceptance_criteria=[],
        anti_patterns=[],
        syntactic_anchors=[],
        depends_on=(),
    )
    assert tda.evaluation_track == "EXTRACTIVE_SENSOR"


def test_flattened_atom_v2_core_base_inheritance_and_whitespace_stripping() -> None:
    """Verifies FlattenedAtom inherits V2CoreBase, strips whitespace, and rejects extra fields."""
    from backend_v2.models.core_base import V2CoreBase

    assert issubclass(FlattenedAtom, V2CoreBase)

    atom = FlattenedAtom(
        atom_id="  atm_0195f3a0000070008123456789abcdef  ",
        question="  Does the candidate explain X?  ",
        depends_on=(),
        acceptance_criteria=(),
        anti_patterns=(),
        syntactic_anchors=(),
    )
    assert atom.atom_id == "atm_0195f3a0000070008123456789abcdef"
    assert atom.question == "Does the candidate explain X?"

    with pytest.raises(ValidationError):
        FlattenedAtom.model_validate(
            {
                "atom_id": "atm_1",
                "question": "question",
                "unauthorized_extra": "fail",
            }
        )


def test_matrix_istqb_boundary_value_invalid_partitions() -> None:
    """Verifies ISTQB Boundary Value Analysis (min-1 vs min) and invalid ID patterns."""
    with pytest.raises(ValidationError):
        ContrastivePairDTO(acceptable="123456789", rejected="1234567890")
    with pytest.raises(ValidationError):
        ContrastivePairDTO(acceptable="1234567890", rejected="123456789")
    cp_min = ContrastivePairDTO(acceptable="1234567890", rejected="0987654321")
    assert len(cp_min.acceptable) == 10
    assert len(cp_min.rejected) == 10

    with pytest.raises(ValidationError):
        TDAAssertion(
            tda_id=VALID_TDA_ID,
            inverse_evidence=False,
            aggregation_mode="EXISTS",
            facts_to_find=[],
            concept_description="123456789",
            acceptance_criteria=[],
            anti_patterns=[],
            syntactic_anchors=[],
            depends_on=(),
        )
    tda_min = TDAAssertion(
        tda_id=VALID_TDA_ID,
        inverse_evidence=False,
        aggregation_mode="EXISTS",
        facts_to_find=[],
        concept_description="1234567890",
        acceptance_criteria=[AcceptanceCriterion(instruction="12345")],
        anti_patterns=[AntiPattern(pattern="12345")],
        syntactic_anchors=[],
        depends_on=(),
    )
    assert len(tda_min.concept_description) == 10

    with pytest.raises(ValidationError, match="must be at least 5 characters long"):
        TDAAssertion(
            tda_id=VALID_TDA_ID,
            inverse_evidence=False,
            aggregation_mode="EXISTS",
            facts_to_find=[],
            concept_description="1234567890",
            acceptance_criteria=[AcceptanceCriterion(instruction="1234")],
            anti_patterns=[],
            syntactic_anchors=[],
            depends_on=(),
        )
    with pytest.raises(ValidationError, match="must be at least 5 characters long"):
        TDAAssertion(
            tda_id=VALID_TDA_ID,
            inverse_evidence=False,
            aggregation_mode="EXISTS",
            facts_to_find=[],
            concept_description="1234567890",
            acceptance_criteria=[],
            anti_patterns=[AntiPattern(pattern="1234")],
            syntactic_anchors=[],
            depends_on=(),
        )

    with pytest.raises(ValidationError):
        TDAAssertion(
            tda_id="tda_short",
            inverse_evidence=False,
            aggregation_mode="EXISTS",
            facts_to_find=[],
            concept_description="1234567890",
            acceptance_criteria=[],
            anti_patterns=[],
            syntactic_anchors=[],
            depends_on=(),
        )

    with pytest.raises(ValidationError):
        MatrixClaim(
            label=I18nText(translations={"en": "Claim"}),
            tda_assertions=[],
        )

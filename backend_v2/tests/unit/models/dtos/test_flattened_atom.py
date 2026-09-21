"""Unit tests for FlattenedAtom DTO."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.matrix import AcceptanceCriterion, AntiPattern, ContrastivePairDTO
from backend_v2.models.dtos.dag_models import CausalEdge
from backend_v2.models.dtos.flattened_atom import FlattenedAtom, _coerce_to_tuple
from backend_v2.models.enums import TargetSpeaker


def test_coerce_to_tuple() -> None:
    """Test helper _coerce_to_tuple converts lists and leaves other types intact."""
    assert _coerce_to_tuple([1, 2, 3]) == (1, 2, 3)
    assert _coerce_to_tuple((1, 2, 3)) == (1, 2, 3)
    assert _coerce_to_tuple("string") == "string"


def test_flattened_atom_valid_creation() -> None:
    """Test valid creation of FlattenedAtom with defaults."""
    atom = FlattenedAtom(
        atom_id="tda_123",
        question="Is this claim valid?",
        extraction_rule="Extract exact quote.",
        anchor_target="Section 1",
        is_inverse=False,
    )
    assert atom.atom_id == "tda_123"
    assert atom.question == "Is this claim valid?"
    assert atom.extraction_rule == "Extract exact quote."
    assert atom.anchor_target == "Section 1"
    assert atom.is_inverse is False
    assert atom.depends_on == ()
    assert atom.contrastive_example is None
    assert atom.acceptance_criteria == ()
    assert atom.anti_patterns == ()
    assert atom.syntactic_anchors == ()
    assert atom.target_speaker == TargetSpeaker.USER


def test_flattened_atom_coerces_lists_to_tuples() -> None:
    """Test that list fields are coerced to immutable tuples."""
    edge = CausalEdge(
        edge_reasoning="Parent verification required for child assertion",
        tda_id="tda_1",
        source_id="chk_1",
    )
    criterion = AcceptanceCriterion(instruction="Valid quote")
    anti = AntiPattern(pattern="speculation")
    contrastive = ContrastivePairDTO(
        acceptable="Valid phrase with minimum ten chars", rejected="Bad phrase with minimum ten chars"
    )

    atom = FlattenedAtom(
        atom_id="tda_123",
        question="Question",
        depends_on=[edge],  # type: ignore[arg-type]
        contrastive_example=contrastive,
        acceptance_criteria=[criterion],  # type: ignore[arg-type]
        anti_patterns=[anti],  # type: ignore[arg-type]
        syntactic_anchors=["anchor1", "anchor2"],  # type: ignore[arg-type]
        target_speaker=TargetSpeaker.AI,
    )
    assert isinstance(atom.depends_on, tuple)
    assert len(atom.depends_on) == 1
    assert isinstance(atom.acceptance_criteria, tuple)
    assert len(atom.acceptance_criteria) == 1
    assert isinstance(atom.anti_patterns, tuple)
    assert len(atom.anti_patterns) == 1
    assert isinstance(atom.syntactic_anchors, tuple)
    assert atom.syntactic_anchors == ("anchor1", "anchor2")
    assert atom.target_speaker == TargetSpeaker.AI


def test_flattened_atom_forbids_extra_fields() -> None:
    """Test that extra fields are forbidden."""
    with pytest.raises(ValidationError):
        FlattenedAtom.model_validate({"atom_id": "tda_1", "question": "Q", "extra_field": 123})


def test_flattened_atom_is_frozen() -> None:
    """Test that FlattenedAtom instances are immutable."""
    atom = FlattenedAtom(atom_id="tda_1", question="Q")
    with pytest.raises(ValidationError):
        atom.question = "New Q"  # type: ignore[misc]

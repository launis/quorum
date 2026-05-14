import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.lightweight_matrix import (
    AtomEvaluationItemDTO,
    LightweightMatrixOutput,
    OutputProfileConfig,
)
from backend_v2.models.enums import XaiExtensionType


def test_output_profile_config_strictness() -> None:
    """Test OutputProfileConfig enforces Fail-Fast constraints."""
    config = OutputProfileConfig(visible_extensions=[XaiExtensionType.CITATION])
    assert XaiExtensionType.CITATION in config.visible_extensions

    # Test strictness / forbid extra
    with pytest.raises(ValidationError):
        OutputProfileConfig(
            visible_extensions=[XaiExtensionType.CITATION],
            extra_field="should_fail",  # type: ignore
        )

    # Test mutability (frozen=True)
    with pytest.raises(ValidationError):
        config.visible_extensions = []  # type: ignore


def test_lightweight_matrix_output_strictness() -> None:
    """Test LightweightMatrixOutput enforces Fail-Fast logic."""
    output = LightweightMatrixOutput(
        raw_score=45.5,
        normalized_score=90.0,
        level_breakdown={"level1": {"A": 1}},
        justification="Perfect score",
        evaluated_atoms={"atom1": True},
        extensions={XaiExtensionType.CITATION: "Some quote"},
    )
    assert output.normalized_score == 90.0
    assert output.extensions[XaiExtensionType.CITATION] == "Some quote"

    # Test normalized_score bounds (ge=0.0, le=100.0)
    with pytest.raises(ValidationError) as exc:
        LightweightMatrixOutput(
            raw_score=150.0,
            normalized_score=150.0,  # Fails le=100.0
            level_breakdown={},
            justification="Too high",
            evaluated_atoms={},
            extensions={},
        )
    assert "Input should be less than or equal to 100" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        LightweightMatrixOutput(
            raw_score=-10.0,
            normalized_score=-10.0,  # Fails ge=0.0
            level_breakdown={},
            justification="Too low",
            evaluated_atoms={},
            extensions={},
        )
    assert "Input should be greater than or equal to 0" in str(exc.value)

    # Test forbid extra
    with pytest.raises(ValidationError):
        LightweightMatrixOutput(
            raw_score=50.0,
            normalized_score=50.0,
            justification="Valid",
            evaluated_atoms={},
            extensions={},
            invalid_duck="quack",  # type: ignore
        )


def test_atom_evaluation_item_dto_strictness() -> None:
    """Test AtomEvaluationItemDTO enforces strict validation and V4.3 Blacklist."""
    item = AtomEvaluationItemDTO(
        atom_id="atom_123",
        mechanical_trace="Because logic.",
        exact_quote="Some valid quote",
    )
    assert item.atom_id == "atom_123"
    assert item.evidence_found is True
    assert item.calculate_rule_satisfied(inverse_evidence=False) is True

    # Test forbid extra
    with pytest.raises(ValidationError):
        AtomEvaluationItemDTO(
            atom_id="atom_123",
            mechanical_trace="Logic",
            exact_quote="Quote",
            extra="not allowed",  # type: ignore
        )

    # Test V4.3 Phantom Boolean Sanity Check
    phantom = AtomEvaluationItemDTO(
        atom_id="atom_phantom",
        mechanical_trace="Logic.",
        exact_quote="Not found",
    )
    assert phantom.evidence_found is False

    # Test inverse evidence logic
    assert phantom.calculate_rule_satisfied(inverse_evidence=True) is True
    assert phantom.calculate_rule_satisfied(inverse_evidence=False) is False

"""Tests for Lightweight Matrix DTO."""

from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
from backend_v2.models.enums import XaiExtensionType
from pydantic import ValidationError
import pytest


def test_lightweight_matrix_initialization() -> None:
    """Ensure strict Pydantic V2 instantiation works correctly."""
    data = LightweightMatrixOutput(
        normalized_score=0.8,
        level_breakdown="Good",
        justification="Hyvä",
        evaluated_atoms={"atom_1": True},
        extensions={XaiExtensionType.JUSTIFICATION: "Data"}
    )
    assert data.normalized_score == 0.8


def test_lightweight_matrix_score_bounds() -> None:
    """Ensure score strictly adheres to ge=0.0 and le=1.0 bounds."""
    # Test over max
    with pytest.raises(ValidationError) as exc_high:
        LightweightMatrixOutput(
            normalized_score=1.5,
            level_breakdown="Good",
            justification="Hyvä",
            evaluated_atoms={"atom_1": True},
            extensions={XaiExtensionType.JUSTIFICATION: "Data"}
        )
    assert "Input should be less than or equal to 1" in str(exc_high.value)

    # Test below min
    with pytest.raises(ValidationError) as exc_low:
        LightweightMatrixOutput(
            normalized_score=-0.1,
            level_breakdown="Good",
            justification="Hyvä",
            evaluated_atoms={"atom_1": True},
            extensions={XaiExtensionType.JUSTIFICATION: "Data"}
        )
    assert "Input should be greater than or equal to 0" in str(exc_low.value)


def test_lightweight_matrix_forbids_extra() -> None:
    """Ensure extra='forbid' strictly rejects unknown fields."""
    with pytest.raises(ValidationError) as exc:
        LightweightMatrixOutput(
            normalized_score=0.5,
            level_breakdown="Good",
            justification="Hyvä",
            evaluated_atoms={"atom_1": True},
            extensions={XaiExtensionType.JUSTIFICATION: "Data"},
            random_injection="hax"
        )
    assert "Extra inputs are not permitted" in str(exc.value)

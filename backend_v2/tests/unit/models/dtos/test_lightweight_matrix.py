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

    # Test status-based inverse evidence logic
    pass_item = AtomEvaluationItemDTO(
        atom_id="atom_pass",
        mechanical_trace="Logic.",
        exact_quote="Found",
        status="PASS",
    )
    assert pass_item.calculate_rule_satisfied(inverse_evidence=True) is False
    assert pass_item.calculate_rule_satisfied(inverse_evidence=False) is True

    fail_item = AtomEvaluationItemDTO(
        atom_id="atom_fail",
        mechanical_trace="Logic.",
        exact_quote="None",
        status="FAIL",
    )
    assert fail_item.calculate_rule_satisfied(inverse_evidence=True) is True
    assert fail_item.calculate_rule_satisfied(inverse_evidence=False) is False


def test_atom_evaluation_item_dto_rejects_nulls() -> None:
    """Test that null values for strict string fields raise ValidationError (caught by ChunkAccumulator)."""
    raw_data = {
        "atom_id": "atom_null_test",
        "mechanical_trace": None,
        "exact_quote": None,
        "pre_quote_anchor": None,
        "post_quote_anchor": None,
    }
    with pytest.raises(ValidationError):
        AtomEvaluationItemDTO.model_validate(raw_data)


def test_map_llm_extensions_with_base_tda_extraction_keys() -> None:
    """Test that Phase 4 BaseTDAExtraction fields map without raising extra_forbidden errors."""
    raw_data = {
        "raw_score": 50.0,
        "normalized_score": 50.0,
        "localized_anchors_found": ["avainsana1", "avainsana2"],
        "semantic_reasoning": "Käyttäjä ohjasi aktiivisesti...",
        "step_2_mitigating_context": "Prosessi alkoi...",
        "contextual_override": False,
        "exact_quote": "Megatrendien Kooste...",
    }

    mapped = LightweightMatrixOutput.map_llm_extensions_to_domain(raw_data)

    # This will fail with 'Extra inputs are not permitted' if the mapping doesn't strip the BaseTDA fields
    LightweightMatrixOutput.model_validate(mapped)

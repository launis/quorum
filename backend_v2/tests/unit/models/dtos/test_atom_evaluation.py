import pytest
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import ValidationError

from backend_v2.models.dtos.atom_evaluation import (
    EvaluatedMatrixRefDTO,
    LightweightMatrixDTO,
    RawXAIExtensionDTO,
    ReasoningStepDTO,
    ReducedAtomDTO,
)
from backend_v2.models.enums import ExecutionStatus


class ReasoningStepDTOFactory(ModelFactory[ReasoningStepDTO]):
    __model__ = ReasoningStepDTO


class ReducedAtomDTOFactory(ModelFactory[ReducedAtomDTO]):
    __model__ = ReducedAtomDTO


class LightweightMatrixDTOFactory(ModelFactory[LightweightMatrixDTO]):
    __model__ = LightweightMatrixDTO


def test_reasoning_step_dto_validation() -> None:
    dto = ReasoningStepDTOFactory.build()
    assert isinstance(dto.step_1_identify_premise, str)
    assert isinstance(dto.step_2_scan_source, str)
    assert isinstance(dto.step_3_evaluate_anti_patterns, str)
    assert isinstance(dto.step_4_final_conclusion, str)


def test_reduced_atom_dto_validation() -> None:
    dto = ReducedAtomDTOFactory.build(status=ExecutionStatus.PASSED)
    assert isinstance(dto.tda_id, str)
    assert dto.status == ExecutionStatus.PASSED


def test_reduced_atom_dto_source_quotes_tuple() -> None:
    """Verify ReducedAtomDTO preserves source_quotes as tuple."""
    dto = ReducedAtomDTO(
        tda_id="tda_123",
        status=ExecutionStatus.PASSED,
        source_quotes=("Segment 1 with sufficient length.", "Segment 2 with sufficient length."),
    )
    assert dto.source_quotes == ("Segment 1 with sufficient length.", "Segment 2 with sufficient length.")
    dumped = dto.model_dump(mode="json")
    loaded = ReducedAtomDTO.model_validate(dumped)
    assert loaded.source_quotes == ("Segment 1 with sufficient length.", "Segment 2 with sufficient length.")


def test_lightweight_matrix_dto_validation() -> None:
    dto = LightweightMatrixDTOFactory.build()
    assert isinstance(dto.execution_id, str)
    assert isinstance(dto.reduced_atoms, list)
    assert type(dto.global_metrics) is dict
    assert isinstance(dto.evaluated_matrices, list)
    assert isinstance(dto.raw_extensions, list)


def test_evaluated_matrix_ref_dto_roundtrip() -> None:
    """Verify EvaluatedMatrixRefDTO roundtrip serialization with 100% fidelity."""
    ref = EvaluatedMatrixRefDTO(matrix_id="mat_1", score=4.5, display_name="Governance Matrix")
    dumped = ref.model_dump(mode="json")
    loaded = EvaluatedMatrixRefDTO.model_validate(dumped)
    assert loaded == ref
    assert loaded.matrix_id == "mat_1"
    assert loaded.score == 4.5
    assert loaded.display_name == "Governance Matrix"


def test_evaluated_matrix_ref_dto_rejects_extra() -> None:
    """Verify EvaluatedMatrixRefDTO extra fields are forbidden."""
    with pytest.raises(ValidationError):
        EvaluatedMatrixRefDTO.model_validate({"matrix_id": "mat_1", "extra_field": "bad"})


def test_evaluated_matrix_ref_dto_rejects_missing_matrix_id() -> None:
    """Verify EvaluatedMatrixRefDTO rejects missing required matrix_id."""
    with pytest.raises(ValidationError):
        EvaluatedMatrixRefDTO.model_validate({"score": 4.5})


def test_raw_xai_extension_dto_validation() -> None:
    """Verify RawXAIExtensionDTO serialization and validation."""
    ext = RawXAIExtensionDTO(
        id="ext_1",
        type="coaching",
        citation="Quote",
        risk_flag=True,
        raw_payload={"custom": 123},
    )
    dumped = ext.model_dump(mode="json")
    loaded = RawXAIExtensionDTO.model_validate(dumped)
    assert loaded == ext
    assert loaded.id == "ext_1"
    assert loaded.risk_flag is True


def test_raw_xai_extension_dto_rejects_extra() -> None:
    """Verify RawXAIExtensionDTO extra fields are forbidden."""
    with pytest.raises(ValidationError):
        RawXAIExtensionDTO.model_validate({"id": "ext_1", "forbidden_prop": 999})


def test_raw_xai_extension_dto_rejects_invalid_confidence_type() -> None:
    """Verify RawXAIExtensionDTO strict validation rejects non-float confidence."""
    with pytest.raises(ValidationError):
        RawXAIExtensionDTO.model_validate({"id": "ext_1", "confidence": "not-a-float"})


def test_reasoning_step_dto_rejects_extra() -> None:
    """Verify ReasoningStepDTO rejects unexpected extra fields."""
    with pytest.raises(ValidationError):
        ReasoningStepDTO.model_validate(
            {
                "step_1_identify_premise": "Premise",
                "step_2_scan_source": "Source",
                "step_3_evaluate_anti_patterns": "None",
                "step_4_final_conclusion": "Conclusion",
                "unauthorized_field": "illegal",
            }
        )


def test_reasoning_step_dto_rejects_missing_required() -> None:
    """Verify ReasoningStepDTO rejects missing required premise."""
    with pytest.raises(ValidationError):
        ReasoningStepDTO.model_validate(
            {
                "step_2_scan_source": "Source",
                "step_3_evaluate_anti_patterns": "None",
                "step_4_final_conclusion": "Conclusion",
            }
        )


def test_reduced_atom_dto_rejects_extra() -> None:
    """Verify ReducedAtomDTO rejects unauthorized extra fields."""
    with pytest.raises(ValidationError):
        ReducedAtomDTO.model_validate(
            {
                "tda_id": "atm_1",
                "status": "PASSED",
                "unexpected_prop": "error",
            }
        )


def test_reduced_atom_dto_rejects_invalid_status() -> None:
    """Verify ReducedAtomDTO rejects unknown execution status."""
    with pytest.raises(ValidationError):
        ReducedAtomDTO.model_validate(
            {
                "tda_id": "atm_1",
                "status": "NON_EXISTENT_STATUS",
            }
        )


def test_lightweight_matrix_dto_rejects_extra() -> None:
    """Verify LightweightMatrixDTO rejects unauthorized extra fields."""
    with pytest.raises(ValidationError):
        LightweightMatrixDTO.model_validate(
            {
                "execution_id": "exe_1",
                "reduced_atoms": [],
                "global_metrics": {},
                "extra_key": "forbidden",
            }
        )


def test_lightweight_matrix_dto_rejects_missing_execution_id() -> None:
    """Verify LightweightMatrixDTO rejects missing execution_id."""
    with pytest.raises(ValidationError):
        LightweightMatrixDTO.model_validate(
            {
                "reduced_atoms": [],
                "global_metrics": {},
            }
        )

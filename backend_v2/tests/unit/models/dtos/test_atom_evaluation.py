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

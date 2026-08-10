from polyfactory.factories.pydantic_factory import ModelFactory

from backend_v2.models.dtos.atom_evaluation import (
    LightweightMatrixDTO,
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
    assert isinstance(dto.global_metrics, dict)
    assert isinstance(dto.raw_extensions, list)

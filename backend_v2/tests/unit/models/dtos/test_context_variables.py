"""Unit tests for ContextVariablesDTO."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.blackboard import GlobalAtomBlackboard
from backend_v2.models.dtos.context_variables import ContextVariablesDTO
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput


def test_context_variables_dto_defaults() -> None:
    """Test default initialization has expected empty attributes."""
    dto = ContextVariablesDTO()
    assert dto.global_atom_blackboard is None
    assert dto.matrix_reducer_output is None
    assert dto.report_context is None
    assert dto.step_detector is None
    assert dto.evaluated_matrices is None
    assert dto.variables == {}
    assert dto.to_dict() == {}


def test_context_variables_dto_with_update() -> None:
    """Test with_update creates an updated immutable instance."""
    bb = GlobalAtomBlackboard(atoms_by_input={})
    matrix_out = LightweightMatrixOutput(raw_score=100.0, normalized_score=100.0)
    dto = ContextVariablesDTO()
    updated = dto.with_update(
        __GLOBAL_ATOM_BLACKBOARD__=bb,
        __MATRIX_REDUCER_OUTPUT__=matrix_out,
        report_context={"summary": "ok"},
        step_detector={"detected": "true"},
        evaluated_matrices={"mat1": 5.0},
        custom_var="custom_val",
    )

    assert updated.global_atom_blackboard == bb
    assert updated.matrix_reducer_output == matrix_out
    assert updated.report_context == {"summary": "ok"}
    assert updated.step_detector == {"detected": "true"}
    assert updated.evaluated_matrices == {"mat1": 5.0}
    assert updated.variables == {"custom_var": "custom_val"}

    # Immutability
    with pytest.raises(ValidationError):
        updated.variables = {}  # type: ignore[misc]


def test_context_variables_dto_serialization_and_deserialization() -> None:
    """Test to_dict and from_dict roundtrip operations."""
    bb = GlobalAtomBlackboard(atoms_by_input={})
    matrix_out = LightweightMatrixOutput(raw_score=80.0, normalized_score=80.0)
    data = {
        "__GLOBAL_ATOM_BLACKBOARD__": bb.model_dump(mode="json"),
        "__MATRIX_REDUCER_OUTPUT__": matrix_out.model_dump(mode="json"),
        "report_context": {"context": "text"},
        "step_detector": {"status": "ok"},
        "evaluated_matrices": {"m": 1.0},
        "dyn_key": "dyn_val",
        "variables": {"nested_k": "nested_v"},
    }
    dto = ContextVariablesDTO.from_dict(data)
    assert dto.global_atom_blackboard == bb
    assert dto.matrix_reducer_output == matrix_out
    exported = dto.to_dict()
    assert exported["__GLOBAL_ATOM_BLACKBOARD__"] == bb
    assert exported["__MATRIX_REDUCER_OUTPUT__"] == matrix_out
    assert exported["report_context"] == {"context": "text"}
    assert exported["step_detector"] == {"status": "ok"}
    assert exported["evaluated_matrices"] == {"m": 1.0}
    assert exported["dyn_key"] == "dyn_val"

    # Test empty / None handling
    empty_dto = ContextVariablesDTO.from_dict(None)
    assert empty_dto.variables == {}
    assert empty_dto.global_atom_blackboard is None


def test_context_variables_dto_subscript_and_contains() -> None:
    """Test subscript indexing and membership checking."""
    bb = GlobalAtomBlackboard(atoms_by_input={})
    matrix_out = LightweightMatrixOutput(raw_score=80.0, normalized_score=80.0)
    dto = ContextVariablesDTO(
        global_atom_blackboard=bb,
        matrix_reducer_output=matrix_out,
        report_context={"rc": "3"},
        step_detector={"sd": "4"},
        evaluated_matrices={"em": 5.0},
        variables={"var_k": "var_v"},
    )

    assert dto["__GLOBAL_ATOM_BLACKBOARD__"] == bb
    assert dto["global_atom_blackboard"] == bb
    assert dto["__MATRIX_REDUCER_OUTPUT__"] == matrix_out
    assert dto["matrix_reducer_output"] == matrix_out
    assert dto["report_context"] == {"rc": "3"}
    assert dto["step_detector"] == {"sd": "4"}
    assert dto["evaluated_matrices"] == {"em": 5.0}
    assert dto["var_k"] == "var_v"

    with pytest.raises(KeyError):
        _ = dto["nonexistent"]

    assert "__GLOBAL_ATOM_BLACKBOARD__" in dto
    assert "global_atom_blackboard" in dto
    assert "__MATRIX_REDUCER_OUTPUT__" in dto
    assert "report_context" in dto
    assert "step_detector" in dto
    assert "evaluated_matrices" in dto
    assert "var_k" in dto
    assert "missing" not in dto
    assert (123 in dto) is False

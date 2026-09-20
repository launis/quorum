"""Unit tests for ContextVariablesDTO."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.context_variables import ContextVariablesDTO


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
    dto = ContextVariablesDTO()
    updated = dto.with_update(
        __GLOBAL_ATOM_BLACKBOARD__={"atoms": ["a1"]},
        __MATRIX_REDUCER_OUTPUT__={"score": 100},
        report_context={"summary": "ok"},
        step_detector={"detected": True},
        evaluated_matrices={"mat1": 5},
        custom_var="custom_val",
    )

    assert updated.global_atom_blackboard == {"atoms": ["a1"]}
    assert updated.matrix_reducer_output == {"score": 100}
    assert updated.report_context == {"summary": "ok"}
    assert updated.step_detector == {"detected": True}
    assert updated.evaluated_matrices == {"mat1": 5}
    assert updated.variables == {"custom_var": "custom_val"}

    # Immutability
    with pytest.raises(ValidationError):
        updated.variables = {}  # type: ignore[misc]


def test_context_variables_dto_serialization_and_deserialization() -> None:
    """Test to_dict and from_dict roundtrip operations."""
    data = {
        "__GLOBAL_ATOM_BLACKBOARD__": {"atoms": ["a1"]},
        "__MATRIX_REDUCER_OUTPUT__": {"score": 80},
        "report_context": {"context": "text"},
        "step_detector": {"status": "ok"},
        "evaluated_matrices": {"m": 1},
        "dyn_key": "dyn_val",
        "variables": {"nested_k": "nested_v"},
    }
    dto = ContextVariablesDTO.from_dict(data)
    assert dto.global_atom_blackboard == {"atoms": ["a1"]}
    assert dto.matrix_reducer_output == {"score": 80}
    exported = dto.to_dict()
    assert exported["__GLOBAL_ATOM_BLACKBOARD__"] == {"atoms": ["a1"]}
    assert exported["__MATRIX_REDUCER_OUTPUT__"] == {"score": 80}
    assert exported["report_context"] == {"context": "text"}
    assert exported["step_detector"] == {"status": "ok"}
    assert exported["evaluated_matrices"] == {"m": 1}
    assert exported["dyn_key"] == "dyn_val"

    # Test empty / None handling
    empty_dto = ContextVariablesDTO.from_dict(None)
    assert empty_dto.variables == {}
    assert empty_dto.global_atom_blackboard is None


def test_context_variables_dto_subscript_and_contains() -> None:
    """Test subscript indexing and membership checking."""
    dto = ContextVariablesDTO(
        global_atom_blackboard={"bb": 1},
        matrix_reducer_output={"red": 2},
        report_context={"rc": 3},
        step_detector={"sd": 4},
        evaluated_matrices={"em": 5},
        variables={"var_k": "var_v"},
    )

    assert dto["__GLOBAL_ATOM_BLACKBOARD__"] == {"bb": 1}
    assert dto["global_atom_blackboard"] == {"bb": 1}
    assert dto["__MATRIX_REDUCER_OUTPUT__"] == {"red": 2}
    assert dto["matrix_reducer_output"] == {"red": 2}
    assert dto["report_context"] == {"rc": 3}
    assert dto["step_detector"] == {"sd": 4}
    assert dto["evaluated_matrices"] == {"em": 5}
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

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
    assert len(dto) == 0
    assert list(dto.keys()) == []
    assert list(dto.items()) == []
    assert list(dto.values()) == []


def test_context_variables_dto_with_update() -> None:
    """Test with_update creates an updated immutable instance."""
    bb = GlobalAtomBlackboard(atoms_by_input={})
    matrix_out = LightweightMatrixOutput(raw_score=100.0, normalized_score=100.0)
    dto = ContextVariablesDTO()
    updated = dto.with_update(
        __GLOBAL_ATOM_BLACKBOARD__=bb,
        __MATRIX_REDUCER_OUTPUT__=matrix_out,
        report_context="summary text",
        step_detector="detected",
        evaluated_matrices={"mat1": 5.0},
        custom_var="custom_val",
    )

    assert updated.global_atom_blackboard == bb
    assert updated.matrix_reducer_output == matrix_out
    assert updated.report_context == "summary text"
    assert updated.step_detector == "detected"
    assert updated.evaluated_matrices == {"mat1": 5.0}
    assert updated.variables == {"custom_var": "custom_val"}

    # Immutability
    with pytest.raises(ValidationError):
        updated.variables = {}  # type: ignore[misc]


def test_context_variables_dto_serialization_and_deserialization() -> None:
    """Test Pydantic model_dump and model_validate roundtrip operations."""
    bb = GlobalAtomBlackboard(atoms_by_input={})
    matrix_out = LightweightMatrixOutput(raw_score=80.0, normalized_score=80.0)
    dto = ContextVariablesDTO(
        global_atom_blackboard=bb,
        matrix_reducer_output=matrix_out,
        report_context="rc",
        step_detector="sd",
        evaluated_matrices={"m": 1.0},
        variables={"dyn_key": "dyn_val"},
    )
    dumped = dto.model_dump(mode="json")
    rehydrated = ContextVariablesDTO.model_validate(dumped)
    assert rehydrated == dto
    assert rehydrated["global_atom_blackboard"] == bb
    assert rehydrated["dyn_key"] == "dyn_val"

    empty_dto = ContextVariablesDTO.empty()
    assert empty_dto.variables == {}
    assert empty_dto.global_atom_blackboard is None


def test_context_variables_dto_forbids_extra_keys_fail_fast() -> None:
    """Negative test: unmapped or flat keys passed to ContextVariablesDTO raise ValidationError under extra='forbid'."""
    with pytest.raises(ValidationError):
        ContextVariablesDTO.model_validate({
            "unmapped_flat_key": "some_value",
        })


def test_context_variables_dto_subscript_and_contains() -> None:
    """Test subscript indexing and membership checking."""
    bb = GlobalAtomBlackboard(atoms_by_input={})
    matrix_out = LightweightMatrixOutput(raw_score=80.0, normalized_score=80.0)
    dto = ContextVariablesDTO(
        global_atom_blackboard=bb,
        matrix_reducer_output=matrix_out,
        report_context="rc_text",
        step_detector="sd_text",
        evaluated_matrices={"em_key": 2.5},
        variables={"var_k": "var_v"},
    )

    assert dto["__GLOBAL_ATOM_BLACKBOARD__"] == bb
    assert dto["global_atom_blackboard"] == bb
    assert dto["__MATRIX_REDUCER_OUTPUT__"] == matrix_out
    assert dto["matrix_reducer_output"] == matrix_out
    assert dto["report_context"] == "rc_text"
    assert dto["step_detector"] == "sd_text"
    assert dto["evaluated_matrices"] == {"em_key": 2.5}
    assert dto["var_k"] == "var_v"

    with pytest.raises(KeyError):
        _ = dto["nonexistent"]

    assert "__GLOBAL_ATOM_BLACKBOARD__" in dto
    assert "global_atom_blackboard" in dto
    assert "__MATRIX_REDUCER_OUTPUT__" in dto
    assert "matrix_reducer_output" in dto
    assert "report_context" in dto
    assert "step_detector" in dto
    assert "evaluated_matrices" in dto
    assert "var_k" in dto
    assert "missing" not in dto
    assert (123 in dto) is False


def test_context_variables_dto_mapping_protocol_all_fields() -> None:
    """Test collections.abc.Mapping compliance with all known fields and variables populated."""
    bb = GlobalAtomBlackboard(atoms_by_input={})
    matrix_out = LightweightMatrixOutput(raw_score=90.0, normalized_score=90.0)
    dto = ContextVariablesDTO(
        global_atom_blackboard=bb,
        matrix_reducer_output=matrix_out,
        report_context="report",
        step_detector="detector",
        evaluated_matrices={"score": 4.0},
        variables={"k1": "v1", "k2": "v2"},
    )
    # Keys: __GLOBAL_ATOM_BLACKBOARD__, global_atom_blackboard, __MATRIX_REDUCER_OUTPUT__, matrix_reducer_output,
    # report_context, step_detector, evaluated_matrices, k1, k2 -> 9 keys
    assert len(dto) == 9
    assert len(list(dto.keys())) == 9
    assert len(list(dto.values())) == 9
    assert len(list(dto.items())) == 9


def test_context_variables_dto_subscript_absent_known_fields_raise_keyerror() -> None:
    """Test that accessing known fields when None and not in variables raises KeyError."""
    dto = ContextVariablesDTO()
    with pytest.raises(KeyError):
        _ = dto["__GLOBAL_ATOM_BLACKBOARD__"]
    with pytest.raises(KeyError):
        _ = dto["global_atom_blackboard"]
    with pytest.raises(KeyError):
        _ = dto["__MATRIX_REDUCER_OUTPUT__"]
    with pytest.raises(KeyError):
        _ = dto["matrix_reducer_output"]
    with pytest.raises(KeyError):
        _ = dto["report_context"]
    with pytest.raises(KeyError):
        _ = dto["step_detector"]
    with pytest.raises(KeyError):
        _ = dto["evaluated_matrices"]


def test_context_variables_dto_subscript_fallback_to_variables_for_known_names() -> None:
    """Test accessing known field names when root is None but key is present in variables."""
    dto = ContextVariablesDTO(
        variables={
            "__GLOBAL_ATOM_BLACKBOARD__": "bb_in_var",
            "global_atom_blackboard": "bb_in_var2",
            "__MATRIX_REDUCER_OUTPUT__": "mat_in_var",
            "matrix_reducer_output": "mat_in_var2",
            "report_context": "rep_in_var",
            "step_detector": "step_in_var",
            "evaluated_matrices": "ev_in_var",
        }
    )
    assert dto["__GLOBAL_ATOM_BLACKBOARD__"] == "bb_in_var"
    assert dto["global_atom_blackboard"] == "bb_in_var2"
    assert dto["__MATRIX_REDUCER_OUTPUT__"] == "mat_in_var"
    assert dto["matrix_reducer_output"] == "mat_in_var2"
    assert dto["report_context"] == "rep_in_var"
    assert dto["step_detector"] == "step_in_var"
    assert dto["evaluated_matrices"] == "ev_in_var"

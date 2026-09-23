"""Unit tests for StepOutputDTO and StepPayloadValue validation."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.atom_evaluation import ReducedAtomDTO
from backend_v2.models.dtos.atom_result import AtomResultDTO
from backend_v2.models.dtos.step_output import StepOutputDTO
from backend_v2.models.enums import ExecutionStatus, LaxExecutionStatus


def test_step_output_dto_with_atom_result() -> None:
    """Test StepOutputDTO with AtomResultDTO payload."""
    atom = AtomResultDTO(
        tda_id="tda_1234567890abcdef",
        status=ExecutionStatus.PASSED,
        evaluation_reasoning="Meets criteria.",
        source_quote="Exact quote here.",
    )
    dto = StepOutputDTO(
        step_id="stp_1234567890abcdef",
        block_id="blk_1234567890abcdef",
        data_type="matrix",
        payload=atom,
    )
    assert dto.step_id == "stp_1234567890abcdef"
    assert dto.payload == atom


def test_step_output_dto_with_reduced_atom_dto() -> None:
    """Test StepOutputDTO with ReducedAtomDTO payload."""
    reduced_atom = ReducedAtomDTO(
        tda_id="tda_1234567890abcdef",
        status=LaxExecutionStatus.PASSED,
        reasoning="Compact reasoning.",
        source_quote="Verbatim quote text.",
    )
    dto = StepOutputDTO(
        step_id="matrix_reducer",
        block_id="reduced_atoms",
        data_type="unknown",
        payload=reduced_atom,
    )
    assert dto.step_id == "matrix_reducer"
    assert dto.block_id == "reduced_atoms"
    assert dto.payload == reduced_atom


def test_step_output_dto_with_reduced_atoms_list() -> None:
    """Test StepOutputDTO with list[ReducedAtomDTO] payload."""
    reduced_atoms = [
        ReducedAtomDTO(
            tda_id="tda_1234567890abcdef",
            status=LaxExecutionStatus.PASSED,
            reasoning="Passed evaluation.",
        ),
        ReducedAtomDTO(
            tda_id="tda_abcdef1234567890",
            status=LaxExecutionStatus.FAILED,
            reasoning="Failed criteria.",
        ),
    ]
    dto = StepOutputDTO(
        step_id="matrix_reducer",
        block_id="reduced_atoms",
        data_type="unknown",
        payload=reduced_atoms,
    )
    assert isinstance(dto.payload, list)
    assert len(dto.payload) == 2
    assert dto.payload[0].tda_id == "tda_1234567890abcdef"


def test_step_output_dto_with_scalar_payloads() -> None:
    """Test StepOutputDTO with scalar and None payloads."""
    dto_str = StepOutputDTO(
        step_id="stp_1",
        block_id="blk_1",
        data_type="text",
        payload="text content",
    )
    assert dto_str.payload == "text content"

    dto_none = StepOutputDTO(
        step_id="stp_2",
        block_id="blk_2",
        data_type="text",
        payload=None,
    )
    assert dto_none.payload is None


def test_step_output_dto_extra_forbidden() -> None:
    """Test StepOutputDTO rejects extra fields under extra='forbid'."""
    with pytest.raises(ValidationError):
        StepOutputDTO.model_validate(
            {
                "step_id": "stp_1",
                "block_id": "blk_1",
                "data_type": "text",
                "payload": "content",
                "extra_forbidden_key": "crash",
            }
        )

"""Unit tests for hook delta and projection DTOs.

Verifies strict typing, immutability, extra forbidden constraints,
discriminated unions, and serialization parity across all hook delta models.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.atom_result import AtomResultDTO, HydratedAtomDTO
from backend_v2.models.dtos.hook_delta import (
    HookDeltaDTO,
    MatrixHookResultDTO,
    MatrixProjectionResultDTO,
    MissingContextDTO,
    ProjectedResultsDTO,
)
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.enums import ExecutionStatus, LaxSDUIComponentType


def _build_test_atom_result() -> AtomResultDTO:
    """Helper to construct a valid AtomResultDTO fixture."""
    return AtomResultDTO(
        tda_id="tda_11112222333344445555666677778888",
        status=ExecutionStatus.PASSED,
        source_quote="Direct evidence quotation.",
        evaluation_reasoning="Valid justification evidence.",
    )


def test_projected_results_dto() -> None:
    """Verify ProjectedResultsDTO instantiation, immutability, and extra forbid."""
    atom = _build_test_atom_result()
    hydrated = HydratedAtomDTO(
        sdui_component=LaxSDUIComponentType.BOOLEAN_CARD,
        resolved_claim="Test assertion",
        source_quote=atom.source_quote,
    )
    dto = ProjectedResultsDTO(results=[atom], hydrated_references={atom.tda_id: hydrated})
    assert len(dto.results) == 1
    assert atom.tda_id in dto.hydrated_references

    with pytest.raises(ValidationError):
        dto.results = []  # type: ignore[misc]

    with pytest.raises(ValidationError):
        ProjectedResultsDTO.model_validate({"results": [atom], "hydrated_references": {}, "extra": 1})


def test_missing_context_dto() -> None:
    """Verify MissingContextDTO instantiation, immutability, and extra forbid."""
    dto = MissingContextDTO(missing_atoms=["Atom A", "Atom B"], missing_context_text="Missing A, B")
    assert dto.missing_atoms == ["Atom A", "Atom B"]
    assert dto.missing_context_text == "Missing A, B"

    with pytest.raises(ValidationError):
        dto.missing_atoms = []  # type: ignore[misc]

    with pytest.raises(ValidationError):
        MissingContextDTO.model_validate({"missing_atoms": [], "forbidden": "field"})


def test_matrix_projection_result_dto() -> None:
    """Verify MatrixProjectionResultDTO instantiation, immutability, and extra forbid."""
    atom = _build_test_atom_result()
    matrix = LightweightMatrixOutput(raw_score=4.0, normalized_score=80.0, justification="Good")
    missing = MissingContextDTO(missing_atoms=["Atom C"])
    dto = MatrixProjectionResultDTO(results=[atom], matrix_output=matrix, missing_context=missing)

    assert len(dto.results) == 1
    assert dto.matrix_output.raw_score == 4.0
    assert dto.missing_context is not None
    assert dto.missing_context.missing_atoms == ["Atom C"]

    with pytest.raises(ValidationError):
        dto.matrix_output = matrix  # type: ignore[misc]

    with pytest.raises(ValidationError):
        MatrixProjectionResultDTO.model_validate(
            {"results": [atom], "matrix_output": matrix, "unexpected": True}
        )


def test_matrix_hook_result_dto() -> None:
    """Verify MatrixHookResultDTO instantiation, immutability, and extra forbid."""
    matrix = LightweightMatrixOutput(raw_score=5.0, normalized_score=100.0)
    quote = QuoteEvidenceDTO(quote="Verifiable text", verified_source_ids=[])
    dto = MatrixHookResultDTO(
        matrix_outputs={"blk_test": matrix},
        missing_contexts={"blk_test": "None missing"},
        atom_quotes={"blk_test": [quote]},
    )
    assert "blk_test" in dto.matrix_outputs
    assert dto.missing_contexts["blk_test"] == "None missing"
    assert len(dto.atom_quotes["blk_test"]) == 1

    with pytest.raises(ValidationError):
        dto.matrix_outputs = {}  # type: ignore[misc]

    with pytest.raises(ValidationError):
        MatrixHookResultDTO.model_validate(
            {
                "matrix_outputs": {},
                "missing_contexts": {},
                "atom_quotes": {},
                "invalid_extra": "value",
            }
        )


def test_hook_delta_dto_variants_and_roundtrip() -> None:
    """Verify HookDeltaDTO with various delta models and full-duplex roundtrip."""
    matrix = LightweightMatrixOutput(raw_score=3.0, normalized_score=60.0)
    matrix_hook_res = MatrixHookResultDTO(
        matrix_outputs={"blk_1": matrix},
        missing_contexts={"blk_1": "Missing"},
        atom_quotes={"blk_1": []},
    )
    delta_dto = HookDeltaDTO(delta=matrix_hook_res, metadata_updates={"custom_key": "custom_val"})
    assert delta_dto.delta == matrix_hook_res
    assert delta_dto.metadata_updates == {"custom_key": "custom_val"}

    dumped = delta_dto.model_dump(mode="json")
    reconstituted = HookDeltaDTO.model_validate(dumped)
    assert isinstance(reconstituted.delta, MatrixHookResultDTO)
    assert reconstituted.delta.matrix_outputs["blk_1"].raw_score == 3.0

    empty_delta = HookDeltaDTO()
    assert empty_delta.delta is None
    assert empty_delta.metadata_updates is None

    with pytest.raises(ValidationError):
        empty_delta.delta = None  # type: ignore[misc]

    with pytest.raises(ValidationError):
        HookDeltaDTO.model_validate({"extra_forbidden": True})

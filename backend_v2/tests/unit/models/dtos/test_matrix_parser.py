"""Unit tests for ParsedMatricesResultDTO and ScorecardAtomCollectionDTO."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO
from backend_v2.models.dtos.matrix_parser import ParsedMatricesResultDTO, ScorecardAtomCollectionDTO
from backend_v2.models.dtos.matrix_scorecard import ScorecardAtomDTO
from backend_v2.models.enums import ExecutionStatus, VisualIntent


def test_scorecard_atom_collection_dto() -> None:
    """Verify ScorecardAtomCollectionDTO dictionary-like behavior and immutability."""
    reasoning = ReasoningStepDTO(
        step_1_identify_premise="Test premise",
        step_2_scan_source="Test source scan",
        step_3_evaluate_anti_patterns="Test anti-patterns",
        step_4_final_conclusion="Test conclusion",
    )
    atom = ScorecardAtomDTO(
        atom_id="atom_1",
        level=1,
        level_name="Level 1",
        claim_label="Test Claim",
        extracted_facts={},
        exact_quotes=[],
        internal_logic_en=reasoning,
        status=ExecutionStatus.PASSED,
        semantic_reasoning="Reasoning test",
        contextual_override=False,
        chart_display_label="Atom 1",
        visual_intent=VisualIntent.NEUTRAL,
    )
    col = ScorecardAtomCollectionDTO(atoms={"atom_1": atom})
    assert len(col) == 1
    assert "atom_1" in col
    assert "atom_2" not in col
    assert col["atom_1"] == atom
    assert list(col.values()) == [atom]
    assert list(col.items()) == [("atom_1", atom)]
    assert list(col.keys()) == ["atom_1"]

    with pytest.raises(KeyError):
        _ = col["unknown"]

    with pytest.raises(ValidationError):
        ScorecardAtomCollectionDTO(unknown="field")  # type: ignore[call-arg]


def test_parsed_matrices_result_dto() -> None:
    """Verify ParsedMatricesResultDTO construction and extra forbidden."""
    col = ScorecardAtomCollectionDTO()
    dto = ParsedMatricesResultDTO(
        evaluative_matrices=[],
        informational_matrices=[],
        all_parsed_matrices={},
        step_scorecard_atoms={"step_1": col},
    )
    assert dto.evaluative_matrices == []
    assert dto.informational_matrices == []
    assert dto.all_parsed_matrices == {}
    assert "step_1" in dto.step_scorecard_atoms

    with pytest.raises(ValidationError):
        ParsedMatricesResultDTO(
            evaluative_matrices=[],
            informational_matrices=[],
            all_parsed_matrices={},
            step_scorecard_atoms={},
            extra_field="bad",  # type: ignore[call-arg]
        )

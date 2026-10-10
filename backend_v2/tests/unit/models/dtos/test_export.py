"""Unit tests for Export DTOs.

Verifies strict Pydantic V2 instantiation, extra='forbid' validation,
frozen immutability, and field constraints for ExportForensicAtomDTO,
ExportMatrixSummaryRowDTO, and ExportPayloadDTO.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.export import (
    ExportDenormalizedFlatRowDTO,
    ExportForensicAtomDTO,
    ExportMatrixSummaryRowDTO,
    ExportPayloadDTO,
)


def test_export_forensic_atom_dto_valid() -> None:
    """Test valid instantiation and field serialization for ExportForensicAtomDTO."""
    atom = ExportForensicAtomDTO(
        matrix_label="Strategic Alignment",
        context_target="Overall Strategy",
        level=1,
        level_name="Baseline",
        criterion="Evidence of roadmap planning",
        claim_type="Required Claim",
        result_status=1,
        quotes="The roadmap defines Q1 deliverables.",
        ai_reasoning="Quote directly verifies the milestone planning.",
    )
    assert atom.matrix_label == "Strategic Alignment"
    assert atom.context_target == "Overall Strategy"
    assert atom.level == 1
    assert atom.level_name == "Baseline"
    assert atom.criterion == "Evidence of roadmap planning"
    assert atom.claim_type == "Required Claim"
    assert atom.result_status == 1
    assert atom.quotes == "The roadmap defines Q1 deliverables."
    assert atom.ai_reasoning == "Quote directly verifies the milestone planning."


def test_export_forensic_atom_dto_extra_forbid() -> None:
    """Test that ExportForensicAtomDTO rejects unexpected extra fields."""
    with pytest.raises(ValidationError):
        ExportForensicAtomDTO.model_validate(
            {
                "matrix_label": "M",
                "context_target": "C",
                "level": 1,
                "level_name": "L",
                "criterion": "Crit",
                "claim_type": "T",
                "result_status": 1,
                "quotes": "Q",
                "ai_reasoning": "R",
                "unexpected_field": "disallowed",
            }
        )


def test_export_forensic_atom_dto_frozen() -> None:
    """Test that ExportForensicAtomDTO is immutable."""
    atom = ExportForensicAtomDTO(
        matrix_label="M",
        context_target="C",
        level=1,
        level_name="L",
        criterion="Crit",
        claim_type="T",
        result_status=1,
        quotes="Q",
        ai_reasoning="R",
    )
    with pytest.raises(ValidationError):
        atom.matrix_label = "Mutated"


def test_export_matrix_summary_row_dto_valid() -> None:
    """Test valid instantiation and field serialization for ExportMatrixSummaryRowDTO."""
    row = ExportMatrixSummaryRowDTO(
        execution_id="exe_0123456789abcdef",
        label="Operational Excellence",
        context_target="Internal Processes",
        distribution="3 / 2 / 1",
        hits=6,
        total_atoms=8,
        hit_ratio=0.75,
        raw_score=3.75,
        scale_max=5.0,
        normalized_score=75.0,
        row_explanation="Solid operational cadence with minor process gaps.",
        criteria="6/8",
        source="doc_engineering_handbook",
    )
    assert row.execution_id == "exe_0123456789abcdef"
    assert row.label == "Operational Excellence"
    assert row.context_target == "Internal Processes"
    assert row.distribution == "3 / 2 / 1"
    assert row.hits == 6
    assert row.total_atoms == 8
    assert row.hit_ratio == 0.75
    assert row.raw_score == 3.75
    assert row.scale_max == 5.0
    assert row.normalized_score == 75.0
    assert row.row_explanation == "Solid operational cadence with minor process gaps."
    assert row.criteria == "6/8"
    assert row.source == "doc_engineering_handbook"


def test_export_matrix_summary_row_dto_extra_forbid() -> None:
    """Test that ExportMatrixSummaryRowDTO rejects unexpected extra fields."""
    with pytest.raises(ValidationError):
        ExportMatrixSummaryRowDTO.model_validate(
            {
                "execution_id": "exe_123",
                "label": "M",
                "context_target": "C",
                "distribution": "D",
                "hits": 1,
                "total_atoms": 1,
                "hit_ratio": 1.0,
                "raw_score": 5.0,
                "scale_max": 5.0,
                "normalized_score": 100.0,
                "row_explanation": "E",
                "criteria": "1/1",
                "source": "S",
                "extra_property": "illegal",
            }
        )


def test_export_matrix_summary_row_dto_frozen() -> None:
    """Test that ExportMatrixSummaryRowDTO is immutable."""
    row = ExportMatrixSummaryRowDTO(
        execution_id="exe_123",
        label="M",
        context_target="C",
        distribution="D",
        hits=1,
        total_atoms=1,
        hit_ratio=1.0,
        raw_score=5.0,
        scale_max=5.0,
        normalized_score=100.0,
        row_explanation="E",
        criteria="1/1",
        source="S",
    )
    with pytest.raises(ValidationError):
        row.label = "Modified"


def test_export_denormalized_flat_row_dto_valid() -> None:
    """Test valid instantiation and field serialization for ExportDenormalizedFlatRowDTO."""
    row = ExportDenormalizedFlatRowDTO(
        execution_id="exe_0123456789abcdef",
        matrix_label="Operational Excellence",
        context_target="Internal Processes",
        distribution="3 / 2 / 1",
        hits=6,
        total_atoms=8,
        hit_ratio=0.75,
        raw_score=3.75,
        scale_max=5.0,
        normalized_score=75.0,
        level=2,
        level_name="Intermediate",
        criterion="Systematic sprint retrospective documentation",
        claim_type="Positive Competence",
        result_status=1,
        quotes="Weekly retrospectives are maintained in Confluence.",
        ai_reasoning="Consistent cadence evidenced by verified artifact.",
    )
    assert row.execution_id == "exe_0123456789abcdef"
    assert row.matrix_label == "Operational Excellence"
    assert row.context_target == "Internal Processes"
    assert row.distribution == "3 / 2 / 1"
    assert row.hits == 6
    assert row.total_atoms == 8
    assert row.hit_ratio == 0.75
    assert row.raw_score == 3.75
    assert row.scale_max == 5.0
    assert row.normalized_score == 75.0
    assert row.level == 2
    assert row.level_name == "Intermediate"
    assert row.criterion == "Systematic sprint retrospective documentation"
    assert row.claim_type == "Positive Competence"
    assert row.result_status == 1
    assert row.quotes == "Weekly retrospectives are maintained in Confluence."
    assert row.ai_reasoning == "Consistent cadence evidenced by verified artifact."


def test_export_denormalized_flat_row_dto_extra_forbid() -> None:
    """Test that ExportDenormalizedFlatRowDTO rejects unexpected extra fields."""
    with pytest.raises(ValidationError):
        ExportDenormalizedFlatRowDTO.model_validate(
            {
                "execution_id": "exe_123",
                "matrix_label": "M",
                "context_target": "C",
                "distribution": "D",
                "hits": 1,
                "total_atoms": 1,
                "hit_ratio": 1.0,
                "raw_score": 5.0,
                "scale_max": 5.0,
                "normalized_score": 100.0,
                "level": 1,
                "level_name": "L",
                "criterion": "Crit",
                "claim_type": "Claim",
                "result_status": 1,
                "quotes": "Q",
                "ai_reasoning": "R",
                "extra_column": "forbidden",
            }
        )


def test_export_denormalized_flat_row_dto_frozen() -> None:
    """Test that ExportDenormalizedFlatRowDTO is immutable."""
    row = ExportDenormalizedFlatRowDTO(
        execution_id="exe_123",
        matrix_label="M",
        context_target="C",
        distribution="D",
        hits=1,
        total_atoms=1,
        hit_ratio=1.0,
        raw_score=5.0,
        scale_max=5.0,
        normalized_score=100.0,
        level=1,
        level_name="L",
        criterion="Crit",
        claim_type="Claim",
        result_status=1,
        quotes="Q",
        ai_reasoning="R",
    )
    with pytest.raises(ValidationError):
        row.matrix_label = "Modified"


def test_export_denormalized_flat_row_dto_boundary_validation() -> None:
    """Test ISTQB boundary value validation on numeric constraints."""
    # Negative hits rejected
    with pytest.raises(ValidationError):
        ExportDenormalizedFlatRowDTO(
            execution_id="exe_123",
            matrix_label="M",
            context_target="C",
            distribution="D",
            hits=-1,
            total_atoms=1,
            hit_ratio=0.5,
            raw_score=2.5,
            scale_max=5.0,
            normalized_score=50.0,
            level=1,
            level_name="L",
            criterion="Crit",
            claim_type="Claim",
            result_status=1,
            quotes="Q",
            ai_reasoning="R",
        )

    # Invalid result_status rejected (must be 0 or 1)
    with pytest.raises(ValidationError):
        ExportDenormalizedFlatRowDTO(
            execution_id="exe_123",
            matrix_label="M",
            context_target="C",
            distribution="D",
            hits=1,
            total_atoms=1,
            hit_ratio=0.5,
            raw_score=2.5,
            scale_max=5.0,
            normalized_score=50.0,
            level=1,
            level_name="L",
            criterion="Crit",
            claim_type="Claim",
            result_status=2,
            quotes="Q",
            ai_reasoning="R",
        )


def test_export_payload_dto_valid() -> None:
    """Test valid instantiation and field serialization for ExportPayloadDTO."""
    payload = ExportPayloadDTO(
        content_bytes=b"sample binary content",
        filename="report.xlsx",
        mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    assert payload.content_bytes == b"sample binary content"
    assert payload.filename == "report.xlsx"
    assert payload.mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def test_export_payload_dto_extra_forbid() -> None:
    """Test that ExportPayloadDTO rejects unexpected extra fields."""
    with pytest.raises(ValidationError):
        ExportPayloadDTO.model_validate(
            {
                "content_bytes": b"data",
                "filename": "file.csv",
                "mime_type": "text/csv",
                "spurious_field": True,
            }
        )


def test_export_payload_dto_frozen() -> None:
    """Test that ExportPayloadDTO is immutable."""
    payload = ExportPayloadDTO(
        content_bytes=b"data",
        filename="file.csv",
        mime_type="text/csv",
    )
    with pytest.raises(ValidationError):
        payload.filename = "other.csv"

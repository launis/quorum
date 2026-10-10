"""Unit tests for Export DTOs.

Verifies strict Pydantic V2 instantiation, extra='forbid' validation,
frozen immutability, and field constraints for ExportForensicAtomDTO,
ExportMatrixSummaryRowDTO, and ExportPayloadDTO.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.export import (
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
        label="Operational Excellence",
        context_target="Internal Processes",
        distribution="3 / 2 / 1",
        row_explanation="Solid operational cadence with minor process gaps.",
        criteria="6/8",
        quotes="Weekly sprint retrospectives are conducted.",
        source="doc_engineering_handbook",
        normalized_score=75.0,
        score=3.75,
    )
    assert row.label == "Operational Excellence"
    assert row.context_target == "Internal Processes"
    assert row.distribution == "3 / 2 / 1"
    assert row.row_explanation == "Solid operational cadence with minor process gaps."
    assert row.criteria == "6/8"
    assert row.quotes == "Weekly sprint retrospectives are conducted."
    assert row.source == "doc_engineering_handbook"
    assert row.normalized_score == 75.0
    assert row.score == 3.75


def test_export_matrix_summary_row_dto_extra_forbid() -> None:
    """Test that ExportMatrixSummaryRowDTO rejects unexpected extra fields."""
    with pytest.raises(ValidationError):
        ExportMatrixSummaryRowDTO.model_validate(
            {
                "label": "M",
                "context_target": "C",
                "distribution": "D",
                "row_explanation": "E",
                "criteria": "1/1",
                "quotes": "Q",
                "source": "S",
                "normalized_score": 100.0,
                "score": 5.0,
                "extra_property": "illegal",
            }
        )


def test_export_matrix_summary_row_dto_frozen() -> None:
    """Test that ExportMatrixSummaryRowDTO is immutable."""
    row = ExportMatrixSummaryRowDTO(
        label="M",
        context_target="C",
        distribution="D",
        row_explanation="E",
        criteria="1/1",
        quotes="Q",
        source="S",
        normalized_score=100.0,
        score=5.0,
    )
    with pytest.raises(ValidationError):
        row.label = "Modified"


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

"""Unit tests for ArchivalPrecedentDTO domain schema and ISTQB boundary invariants."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.domain.archival import ArchivalPrecedentDTO, PrecedentDTO
from backend_v2.models.enums import EntityPrefix


def test_archival_precedent_dto_validation() -> None:
    """Verify ArchivalPrecedentDTO and PrecedentDTO alias construct and serialize valid records."""
    exec_id = generate_opaque_id(EntityPrefix.EXECUTION)
    dto: PrecedentDTO = ArchivalPrecedentDTO(
        id=exec_id,
        date="2026-05-04T12:00:00Z",
        scores="Accuracy: 5.00",
        verdict="Approved",
    )

    assert dto.id == exec_id
    assert dto.date == "2026-05-04T12:00:00Z"
    assert dto.scores == "Accuracy: 5.00"
    assert dto.verdict == "Approved"

    roundtrip = ArchivalPrecedentDTO.model_validate_json(dto.model_dump_json())
    assert roundtrip == dto


def test_archival_precedent_dto_invalid_extra_and_missing_fields() -> None:
    """Verify ArchivalPrecedentDTO rejects unrecognized extra fields and missing required fields."""
    exec_id = generate_opaque_id(EntityPrefix.EXECUTION)

    with pytest.raises(ValidationError):
        ArchivalPrecedentDTO.model_validate(
            {
                "id": exec_id,
                "date": "2026-05-04T12:00:00Z",
                "scores": "5.0",
                "verdict": "Approved",
                "extra_field": "not allowed",
            }
        )

    with pytest.raises(ValidationError):
        ArchivalPrecedentDTO.model_validate(
            {
                "id": exec_id,
                "date": "2026-05-04T12:00:00Z",
                "scores": "5.0",
            }
        )


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("id", ""),
        ("id", "   "),
        ("date", ""),
        ("scores", ""),
        ("verdict", ""),
    ],
)
def test_archival_precedent_dto_invalid_boundary_empty_strings(field_name: str, invalid_value: str) -> None:
    """Verify ArchivalPrecedentDTO enforces min_length=1 boundary after whitespace stripping."""
    payload = {
        "id": generate_opaque_id(EntityPrefix.EXECUTION),
        "date": "2026-05-04T12:00:00Z",
        "scores": "5.0",
        "verdict": "Approved",
        field_name: invalid_value,
    }
    with pytest.raises(ValidationError):
        ArchivalPrecedentDTO.model_validate(payload)


def test_archival_precedent_dto_type_violation_failure() -> None:
    """Verify ArchivalPrecedentDTO enforces strict type checking and rejects non-string inputs."""
    exec_id = generate_opaque_id(EntityPrefix.EXECUTION)
    dto = ArchivalPrecedentDTO(
        id=exec_id,
        date="2026-05-04T12:00:00Z",
        scores="5.0",
        verdict="Approved",
    )
    updated = dto.model_copy(update={"verdict": "Updated Verdict"})
    assert updated.verdict == "Updated Verdict"
    assert dto.verdict == "Approved"

    with pytest.raises(ValidationError):
        ArchivalPrecedentDTO.model_validate(
            {
                "id": exec_id,
                "date": "2026-05-04T12:00:00Z",
                "scores": 5.0,
                "verdict": "Approved",
            }
        )

    with pytest.raises(ValidationError):
        ArchivalPrecedentDTO.model_validate(
            {
                "id": exec_id,
                "date": "2026-05-04T12:00:00Z",
                "scores": "5.0",
                "verdict": 123,
            }
        )

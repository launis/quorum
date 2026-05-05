import pytest
from pydantic import ValidationError

from backend_v2.models.domain.archival import ArchivalPrecedentDTO


def test_archival_precedent_dto_validation() -> None:
    """Test that ArchivalPrecedentDTO follows V2CoreBase strict constraints."""
    dto = ArchivalPrecedentDTO(
        id="arc_123",
        date="2026-05-04",
        scores="5.0",
        verdict="Approved"
    )
    
    assert dto.id == "arc_123"
    assert dto.date == "2026-05-04"
    assert dto.scores == "5.0"
    assert dto.verdict == "Approved"
    
    # Test frozen / extra=forbid
    with pytest.raises(ValidationError):
        ArchivalPrecedentDTO(
            id="arc_123",
            date="2026-05-04",
            scores="5.0",
            verdict="Approved",
            extra_field="not allowed"
        )

    # Test missing fields
    with pytest.raises(ValidationError):
        ArchivalPrecedentDTO(
            id="arc_123",
            date="2026-05-04",
            scores="5.0"
        )

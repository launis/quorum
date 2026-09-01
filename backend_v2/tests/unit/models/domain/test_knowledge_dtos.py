import pytest
from pydantic import ValidationError

from backend_v2.models.auth import OrganizationUpdateDTO
from backend_v2.models.domain.knowledge import (
    ClaimCreateDTO,
    ConceptCreateDTO,
    ReferenceCreateDTO,
)


def test_knowledge_create_dtos_strictness() -> None:
    """Test ConceptCreateDTO, ReferenceCreateDTO, ClaimCreateDTO validation and extra='forbid'."""
    concept = ConceptCreateDTO(name="Agile Development")
    assert concept.name == "Agile Development"

    ref = ReferenceCreateDTO(name="Clean Code Book")
    assert ref.name == "Clean Code Book"

    claim = ClaimCreateDTO(name="SOLID Principles improve maintainability")
    assert claim.name == "SOLID Principles improve maintainability"

    # Empty name fails min_length=1
    with pytest.raises(ValidationError):
        ConceptCreateDTO(name="")

    with pytest.raises(ValidationError):
        ReferenceCreateDTO(name="")

    with pytest.raises(ValidationError):
        ClaimCreateDTO(name="")

    # Extra forbid
    with pytest.raises(ValidationError) as exc:
        ConceptCreateDTO.model_validate({"name": "Test", "extra": 123})
    assert "extra_forbidden" in str(exc.value) or "Extra inputs are not permitted" in str(exc.value)


def test_organization_update_dto_strictness() -> None:
    """Test OrganizationUpdateDTO validation and extra='forbid'."""
    dto = OrganizationUpdateDTO(
        name="Acme Corp",
        quota_limit=5000.0,
        tpm_limit=50000,
        rpm_limit=100,
    )
    assert dto.name == "Acme Corp"
    assert dto.quota_limit == 5000.0
    assert dto.tpm_limit == 50000

    # Negative: quota_limit < 0
    with pytest.raises(ValidationError):
        OrganizationUpdateDTO(quota_limit=-1.0)

    # Negative: tpm_limit < 1000
    with pytest.raises(ValidationError):
        OrganizationUpdateDTO(tpm_limit=500)

    # Negative: rpm_limit < 1
    with pytest.raises(ValidationError):
        OrganizationUpdateDTO(rpm_limit=0)

    # Extra forbid
    with pytest.raises(ValidationError) as exc:
        OrganizationUpdateDTO.model_validate({"name": "Acme", "unauthorized_extra": "fail"})
    assert "extra_forbidden" in str(exc.value) or "Extra inputs are not permitted" in str(exc.value)

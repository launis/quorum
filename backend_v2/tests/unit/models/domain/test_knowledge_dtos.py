"""Unit tests for Knowledge Base, Banned Phrase, and Prompt Template domain models and DTOs."""

import pytest
from pydantic import ValidationError

from backend_v2.models.auth import OrganizationUpdateDTO
from backend_v2.models.domain.knowledge import (
    BannedPhrase,
    Claim,
    ClaimCreateDTO,
    Concept,
    ConceptCreateDTO,
    PromptTemplateDTO,
    Reference,
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

    with pytest.raises(ValidationError) as exc:
        ReferenceCreateDTO.model_validate({"name": "Test", "extra": 123})
    assert "extra_forbidden" in str(exc.value) or "Extra inputs are not permitted" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        ClaimCreateDTO.model_validate({"name": "Test", "extra": 123})
    assert "extra_forbidden" in str(exc.value) or "Extra inputs are not permitted" in str(exc.value)


def test_banned_phrase_and_prompt_template_strictness() -> None:
    """Test BannedPhrase and PromptTemplateDTO positive, negative, and boundary validations."""
    bp = BannedPhrase(id="bp_1", phrase="synergy")
    assert bp.id == "bp_1"
    assert bp.phrase == "synergy"
    assert bp.language == "en"

    # Negative 1: empty id or phrase (min_length=1 boundary)
    with pytest.raises(ValidationError):
        BannedPhrase(id="", phrase="synergy")
    with pytest.raises(ValidationError):
        BannedPhrase(id="bp_1", phrase="")

    # Negative 2: extra field forbidden
    with pytest.raises(ValidationError):
        BannedPhrase.model_validate({"id": "bp_1", "phrase": "synergy", "extra": "bad"})
    with pytest.raises(ValidationError):
        BannedPhrase.model_validate({"id": "bp_1", "phrase": 123})

    pt = PromptTemplateDTO(system="Sys instruction", user="User instruction")
    assert pt.system == "Sys instruction"
    assert pt.user == "User instruction"

    # Negative 1: missing required fields or wrong type in strict mode
    with pytest.raises(ValidationError):
        PromptTemplateDTO.model_validate({"system": "Sys only"})
    with pytest.raises(ValidationError):
        PromptTemplateDTO.model_validate({"system": 123, "user": "User"})

    # Negative 2: extra field forbidden
    with pytest.raises(ValidationError):
        PromptTemplateDTO.model_validate({"system": "Sys", "user": "Usr", "extra": "bad"})


def test_knowledge_domain_entities_strictness() -> None:
    """Test Concept, Reference, and Claim positive, negative, and boundary validations."""
    concept = Concept(id="con_1", name="Test Concept")
    assert concept.id == "con_1"
    assert concept.name == "Test Concept"

    ref = Reference(id="ref_1")
    assert ref.id == "ref_1"
    assert ref.name is None

    claim = Claim(id="clm_1", name="Test Claim")
    assert claim.id == "clm_1"
    assert claim.name == "Test Claim"

    # Negative 1: min_length=1 boundary violation on id (whitespace stripped by V2CoreBase)
    with pytest.raises(ValidationError):
        Concept(id="")
    with pytest.raises(ValidationError):
        Reference(id="   ")
    with pytest.raises(ValidationError):
        Claim(id="")

    # Negative 2: extra='forbid' and strict type enforcement
    with pytest.raises(ValidationError):
        Concept.model_validate({"id": "con_1", "unknown": "field"})
    with pytest.raises(ValidationError):
        Reference.model_validate({"id": "ref_1", "name": 999})
    with pytest.raises(ValidationError):
        Claim.model_validate({"id": "clm_1", "unknown": "field"})


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


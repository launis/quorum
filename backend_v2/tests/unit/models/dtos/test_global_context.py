"""Unit tests for GlobalContextVarsDTO.

Verifies strict typing, immutability, extra forbidden constraints,
alias handling, and serialization parity for global context variables.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.global_context import GlobalContextVarsDTO


def test_global_context_vars_defaults() -> None:
    """Verify default instantiation of GlobalContextVarsDTO."""
    dto = GlobalContextVarsDTO()
    assert dto.language is None
    assert dto.target_locale is None
    assert dto.system_locale is None
    assert dto.profile_id is None
    assert dto.organization_id is None
    assert dto.initiator_id is None
    assert dto.step_coach is None
    assert dto.knowledge_base is None
    assert dto.hydration_results is None
    assert dto.step_linguistics is None
    assert dto.external_evidence is None


def test_global_context_vars_custom_values_and_alias() -> None:
    """Verify GlobalContextVarsDTO with custom values and alias hydration."""
    dto = GlobalContextVarsDTO.model_validate(
        {
            "language": "en",
            "target_locale": "fi",
            "system_locale": "en",
            "profile_id": "prf_1234567890123456",
            "organization_id": "org_1234567890123456",
            "_sys_initiator_id": "usr_1234567890123456",
            "step_coach": {"status": "passed", "score": 4.5, "tags": ["lead"]},
            "knowledge_base": {"domain": "coaching", "active": True},
            "external_evidence": "verified search result",
        }
    )
    assert dto.language == "en"
    assert dto.target_locale == "fi"
    assert dto.system_locale == "en"
    assert dto.profile_id == "prf_1234567890123456"
    assert dto.organization_id == "org_1234567890123456"
    assert dto.initiator_id == "usr_1234567890123456"
    assert dto.step_coach == {"status": "passed", "score": 4.5, "tags": ["lead"]}
    assert dto.knowledge_base == {"domain": "coaching", "active": True}
    assert dto.external_evidence == "verified search result"


def test_global_context_vars_immutability() -> None:
    """Verify that GlobalContextVarsDTO is strictly frozen against in-place mutations."""
    dto = GlobalContextVarsDTO(language="fi")
    with pytest.raises(ValidationError):
        dto.language = "en"  # type: ignore[misc]


def test_global_context_vars_extra_forbidden() -> None:
    """Verify that GlobalContextVarsDTO rejects unexpected extra fields."""
    with pytest.raises(ValidationError):
        GlobalContextVarsDTO.model_validate({"unknown_extra_field": "disallowed"})


def test_global_context_vars_type_strictness() -> None:
    """Verify that GlobalContextVarsDTO rejects invalid primitive types in strict mode."""
    with pytest.raises(ValidationError):
        GlobalContextVarsDTO.model_validate({"language": 12345})

    with pytest.raises(ValidationError):
        GlobalContextVarsDTO.model_validate({"step_coach": "not_a_dictionary"})


def test_global_context_vars_serialization_parity() -> None:
    """Verify full-duplex JSON serialization and roundtrip parity."""
    original = GlobalContextVarsDTO(
        language="fi",
        target_locale="en",
        initiator_id="usr_admin01",
        step_coach={"coaching_mode": "strict"},
    )
    dumped = original.model_dump(mode="json", by_alias=True)
    assert dumped["_sys_initiator_id"] == "usr_admin01"
    reconstituted = GlobalContextVarsDTO.model_validate(dumped)
    assert reconstituted == original

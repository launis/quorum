"""Unit tests for GlobalContextVarsDTO.

Verifies strict typing, immutability, extra forbidden constraints,
alias handling, and serialization parity for global context variables.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.dtos.global_context import GlobalContextVarsDTO
from backend_v2.models.enums import EntityPrefix
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.tests.factories.model_factories import GlobalContextVarsDTOFactory


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


def test_global_context_vars_custom_values_and_canonical_initiator_id() -> None:
    """Verify GlobalContextVarsDTO with custom values and canonical initiator_id hydration."""
    profile_id = generate_opaque_id(EntityPrefix.OUTPUT_PROFILE)
    org_id = generate_opaque_id(EntityPrefix.ORGANIZATION)
    initiator_id = generate_opaque_id(EntityPrefix.USER)
    dto = GlobalContextVarsDTOFactory.build(
        language="en",
        target_locale="fi",
        system_locale="en",
        profile_id=profile_id,
        organization_id=org_id,
        initiator_id=initiator_id,
        step_coach={"status": "passed", "score": 4.5, "tags": ["lead"]},
        knowledge_base={"domain": "coaching", "active": True},
        external_evidence="verified search result",
    )
    assert dto.language == "en"
    assert dto.target_locale == "fi"
    assert dto.system_locale == "en"
    assert dto.profile_id == profile_id
    assert dto.organization_id == org_id
    assert dto.initiator_id == initiator_id
    assert dto.step_coach == {"status": "passed", "score": 4.5, "tags": ["lead"]}
    assert dto.knowledge_base == {"domain": "coaching", "active": True}
    assert dto.external_evidence == "verified search result"


def test_global_context_vars_immutability() -> None:
    """Verify that GlobalContextVarsDTO enforces frozen=True, strict=True, and extra='forbid'."""
    assert GlobalContextVarsDTO.model_config["frozen"] is True
    assert GlobalContextVarsDTO.model_config["strict"] is True
    assert GlobalContextVarsDTO.model_config["extra"] == "forbid"
    dto = GlobalContextVarsDTO(language="fi")
    updated = dto.model_copy(update={"language": "en"})
    assert dto.language == "fi"
    assert updated.language == "en"


def test_global_context_vars_extra_forbidden_error() -> None:
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
    """Verify full-duplex JSON serialization and FastAPI by_alias=True parity with Flutter GlobalContextVarsDto."""
    initiator_id = generate_opaque_id(EntityPrefix.USER)
    org_id = generate_opaque_id(EntityPrefix.ORGANIZATION)
    original = GlobalContextVarsDTOFactory.build(
        language="fi",
        target_locale="en",
        organization_id=org_id,
        initiator_id=initiator_id,
        step_coach={"coaching_mode": "strict"},
    )
    dumped = original.model_dump(mode="json", by_alias=True)
    assert "_sys_initiator_id" not in dumped
    assert dumped["initiator_id"] == initiator_id
    reconstituted = GlobalContextVarsDTO.model_validate(dumped)
    assert reconstituted == original


def test_execution_metadata_by_alias_serialization_forbids_legacy_sys_initiator_id() -> None:
    """Verify ExecutionMetadata serialized with by_alias=True emits canonical initiator_id and rejects _sys_initiator_id."""
    initiator_id = generate_opaque_id(EntityPrefix.USER)
    org_id = generate_opaque_id(EntityPrefix.ORGANIZATION)
    metadata = ExecutionMetadata(
        workflow_version=1,
        global_context_vars=GlobalContextVarsDTOFactory.build(
            organization_id=org_id,
            initiator_id=initiator_id,
            target_locale="fi",
        ),
    )
    dumped_meta = metadata.model_dump(mode="json", by_alias=True, exclude_none=True)
    gvars_payload = dumped_meta["global_context_vars"]
    assert isinstance(gvars_payload, dict)
    assert "_sys_initiator_id" not in gvars_payload
    assert gvars_payload["initiator_id"] == initiator_id

    with pytest.raises(ValidationError):
        GlobalContextVarsDTO.model_validate({"_sys_initiator_id": initiator_id})

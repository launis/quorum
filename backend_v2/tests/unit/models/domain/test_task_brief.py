"""Unit tests for TaskBrief domain model and TaskBriefResponseDTO studio DTO."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.domain.task_brief import TaskBrief
from backend_v2.models.dtos.studio import TaskBriefDeleteResponse, TaskBriefResponseDTO
from backend_v2.models.enums import EntityPrefix
from backend_v2.tests.factories.model_factories import I18nTextFactory, TaskBriefFactory


def test_task_brief_instantiation_and_dto_parity() -> None:
    """Verify TaskBrief and TaskBriefResponseDTO roundtrip serialization and organization_id exposure."""
    brief = TaskBriefFactory.build(
        id="tbr_0195f3a00000700d8a1b2c3d4e5f6001",
        slug="task_brief_ai_steering_audit",
        organization_id="org_0195f3a0000070008000000000000001",
        label=I18nTextFactory.build(translations={"fi": "Tehtävänanto", "en": "Task Brief"}),
        description=I18nTextFactory.build(translations={"fi": "Kuvaus", "en": "Description"}),
        instruction_text="Laadi tekoälyä hyödyntäen perusteltu asiantuntija-analyysi.",
        source_url="https://docs.example.com/brief.pdf",
    )
    assert brief.id == "tbr_0195f3a00000700d8a1b2c3d4e5f6001"
    assert brief.slug == "task_brief_ai_steering_audit"
    assert brief.organization_id == "org_0195f3a0000070008000000000000001"
    assert brief.source_url == "https://docs.example.com/brief.pdf"

    dumped = brief.model_dump(mode="json")
    rehydrated = TaskBrief.model_validate(dumped)
    assert rehydrated == brief

    response_dto = TaskBriefResponseDTO.model_validate(brief.model_dump())
    response_dump = response_dto.model_dump(mode="json")
    assert response_dump["organization_id"] == "org_0195f3a0000070008000000000000001"
    assert response_dump["id"] == brief.id

    delete_resp = TaskBriefDeleteResponse.model_validate_json(f'{{"status": "deleted", "deleted_id": "{brief.id}"}}')
    assert delete_resp.status == "deleted"
    assert delete_resp.deleted_id == brief.id


def test_task_brief_system_level_exclude_none_roundtrip() -> None:
    """Verify system-level TaskBrief omits unset organization_id and source_url when dumped with exclude_none."""
    brief = TaskBriefFactory.build(
        id=generate_opaque_id(EntityPrefix.TASK_BRIEF),
        organization_id=None,
        source_url=None,
    )
    dumped = brief.model_dump(mode="json", exclude_none=True)
    assert "organization_id" not in dumped
    assert "source_url" not in dumped
    rehydrated = TaskBrief.model_validate(dumped)
    assert rehydrated.organization_id is None
    assert rehydrated.source_url is None


@pytest.mark.parametrize(
    "invalid_id",
    [
        "blk_0195f3a00000700d8a1b2c3d4e5f6001",
        "tbr_not_a_32_hex_uuidv7_string",
        "tbr_0195f3a0000040008a1b2c3d4e5f6001",
        "",
    ],
)
def test_task_brief_rejects_invalid_opaque_id(invalid_id: str) -> None:
    """Verify TaskBrief rejects wrong entity prefixes, non-UUIDv7 hex strings, and malformed IDs."""
    payload = TaskBriefFactory.build().model_dump()
    payload["id"] = invalid_id
    with pytest.raises(ValidationError):
        TaskBrief.model_validate(payload)


@pytest.mark.parametrize(
    ("field_name", "invalid_value"),
    [
        ("slug", ""),
        ("instruction_text", ""),
        ("source_url", ""),
    ],
)
def test_task_brief_rejects_empty_required_or_bounded_strings(
    field_name: str,
    invalid_value: str,
) -> None:
    """Verify TaskBrief rejects empty slug, instruction_text, and source_url strings (min_length=1)."""
    payload = TaskBriefFactory.build().model_dump()
    payload[field_name] = invalid_value
    with pytest.raises(ValidationError):
        TaskBrief.model_validate(payload)


def test_task_brief_forbids_extra_fields_and_in_place_mutation() -> None:
    """Verify TaskBrief enforces extra='forbid' and frozen=True immutability."""
    brief = TaskBriefFactory.build()
    payload = brief.model_dump()
    payload["unexpected_field"] = "forbidden"
    with pytest.raises(ValidationError):
        TaskBrief.model_validate(payload)

    with pytest.raises((ValidationError, TypeError)):
        del brief.slug

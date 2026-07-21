from unittest.mock import AsyncMock
import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.output_profile import (
    OutputProfileCreateDTO,
    OutputProfileResponseDTO,
    OutputProfileUpdateDTO,
)
from backend_v2.models.enums import XaiExtensionType


def test_output_profile_create_dto_strictness() -> None:
    """Test Create DTO validation, ID pattern and immutability."""
    dto = OutputProfileCreateDTO.model_validate(
        {
            "id": "prf_1234abcd",
            "slug": "my-profile",
            "workflow_id": "wf_123",
            "name": {"default_locale": "en", "translations": {"en": "Name", "fi": "Name"}},
            "visible_block_extensions": [XaiExtensionType.CITATION, XaiExtensionType.JUSTIFICATION],
            "visible_workflow_extensions": [],
        }
    )
    assert dto.id == "prf_1234abcd"
    assert XaiExtensionType.CITATION in dto.visible_block_extensions

    # Immutability check
    with pytest.raises(ValidationError, match="Instance is frozen"):
        dto.slug = "new-slug"  # type: ignore[misc]

    # Forbid extra check
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        OutputProfileCreateDTO.model_validate(
            {
                "id": "prf_1234abcd",
                "slug": "my-profile",
                "workflow_id": "wf_123",
                "name": {"default_locale": "en", "translations": {"en": "Name", "fi": "Name"}},
                "extra": "bad",
            }
        )


def test_output_profile_update_dto_strictness() -> None:
    """Test Update DTO strictness."""
    dto = OutputProfileUpdateDTO(slug="new-slug")
    assert dto.slug == "new-slug"
    assert dto.workflow_id is None

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        OutputProfileUpdateDTO.model_validate({"invalid_field": "boom"})


def test_output_profile_response_dto_strictness() -> None:
    """Test Response DTO strictness and base class inheritance."""
    dto = OutputProfileResponseDTO.model_validate(
        {
            "id": "prf_1234abcd",
            "slug": "my-profile",
            "workflow_id": "wf_123",
            "name": {"default_locale": "en", "translations": {"en": "Name", "fi": "Name"}},
            "layouts": [],
        }
    )
    assert dto.id == "prf_1234abcd"
    assert "date" in dto.visible_metadata

    # Must omit organization_id from dump if inherited correctly from BaseResponseDTO
    dump = dto.model_dump()
    assert "organization_id" not in dump

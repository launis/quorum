from typing import Any

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.output_profile import (
    OutputProfileCreateDTO,
    OutputProfileResponseDTO,
    OutputProfileUpdateDTO,
)
from backend_v2.models.enums import DisplayScale, TargetBlockType, XaiExtensionType

_VALID_CREATE_PAYLOAD: dict[str, Any] = {
    "id": "prf_1234abcd",
    "slug": "my-profile",
    "workflow_id": "wf_123",
    "name": {"default_locale": "en", "translations": {"en": "Name", "fi": "Name"}},
}


def test_output_profile_create_dto_strictness() -> None:
    """Test Create DTO validation, ID pattern and immutability."""
    dto = OutputProfileCreateDTO.model_validate(
        {
            **_VALID_CREATE_PAYLOAD,
            "visible_block_extensions": [XaiExtensionType.CITATION, XaiExtensionType.JUSTIFICATION],
            "visible_workflow_extensions": [],
            "performativity_detector_step_id": "sp_123",
            "display_scale": DisplayScale.ORIGINAL,
        }
    )
    assert dto.id == "prf_1234abcd"
    assert XaiExtensionType.CITATION in dto.visible_block_extensions
    assert dto.performativity_detector_step_id == "sp_123"
    assert dto.display_scale == DisplayScale.ORIGINAL

    # Immutability check
    with pytest.raises(ValidationError, match="Instance is frozen"):
        dto.slug = "new-slug"  # type: ignore[misc]

    # Forbid extra check
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        OutputProfileCreateDTO.model_validate(
            {
                **_VALID_CREATE_PAYLOAD,
                "extra": "bad",
            }
        )

    # Negative test for performativity_detector_step_id
    with pytest.raises(ValidationError, match="Input should be a valid string"):
        OutputProfileCreateDTO.model_validate(
            {
                **_VALID_CREATE_PAYLOAD,
                "performativity_detector_step_id": 123,
            }
        )


def test_create_dto_max_extension_items_zero_raises() -> None:
    """Boundary test: max_extension_items=0 violates ge=1."""
    payload = {**_VALID_CREATE_PAYLOAD, "max_extension_items": 0}
    with pytest.raises(ValidationError, match="greater than or equal to 1"):
        OutputProfileCreateDTO.model_validate(payload)


def test_create_dto_max_extension_items_negative_raises() -> None:
    """Boundary test: max_extension_items=-1 violates ge=1."""
    payload = {**_VALID_CREATE_PAYLOAD, "max_extension_items": -1}
    with pytest.raises(ValidationError, match="greater than or equal to 1"):
        OutputProfileCreateDTO.model_validate(payload)


def test_create_dto_max_extension_items_101_raises() -> None:
    """Boundary test: max_extension_items=101 violates le=100."""
    payload = {**_VALID_CREATE_PAYLOAD, "max_extension_items": 101}
    with pytest.raises(ValidationError, match="less than or equal to 100"):
        OutputProfileCreateDTO.model_validate(payload)


def test_create_dto_invalid_display_scale_raises() -> None:
    """Negative test: invalid display_scale string is rejected."""
    payload = {**_VALID_CREATE_PAYLOAD, "display_scale": "invalid_scale"}
    with pytest.raises(ValidationError, match="Input should be"):
        OutputProfileCreateDTO.model_validate(payload)


def test_create_dto_legacy_include_diagnostic_scorecard_raises() -> None:
    """Negative test: legacy include_diagnostic_scorecard key is strictly forbidden."""
    payload = {**_VALID_CREATE_PAYLOAD, "include_diagnostic_scorecard": True}
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        OutputProfileCreateDTO.model_validate(payload)


def test_create_dto_extra_key_in_synthesis_config_raises() -> None:
    """Negative test: extra keys in nested SynthesisConfigDTO are strictly forbidden."""
    payload = {
        **_VALID_CREATE_PAYLOAD,
        "synthesis": {"synthesis_block_id": "blk_1", "ghost_field": "illegal"},
    }
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        OutputProfileCreateDTO.model_validate(payload)


def test_create_dto_invalid_target_block_raises() -> None:
    """Negative test: unmapped target_block_order item is rejected."""
    payload = {**_VALID_CREATE_PAYLOAD, "target_block_order": ["invalid_block_type"]}
    with pytest.raises(ValidationError, match="Input should be"):
        OutputProfileCreateDTO.model_validate(payload)


def test_create_dto_max_extension_items_100_valid() -> None:
    """Boundary test: max_extension_items=100 is accepted (le=100 edge)."""
    payload = {**_VALID_CREATE_PAYLOAD, "max_extension_items": 100}
    dto = OutputProfileCreateDTO.model_validate(payload)
    assert dto.max_extension_items == 100


def test_create_dto_max_extension_items_1_valid() -> None:
    """Boundary test: max_extension_items=1 is accepted (ge=1 edge)."""
    payload = {**_VALID_CREATE_PAYLOAD, "max_extension_items": 1}
    dto = OutputProfileCreateDTO.model_validate(payload)
    assert dto.max_extension_items == 1


def test_output_profile_update_dto_strictness() -> None:
    """Test Update DTO strictness."""
    dto = OutputProfileUpdateDTO.model_validate({"slug": "new-slug"})
    assert dto.slug == "new-slug"
    assert dto.workflow_id is None

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        OutputProfileUpdateDTO.model_validate({"invalid_field": "boom"})


def test_update_dto_max_extension_items_boundary_negative() -> None:
    """Boundary test: OutputProfileUpdateDTO rejects out of bounds max_extension_items."""
    with pytest.raises(ValidationError, match="greater than or equal to 1"):
        OutputProfileUpdateDTO.model_validate({"max_extension_items": 0})

    with pytest.raises(ValidationError, match="greater than or equal to 1"):
        OutputProfileUpdateDTO.model_validate({"max_extension_items": -1})

    with pytest.raises(ValidationError, match="less than or equal to 100"):
        OutputProfileUpdateDTO.model_validate({"max_extension_items": 101})

    # Valid edges
    dto1 = OutputProfileUpdateDTO.model_validate({"max_extension_items": 1})
    assert dto1.max_extension_items == 1
    dto100 = OutputProfileUpdateDTO.model_validate({"max_extension_items": 100})
    assert dto100.max_extension_items == 100


def test_output_profile_response_dto_strictness() -> None:
    """Test Response DTO strictness and base class inheritance."""
    dto = OutputProfileResponseDTO.model_validate(
        {
            "id": "prf_1234abcd",
            "slug": "my-profile",
            "workflow_id": "wf_123",
            "name": {"default_locale": "en", "translations": {"en": "Name", "fi": "Name"}},
            "layouts": [],
            "display_scale": DisplayScale.ORIGINAL,
        }
    )
    assert dto.id == "prf_1234abcd"
    assert "date" in dto.visible_metadata
    assert dto.display_scale == DisplayScale.ORIGINAL

    # Must omit organization_id from dump if inherited correctly from BaseResponseDTO
    dump = dto.model_dump()
    assert "organization_id" not in dump


def test_output_profile_create_dto_accepts_string_enums_from_http_payload() -> None:
    """Regression test: FastAPI HTTP requests pass raw strings like 'normalized_100' and 'metadata_block'.

    OutputProfileCreateDTO must accept string-based enum representations for display_scale
    and target_block_order via LaxDisplayScale and LaxTargetBlockType annotations.
    """
    payload = {
        **_VALID_CREATE_PAYLOAD,
        "display_scale": "normalized_100",
        "target_block_order": [
            "metadata_block",
            "executive_summary_block",
            "synthesis_text_block",
            "matrix_graphs_block",
            "grouped_extensions_block",
            "penalties_block",
            "matrix_summary_table_block",
            "variance_validation_block",
            "authenticity_evaluation_block",
            "global_score_block",
            "printable_sources_block",
            "jargon_ratio_block",
            "audit_trail_block",
        ],
    }
    dto = OutputProfileCreateDTO.model_validate(payload)
    assert dto.display_scale == DisplayScale.NORMALIZED_100
    assert dto.target_block_order is not None
    assert len(dto.target_block_order) == 13
    assert dto.target_block_order[0] == TargetBlockType.METADATA_BLOCK


def test_output_profile_update_dto_accepts_string_enums_from_http_payload() -> None:
    """Regression test: OutputProfileUpdateDTO must accept string-based enum representations."""
    payload = {
        "display_scale": "normalized_100",
        "target_block_order": ["metadata_block", "global_score_block"],
    }
    dto = OutputProfileUpdateDTO.model_validate(payload)
    assert dto.display_scale == DisplayScale.NORMALIZED_100
    assert dto.target_block_order == [TargetBlockType.METADATA_BLOCK, TargetBlockType.GLOBAL_SCORE_BLOCK]


def test_output_profile_response_dto_accepts_string_enums_from_storage_payload() -> None:
    """Regression test: OutputProfileResponseDTO must accept string-based enum representations."""
    payload = {
        **_VALID_CREATE_PAYLOAD,
        "display_scale": "normalized_100",
        "target_block_order": ["metadata_block", "global_score_block"],
    }
    dto = OutputProfileResponseDTO.model_validate(payload)
    assert dto.display_scale == DisplayScale.NORMALIZED_100
    assert dto.target_block_order == [TargetBlockType.METADATA_BLOCK, TargetBlockType.GLOBAL_SCORE_BLOCK]

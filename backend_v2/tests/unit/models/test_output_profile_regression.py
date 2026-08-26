"""Regression test for OutputProfile schema modernization (Epic 148 Phase 3)."""

import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.output_profile import OutputProfileResponseDTO
from backend_v2.models.enums import TargetBlockType
from backend_v2.models.v2_core import MatrixSynthesisGroup, OutputProfile


def test_output_profile_response_dto_schema_parity() -> None:
    """Proof of success: OutputProfileResponseDTO accepts matrix_synthesis_groups and strictly forbids legacy dicts."""
    payload = {
        "id": "prf_1234567890123456",
        "slug": "test-profile",
        "workflow_id": "wf_9d68c573802341db",
        "name": {"translations": {"en": "Test"}},
        "target_block_order": [TargetBlockType.METADATA_BLOCK],
        "matrix_synthesis_groups": [
            {
                "id": "grp_1",
                "title": {"translations": {"en": "Group 1", "fi": "Ryhmä 1"}},
                "target_blocks": ["blk_1", "blk_2"],
            }
        ],
    }

    dto = OutputProfileResponseDTO.model_validate(payload)
    assert len(dto.matrix_synthesis_groups) == 1
    assert dto.matrix_synthesis_groups[0].id == "grp_1"


def test_output_profile_response_dto_target_block_order_parity() -> None:
    """Proof of success: OutputProfileResponseDTO should accept target_block_order from database."""
    payload = {
        "id": "prf_1234567890123456",
        "slug": "test-profile",
        "workflow_id": "wf_9d68c573802341db",
        "name": {"translations": {"en": "Test"}},
        "target_block_order": [TargetBlockType.METADATA_BLOCK, TargetBlockType.SYNTHESIS_TEXT_BLOCK],
        "matrix_synthesis_groups": [],
    }

    dto = OutputProfileResponseDTO.model_validate(payload)
    assert dto.target_block_order == [TargetBlockType.METADATA_BLOCK, TargetBlockType.SYNTHESIS_TEXT_BLOCK]


def test_embedded_output_profile_schema_parity() -> None:
    """Proof of success: OutputProfile accepts matrix_synthesis_groups."""
    payload = {
        "id": "prf_1234567890123456",
        "slug": "test-profile",
        "workflow_id": "wf_9d68c573802341db",
        "name": {"translations": {"en": "Test"}},
        "target_block_order": [TargetBlockType.METADATA_BLOCK],
        "matrix_synthesis_groups": [
            {
                "id": "grp_1",
                "title": {"translations": {"en": "Group 1", "fi": "Ryhmä 1"}},
                "target_blocks": ["blk_1", "blk_2"],
            }
        ],
    }

    profile = OutputProfile.model_validate(payload)
    assert len(profile.matrix_synthesis_groups) == 1


def test_output_profile_response_dto_negative_extra_keys() -> None:
    """Proof of failure: extra='forbid' should reject unknown or purged keys."""
    payload = {
        "id": "prf_1234567890123456",
        "slug": "test-profile",
        "workflow_id": "wf_9d68c573802341db",
        "name": {"translations": {"en": "Test"}},
        "invalid_extra_key": "should fail",
    }
    with pytest.raises(ValidationError) as exc_info:
        OutputProfileResponseDTO.model_validate(payload)
    assert "Extra inputs are not permitted" in str(exc_info.value)


def test_embedded_output_profile_negative_wrong_type() -> None:
    """Proof of failure: matrix_synthesis_groups must be a list of valid MatrixSynthesisGroup models."""
    payload = {
        "id": "prf_1234567890123456",
        "slug": "test-profile",
        "workflow_id": "wf_9d68c573802341db",
        "name": {"translations": {"en": "Test"}},
        "target_block_order": [TargetBlockType.METADATA_BLOCK],
        "matrix_synthesis_groups": "not a list",
    }
    with pytest.raises(ValidationError) as exc_info:
        OutputProfile.model_validate(payload)
    assert "Input should be a valid list" in str(exc_info.value)

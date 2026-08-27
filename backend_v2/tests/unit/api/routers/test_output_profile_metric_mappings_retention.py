"""Regression test for matrix_synthesis_groups retention in OutputProfileResponseDTO.

Validates that OutputProfileResponseDTO does NOT exclude matrix_synthesis_groups when serialized,
preventing Flutter and API clients from wiping matrix_synthesis_groups on profile updates.
"""

from typing import Any

from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.dtos.output_profile import (
    OutputProfileCreateDTO,
    OutputProfileResponseDTO,
)
from backend_v2.models.v2_core import I18nText, MatrixSynthesisGroup


def test_output_profile_response_dto_serializes_matrix_synthesis_groups() -> None:
    """OutputProfileResponseDTO must serialize matrix_synthesis_groups in JSON output."""
    db_profile_dict: dict[str, Any] = {
        "id": "prf_5d6e7f8091a2b3c4",
        "slug": "test_profile",
        "workflow_id": "wf_9d68c573802341db",
        "name": {"translations": {"fi": "Testi", "en": "Test"}},
        "matrix_synthesis_groups": [
            {
                "id": "grp_1111111111111111",
                "title": {"translations": {"fi": "Ryhmä 1", "en": "Group 1"}},
                "target_blocks": ["blk_1", "blk_2"],
                "synthesis_directive": "Directive",
            }
        ],
    }

    # 1. Hydrate into OutputProfileResponseDTO
    dto = OutputProfileResponseDTO.model_validate(db_profile_dict, strict=False)

    # 2. Serialize to JSON dict (simulating FastAPI response serialization)
    serialized = dto.model_dump(mode="json")

    # 3. Assert matrix_synthesis_groups is NOT stripped
    assert "matrix_synthesis_groups" in serialized, (
        "matrix_synthesis_groups was excluded from serialized OutputProfileResponseDTO JSON response!"
    )
    assert len(serialized["matrix_synthesis_groups"]) == 1
    assert serialized["matrix_synthesis_groups"][0]["id"] == "grp_1111111111111111"


def test_output_profile_roundtrip_preserves_matrix_synthesis_groups() -> None:
    """Simulates GET -> Flutter Edit -> PUT roundtrip to ensure matrix_synthesis_groups is preserved."""
    db_profile = OutputProfile(
        id="prf_5d6e7f8091a2b3c4",
        slug="test_profile",
        workflow_id="wf_9d68c573802341db",
        name=I18nText(translations={"fi": "Testi", "en": "Test"}),
        target_block_order=[],
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_1111111111111111",
                title=I18nText(translations={"fi": "Ryhmä 1", "en": "Group 1"}),
                target_blocks=["blk_1"],
            )
        ],
    )

    # 1. API GET response serialization
    response_dto = OutputProfileResponseDTO.model_validate(db_profile.model_dump(mode="json"), strict=False)
    api_get_json = response_dto.model_dump(mode="json")

    # 2. Flutter client parses api_get_json and sends back PUT payload (without id in body)
    put_payload = {k: v for k, v in api_get_json.items() if k != "id"}

    # 3. Backend receives PUT payload in OutputProfileCreateDTO and hydrates with path ID
    create_dto = OutputProfileCreateDTO.model_validate(put_payload)
    profile_dict = create_dto.model_dump()
    profile_dict["id"] = "prf_1111111111111111"
    saved_profile = OutputProfile.model_validate(profile_dict)

    # 4. Verify matrix_synthesis_groups is preserved
    assert len(saved_profile.matrix_synthesis_groups) == 1
    assert saved_profile.matrix_synthesis_groups[0].id == "grp_1111111111111111"

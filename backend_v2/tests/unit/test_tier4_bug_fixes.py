from backend_v2.models.dtos.output_profile import OutputProfileResponseDTO, OutputProfileUpdateDTO
from backend_v2.models.v2_core import OutputProfile


def test_bug_metric_mappings_silent_override() -> None:
    """Ensures matrix_synthesis_groups is retained across API read/write cycles."""
    # 1. Simulate the OutputProfile in the Database
    db_profile = OutputProfile(
        id="prof_1234abcd1234abcd",
        slug="test",
        workflow_id="wf_1234",
        name={"translations": {"en": "Name"}},  # type: ignore
        matrix_synthesis_groups=[
            {
                "id": "grp_test",
                "title": {"translations": {"en": "Group"}},
                "target_blocks": ["*"],
            }
        ],
    )

    assert len(db_profile.matrix_synthesis_groups) == 1

    # 2. Simulate API GET (Read)
    db_dict = db_profile.model_dump(mode="json")
    response_dto = OutputProfileResponseDTO.model_validate(db_dict, strict=False)

    # 3. Simulate UI saving it back (OutputProfileUpdateDTO)
    ui_payload = {
        "name": response_dto.name.model_dump(mode="json"),
    }

    update_dto = OutputProfileUpdateDTO.model_validate(ui_payload, strict=False)

    # 4. Simulate the API PATCH (Write) in studio_output_profile_service.py
    update_data = update_dto.model_dump(exclude_unset=True, mode="json")

    # 5. Merge existing DB with update_data
    merged = {**db_dict, **update_data}

    # 6. Validate merged against Domain Model
    saved_profile = OutputProfile.model_validate(merged)

    # Validation: The saved profile should NOT have lost matrix_synthesis_groups
    assert len(saved_profile.matrix_synthesis_groups) == 1
    assert saved_profile.matrix_synthesis_groups[0].id == "grp_test"

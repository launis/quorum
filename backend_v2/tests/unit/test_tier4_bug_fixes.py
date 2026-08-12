from backend_v2.models.dtos.output_profile import OutputProfileResponseDTO, OutputProfileUpdateDTO
from backend_v2.models.v2_core import OutputProfile


def test_bug_metric_mappings_silent_override() -> None:
    """Reproduces the Silent Override bug for metric_mappings."""
    # 1. Simulate the OutputProfile in the Database
    db_profile = OutputProfile(
        id="prof_1234abcd1234abcd",
        slug="test",
        workflow_id="wf_1234",
        name={"default_locale": "en", "translations": {"en": "Name"}},  # type: ignore
        metric_mappings={"variance_mechanical": {"default_locale": "en", "translations": {"en": "Mech"}}},  # type: ignore
    )

    assert "variance_mechanical" in db_profile.metric_mappings

    # 2. Simulate API GET (Read) - OutputProfileResponseDTO strips metric_mappings
    db_dict = db_profile.model_dump(mode="json")
    response_dict = db_profile.model_dump(mode="json", exclude={"metric_mappings"})

    response_dto = OutputProfileResponseDTO.model_validate(response_dict, strict=False)

    # 3. Simulate UI saving it back (OutputProfileUpdateDTO)
    # The UI only sends valid fields, but because it initialized metric_mappings as {}, it sends it.
    ui_payload = {
        "name": response_dto.name.model_dump(mode="json"),
        "metric_mappings": {},  # Flutter falls back to empty map for missing field and sends it back
    }

    update_dto = OutputProfileUpdateDTO.model_validate(ui_payload, strict=False)

    # 4. Simulate the API PATCH (Write) in studio_output_profile_service.py
    update_data = update_dto.model_dump(exclude_unset=True, mode="json")
    update_data.pop("metric_mappings", None)

    # 5. Merge existing DB with update_data
    merged = {**db_dict, **update_data}

    # 6. Validate merged against Domain Model
    saved_profile = OutputProfile.model_validate(merged)

    # Validation: The saved profile should NOT have lost variance_mechanical
    assert "variance_mechanical" in saved_profile.metric_mappings, (
        "Fix failed: variance_mechanical was deleted during merge!"
    )

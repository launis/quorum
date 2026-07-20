from backend_v2.models.dtos.output_profile import (
    OutputProfileResponseDTO,
    OutputProfileUpdateDTO,
)


def test_output_profile_response_dto_synthesis_none():
    data = {
        "id": "op_12345678",
        "slug": "test",
        "workflow_id": "wf_12345678",
        "name": {"default_locale": "en", "translations": {"en": "Test"}},
        "visible_metadata": [],
        "visible_block_extensions": [],
        "visible_workflow_extensions": [],
        "display_scale": "original",
        "layouts": [],
    }

    # This should fail if synthesis is not allowed to be None
    dto = OutputProfileResponseDTO.model_validate(data)

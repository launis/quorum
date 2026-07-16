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
        "synthesis": None,
    }

    # This should fail if synthesis is not allowed to be None
    dto = OutputProfileResponseDTO.model_validate(data)
    assert dto.synthesis is None


def test_output_profile_update_dto_with_matrix_column_labels():
    data = {
        "matrix_column_labels": {
            "label_1": {"default_locale": "en", "translations": {"en": "Label 1"}}
        }
    }
    # This will raise ValidationError if matrix_column_labels is not mapped and extra is 'forbid'
    dto = OutputProfileUpdateDTO.model_validate(data)
    assert dto.matrix_column_labels is not None
    assert "label_1" in dto.matrix_column_labels

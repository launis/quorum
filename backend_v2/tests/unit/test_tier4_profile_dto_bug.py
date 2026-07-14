from typing import Any

from backend_v2.models.dtos.output_profile import (
    OutputProfileCreateDTO,
    OutputProfileResponseDTO,
    OutputProfileUpdateDTO,
)


def test_output_profile_dtos_accept_content_blocks() -> None:
    """Tier 4 Bug: Ensure DTOs do not crash when given content_blocks from SDUI schema."""
    data = {
        "id": "prf_1234abcd1234abcd",
        "slug": "test_slug",
        "workflow_id": "wf_1234abcd1234abcd",
        "name": {"default_locale": "en", "translations": {"en": "Title", "fi": "Title"}},
        "layouts": [],
        "content_blocks": [{"id": "blk_123", "block_type": "markdown", "text": "test"}],
    }

    # These should NOT raise ValidationError
    resp_dto = OutputProfileResponseDTO.model_validate(data)
    assert resp_dto.content_blocks is not None
    assert len(resp_dto.content_blocks) == 1

    create_dto = OutputProfileCreateDTO.model_validate(data)
    assert create_dto.content_blocks is not None

    update_data: dict[str, Any] = {"content_blocks": []}
    update_dto = OutputProfileUpdateDTO.model_validate(update_data)
    assert update_dto.content_blocks == []

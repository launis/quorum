import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.system import ClientErrorPayload, HookListResponse


def test_hook_list_response_strictness() -> None:
    """Test HookListResponse enforces Data Sovereignty (BaseResponseDTO) and Phase 9 extra='forbid'."""
    dto = HookListResponse(hooks=["hook_1", "hook_2"])
    assert dto.hooks == ["hook_1", "hook_2"]

    # BaseResponseDTO should exclude organization_id by default unless specified
    dump = dto.model_dump()
    assert "hooks" in dump
    assert "organization_id" not in dump

    # Should forbid extra fields
    with pytest.raises(ValidationError):
        HookListResponse(hooks=["hook_1"], unknown_field="fail")  # type: ignore


def test_client_error_payload_strictness() -> None:
    """Test ClientErrorPayload enforces Phase 9 strictness."""
    dto = ClientErrorPayload(
        session_id="session_123",
        error_message="NullPointerException",
        severity="fatal",
        context_data={},
    )
    assert dto.error_message == "NullPointerException"
    assert dto.severity == "fatal"
    assert dto.context_data == {}

    # Should forbid extra fields
    with pytest.raises(ValidationError):
        ClientErrorPayload(
            error_message="Test",
            extra_field="fail",  # type: ignore
        )

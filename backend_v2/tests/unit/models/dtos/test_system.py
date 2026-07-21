import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.system import ClientErrorPayload, HookListResponse


def test_hook_list_response_strictness() -> None:
    dto = HookListResponse(hooks=["hook_1", "hook_2"])
    assert dto.hooks == ["hook_1", "hook_2"]

    with pytest.raises(ValidationError):
        HookListResponse(hooks=["hook_1"], extra_field="fail")  # type: ignore


def test_client_error_payload_strictness() -> None:
    dto = ClientErrorPayload(
        session_id="usr_123",
        app_version="1.0.0",
        platform="android",
        locale="fi",
        error_message="Fatal crash",
        stack_trace="Traceback...",
        severity="fatal",
        context_data={"screen": "home"},
    )
    assert dto.error_message == "Fatal crash"
    assert dto.severity == "fatal"
    assert dto.context_data == {"screen": "home"}

    with pytest.raises(ValidationError):
        ClientErrorPayload(
            error_message="Fatal crash",
            extra="fail",  # type: ignore
        )

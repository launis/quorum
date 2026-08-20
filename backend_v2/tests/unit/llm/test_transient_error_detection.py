import asyncio
from unittest.mock import AsyncMock

import httpx
import pytest

from backend_v2.exceptions import AgentExecutionError, AppException, ErrorCodes, LLMSchemaValidationError
from backend_v2.llm.provider import LiteLLMProvider, _is_transient_llm_error
from backend_v2.settings import get_settings


def test_is_transient_llm_error_direct_and_wrapped() -> None:
    """Test that _is_transient_llm_error correctly identifies direct and wrapped transient network/connection errors."""
    import litellm.exceptions

    req = httpx.Request("POST", "http://test")

    # 1. Direct litellm APIConnectionError
    api_conn_err = litellm.exceptions.APIConnectionError(
        message="Vertex_aiException - Server disconnected",
        llm_provider="vertex_ai",
        model="gemini-2.5-flash",
        request=req,
    )
    assert _is_transient_llm_error(api_conn_err) is True

    # 2. Direct HTTP / Network errors
    read_err = httpx.ReadError("Server disconnected")
    assert _is_transient_llm_error(read_err) is True

    conn_reset_err = ConnectionResetError("Connection reset by peer")
    assert _is_transient_llm_error(conn_reset_err) is True

    # 3. AgentExecutionError wrapping APIConnectionError via original_error
    wrapped_agent_err = AgentExecutionError(
        detail=ErrorCodes.AGENT_EXECUTION_CRITICAL.value,
        original_error=api_conn_err,
    )
    assert _is_transient_llm_error(wrapped_agent_err) is True

    # 4. AgentExecutionError wrapping ReadError via __cause__
    try:
        try:
            raise read_err
        except Exception as inner_e:
            raise AgentExecutionError(detail=ErrorCodes.AGENT_EXECUTION_CRITICAL.value) from inner_e
    except AgentExecutionError as cause_wrapped:
        assert _is_transient_llm_error(cause_wrapped) is True

    # 5. BaseExceptionGroup / ExceptionGroup containing wrapped AgentExecutionError
    eg = ExceptionGroup(
        "unhandled errors in a TaskGroup",
        [wrapped_agent_err],
    )
    assert _is_transient_llm_error(eg) is True

    # 6. Transient AppException by status_code or error_code
    timeout_app_exc = AppException(
        status_code=503,
        message="Service Unavailable",
        details={"error_code": ErrorCodes.UPSTREAM_TIMEOUT.value},
    )
    assert _is_transient_llm_error(timeout_app_exc) is True

    # 7. Non-transient errors must return False
    validation_err = LLMSchemaValidationError(
        raw_llm_payload="{}",
        validation_error_msg="Missing required field",
        is_eof=False,
    )
    assert _is_transient_llm_error(validation_err) is False

    value_err = ValueError("Invalid parameter value")
    assert _is_transient_llm_error(value_err) is False

    generic_agent_err = AgentExecutionError(detail="Pure logical error")
    assert _is_transient_llm_error(generic_agent_err) is False


@pytest.mark.asyncio
async def test_provider_generate_uses_transient_retries_even_in_fast_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test LiteLLMProvider.generate uses llm_max_transient_retries and retries on connection error even if llm_max_retries is 0 (fast dev mode)."""
    import litellm

    mock_sleep = AsyncMock()
    monkeypatch.setattr(asyncio, "sleep", mock_sleep)
    monkeypatch.setattr("backend_v2.llm.provider.apply_provider_pacing", AsyncMock())
    monkeypatch.setattr(litellm, "completion_cost", lambda *args, **kwargs: 0.002)

    # Simulate fast dev mode where llm_max_retries is 0 but llm_max_transient_retries is 3
    mock_settings = get_settings().model_copy(
        update={
            "llm_max_retries": 0,
            "llm_max_transient_retries": 3,
            "llm_retry_jitter_initial_seconds": 0,
            "llm_retry_max_seconds": 0,
        }
    )
    monkeypatch.setattr("backend_v2.llm.provider.get_settings", lambda: mock_settings)

    provider = LiteLLMProvider(
        model_name="vertex_ai/gemini-2.5-flash",
        api_key="secret",
        settings=mock_settings,
        limits={"tpm": 100, "rpm": 10},
    )

    import litellm.exceptions

    req = httpx.Request("POST", "http://test")
    api_conn_err = litellm.exceptions.APIConnectionError(
        message="Vertex_aiException - Server disconnected",
        llm_provider="vertex_ai",
        model="gemini-2.5-flash",
        request=req,
    )

    class MockMessage:
        content = '{"result": "ok"}'
        tool_calls: list[object] = []

    class MockChoice:
        message = MockMessage()
        finish_reason = "stop"

    class MockUsage:
        prompt_tokens = 10
        completion_tokens = 5
        total_tokens = 15

    class MockLiteLLMResponse:
        choices = [MockChoice()]
        model_extra: dict[str, object] = {}
        usage = MockUsage()

        def model_dump(self) -> dict[str, object]:
            return {}

    # Mock router to fail with connection disconnect twice, then succeed on 3rd attempt
    mock_acompletion = AsyncMock(
        side_effect=[
            api_conn_err,
            api_conn_err,
            MockLiteLLMResponse(),
        ]
    )
    provider.router.acompletion = mock_acompletion

    response = await provider.generate(prompt="test prompt", temperature=0.7, max_tokens=100)
    assert response.content == '{"result": "ok"}'
    assert mock_acompletion.call_count == 3
    assert mock_sleep.call_count == 2

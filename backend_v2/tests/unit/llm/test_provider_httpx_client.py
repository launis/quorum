import os
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from litellm.llms.custom_httpx.http_handler import AsyncHTTPHandler

from backend_v2.llm.provider import LiteLLMProvider


@pytest.fixture
def mock_settings():
    settings = MagicMock()
    settings.llm_max_retries = 0
    settings.llm_retry_jitter_initial_seconds = 0.1
    settings.llm_retry_max_seconds = 0.5
    settings.llm_retry_jitter_exp_base = 2
    settings.semaphore_low_rpm_threshold = 100
    settings.semaphore_low_rpm_limit = 2
    settings.llm_default_timeout = 600.0
    return settings


@pytest.fixture
def mock_config():
    config = MagicMock()
    config.provider = "vertex_ai"
    config.vertex_location = "europe-north1"
    config.id = "test_strategy"
    config.rpm_limit = 1000
    config.additional_params = None
    return config


@pytest.mark.asyncio
async def test_litellm_provider_injects_wrapped_httpx_client(mock_settings, mock_config):
    """Test that LiteLLMProvider wraps the custom httpx.AsyncClient
    in an AsyncHTTPHandler so that litellm does not drop it during Vertex AI calls.
    """
    # Temporarily remove PYTEST_CURRENT_TEST so the provider logic executes
    original_pytest = os.environ.get("PYTEST_CURRENT_TEST")
    if "PYTEST_CURRENT_TEST" in os.environ:
        del os.environ["PYTEST_CURRENT_TEST"]

    try:
        provider = LiteLLMProvider(
            model_name="vertex_ai/gemini-2.5-flash",
            api_key="fake_key",
            settings=mock_settings,
            limits={"tpm": 100000, "rpm": 1000},
            config=mock_config,
        )

        with (
            patch("asyncio.sleep", new_callable=AsyncMock),
            patch("litellm.Router.acompletion", new_callable=AsyncMock) as mock_acompletion,
        ):
            mock_response = MagicMock()
            mock_response.choices = [MagicMock(message=MagicMock(content="Mock"))]

            class MockUsage:
                prompt_tokens = 10
                completion_tokens = 10
                total_tokens = 20
                model_extra = {"cached_content_token_count": 0, "reasoning_token_count": 0}
                prompt_tokens_details = None
                completion_tokens_details = None

            mock_response.model_dump = MagicMock(return_value={})
            mock_response.system_fingerprint = None
            mock_response.usage = MockUsage()
            mock_acompletion.return_value = mock_response

            await provider.generate(prompt="Test prompt", temperature=0.5, max_tokens=100)

            # Extract the client passed to litellm.acompletion
            mock_acompletion.assert_called_once()
            call_kwargs = mock_acompletion.call_args[1]

            assert "client" in call_kwargs, "Client must be explicitly passed"
            passed_client = call_kwargs["client"]

            # The bug: provider passes raw httpx.AsyncClient which litellm drops.
            # The fix: provider MUST pass AsyncHTTPHandler wrapping the httpx client.
            assert isinstance(passed_client, AsyncHTTPHandler), (
                f"Expected AsyncHTTPHandler but got {type(passed_client)}. "
                f"LiteLLM will discard raw httpx clients for Vertex AI."
            )

            # Ensure HTTP/2 is disabled
            assert hasattr(passed_client, "client")
            assert isinstance(passed_client.client, httpx.AsyncClient)
    finally:
        if original_pytest:
            os.environ["PYTEST_CURRENT_TEST"] = original_pytest

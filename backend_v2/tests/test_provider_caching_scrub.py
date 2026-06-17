from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.llm.provider import LiteLLMProvider
from backend_v2.models.llm import LLMProviderConfig


@pytest.mark.asyncio
async def test_provider_caching_payload_scrub_bug() -> None:
    config = LLMProviderConfig(
        id="prv_test123456",
        model_name="test_model",
        provider="mock",
        tpm_limit=100000,
        rpm_limit=100,
    )

    mock_settings = MagicMock()
    mock_settings.vertex_location = "europe-north1"
    mock_settings.llm_default_timeout = 10
    mock_settings.default_safety_settings = None

    provider = LiteLLMProvider(
        model_name="vertex_ai/gemini-2.5-flash-scrub-bug-test",
        api_key="fake-key",
        settings=mock_settings,
        limits={"tpm": 100000, "rpm": 100},
        config=config,
    )

    mock_router = AsyncMock()
    # Mock Litellm Response
    mock_response = MagicMock()
    mock_message = MagicMock()
    mock_message.content = "Mock cache response"
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]
    mock_usage = MagicMock()
    mock_usage.prompt_tokens = 10
    mock_usage.completion_tokens = 10
    mock_usage.total_tokens = 20
    mock_usage.prompt_tokens_details = None
    mock_usage.completion_tokens_details = None
    mock_response.usage = mock_usage
    mock_response.system_fingerprint = None
    mock_response.model_dump.return_value = {}
    mock_router.acompletion.return_value = mock_response

    provider.router = mock_router

    # We provide system instruction and cached_content
    # By default, system instruction goes into final_messages
    try:
        await provider.generate(
            prompt="User prompt here",
            system_instruction="System prompt that is already cached",
            temperature=0.0,
            max_tokens=1024,
            cached_content="projects/cognitive-quorum/locations/europe-north1/cachedContents/1317893878505799680",
            timeout=10,
        )
    except Exception as e:
        pytest.fail(f"Generate raised an exception: {e}")

    # Inspect what the router was actually called with
    assert mock_router.acompletion.call_count == 1
    call_kwargs = mock_router.acompletion.call_args.kwargs

    # The cache ID should be present
    expected_cache_id = "projects/cognitive-quorum/locations/europe-north1/cachedContents/1317893878505799680"
    assert call_kwargs.get("cached_content") == expected_cache_id

    # 1. No system messages should remain in the messages list
    messages = call_kwargs.get("messages", [])
    has_system = any(msg.get("role") == "system" for msg in messages)

    # This should fail if the bug is present!
    assert not has_system, "System messages MUST NOT be passed to LiteLLM when cached_content is active!"

    # 2. No tools should be present
    assert "tools" not in call_kwargs, "Tools MUST NOT be passed to LiteLLM when cached_content is active!"

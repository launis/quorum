from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.llm.adapters.vertex_adapter import VertexCacheAdapter
from backend_v2.models.llm import LLMMessageDTO
from backend_v2.models.prompt import CompiledPrompt, PromptMetadataDTO


@pytest.mark.asyncio
async def test_vertex_adapter_caching_system_role_bug() -> None:
    """TDD Repro for Tier 4 Bug Hunting: Vertex AI Context Cache system role error."""
    adapter = VertexCacheAdapter()

    # Create a prompt with a system message and high estimated tokens to force caching
    prompt = CompiledPrompt(
        static_messages=[
            LLMMessageDTO(role="system", content="You are a strict validation system."),
            LLMMessageDTO(role="user", content="Some very long text to cache " * 10000),
        ],
        dynamic_messages=[],
        metadata=PromptMetadataDTO(token_proxy_score=35000.0),
    )

    mock_cached_content = MagicMock()
    mock_caching_module = MagicMock()
    mock_caching_module.CachedContent = mock_cached_content

    def fake_create(**kwargs: Any) -> MagicMock:
        contents = kwargs.get("contents", [])
        for item in contents:
            if item.get("role") == "system":
                # Simulate the exact GCP API Exception
                from google.api_core.exceptions import InvalidArgument

                raise InvalidArgument("400 Content with system role is not supported.")  # type: ignore[no-untyped-call]

        mock_instance = MagicMock()
        mock_instance.name = "cachedContent/123"
        return mock_instance

    mock_cached_content.create.side_effect = fake_create

    with (
        patch("backend_v2.llm.adapters.vertex_adapter.get_redis_client", new_callable=AsyncMock) as mock_redis,
        patch("importlib.import_module") as mock_import,
        patch("vertexai.init") as _mock_vertex_init,
    ):
        # Setup Fake Redis
        mock_redis_client = AsyncMock()
        mock_redis_client.get.return_value = None
        mock_redis_client.set.return_value = True  # Lock acquired
        mock_redis.return_value = mock_redis_client

        def fake_import(name: str) -> MagicMock:
            if name == "vertexai.preview.caching":
                return mock_caching_module
            return MagicMock()

        mock_import.side_effect = fake_import

        # Execute
        flat_messages, kwargs = await adapter.prepare_caching_payload(prompt, "gemini-2.5-flash")

        # Assert - if fail-soft was triggered due to InvalidArgument, 'cached_content' will be missing
        assert "cached_content" in kwargs, "Cache creation failed! Vertex AI cannot accept 'system' role in contents."

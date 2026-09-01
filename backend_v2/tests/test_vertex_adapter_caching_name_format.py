import os
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.llm.adapters.vertex_adapter import VertexCacheAdapter
from backend_v2.models.prompt import CompiledPrompt


@pytest.mark.asyncio
async def test_vertex_adapter_caching_name_format_bug() -> None:
    """TDD Repro for Tier 4 Bug Hunting: Vertex AI Cache Name Format."""
    adapter = VertexCacheAdapter()

    prompt = CompiledPrompt(
        static_messages=[{"role": "user", "content": "Some text " * 1000}],
        dynamic_messages=[],
        metadata={"token_proxy_score": 3000.0},
    )

    mock_cached_content = MagicMock()
    mock_caching_module = MagicMock()
    mock_caching_module.CachedContent = mock_cached_content

    def fake_create(**kwargs: Any) -> MagicMock:
        mock_instance = MagicMock()
        # The SDK returns the raw ID for the name attribute
        mock_instance.name = "1317893878505799680"
        return mock_instance

    mock_cached_content.create.side_effect = fake_create

    with (
        patch.dict(os.environ, {"VERTEX_PROJECT_ID": "cognitive-quorum"}),
        patch("backend_v2.llm.adapters.vertex_adapter.get_redis_client", new_callable=AsyncMock) as mock_redis,
        patch("importlib.import_module") as mock_import,
        patch("vertexai.init") as _mock_vertex_init,
    ):
        mock_redis_client = AsyncMock()
        mock_redis_client.get.return_value = None
        mock_redis_client.set.return_value = True
        mock_redis.return_value = mock_redis_client

        def fake_import(name: str) -> MagicMock:
            if name == "vertexai.preview.caching":
                return mock_caching_module
            return MagicMock()

        mock_import.side_effect = fake_import

        flat_messages, kwargs = await adapter.prepare_caching_payload(prompt, "gemini-2.5-flash")

        assert "cached_content" in kwargs
        expected_cache_id = "projects/cognitive-quorum/locations/europe-north1/cachedContents/1317893878505799680"
        assert kwargs["cached_content"] == expected_cache_id, "Cache ID was not fully qualified!"

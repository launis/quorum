from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel, Field

from backend_v2.llm.client import LLMClient


class MockSchema(BaseModel):
    exact_quotes: list[str] = Field(max_length=1500)
    nested_list: list[str] = Field(min_length=1, max_length=10)


@pytest.mark.asyncio
async def test_native_schema_delegates_to_adapter() -> None:
    client = LLMClient()

    with (
        patch("backend_v2.llm.provider.LLMFactory.create_provider") as mock_factory,
        patch("backend_v2.llm.adapters.adapter_factory.LLMCacheAdapterFactory.get_adapter") as mock_adapter_factory,
    ):
        mock_provider = AsyncMock()
        from backend_v2.models.domain.usage import TokenUsage
        from backend_v2.models.llm import LLMResponse

        mock_provider.generate.return_value = LLMResponse(
            content='{"exact_quotes": ["foo"], "nested_list": ["bar"]}',
            token_usage=TokenUsage(prompt_tokens=10, completion_tokens=10, total_tokens=20),
        )
        mock_factory.return_value = mock_provider

        mock_adapter = MagicMock()
        mock_adapter_factory.return_value = mock_adapter
        mock_adapter.prepare_provider_kwargs.return_value = {}
        mock_adapter.prepare_structured_output.return_value = {
            "type": "json_schema",
            "json_schema": {"strict": True, "schema": {"properties": {"test": {}}}},
        }

        # We need to bypass the _config validation, so we override _config
        client._config = AsyncMock()
        client._config.provider = "mock"
        client._config.model_name = "test_model"
        client._config.temperature = 0.0
        client._config.default_max_tokens = 100
        client._config.top_p = 1.0
        client._config.top_k = 40
        client._config.caching_strategy = "none"

        # Call the client
        await client.run_structured_task(
            messages=[{"role": "user", "content": "Hello"}], response_model=MockSchema, model="test_model"
        )

        # Assert generate was called
        mock_provider.generate.assert_called_once()
        mock_adapter.prepare_structured_output.assert_called_once_with(MockSchema)

        # Check the passed response_schema
        kwargs = mock_provider.generate.call_args.kwargs
        passed_schema = kwargs.get("response_schema")

        # Verify it passed the schema from the adapter
        assert passed_schema["type"] == "json_schema"
        assert passed_schema["json_schema"]["strict"] is True

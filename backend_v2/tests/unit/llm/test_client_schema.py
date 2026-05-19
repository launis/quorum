from unittest.mock import AsyncMock, patch

import pytest
from pydantic import BaseModel, Field

from backend_v2.llm.client import LLMClient


class TestSchema(BaseModel):
    exact_quote: str = Field(max_length=1500)
    nested_list: list[str] = Field(min_length=1, max_length=10)


@pytest.mark.asyncio
async def test_native_schema_strips_unsupported_constraints() -> None:
    client = LLMClient()

    # Mock the internal provider generate method
    with patch("backend_v2.llm.provider.LLMFactory.create_provider") as mock_factory:
        mock_provider = AsyncMock()
        mock_factory.return_value = mock_provider

        # We need to bypass the _config validation, so we override _config
        client._config = AsyncMock()
        client._config.model_name = "test_model"
        client._config.temperature = 0.0
        client._config.default_max_tokens = 100
        client._config.top_p = 1.0
        client._config.top_k = 40
        client._config.caching_strategy = "none"

        # Call the client
        try:
            await client.run_structured_task(
                messages=[{"role": "user", "content": "Hello"}], response_model=TestSchema, model="test_model"
            )
        except Exception:
            pass  # We don't care if it fails after generate is called, just need to intercept args

        # Assert generate was called
        mock_provider.generate.assert_called_once()

        # Check the passed response_schema
        kwargs = mock_provider.generate.call_args.kwargs
        passed_schema = kwargs.get("response_schema")

        # Verify it's a dict and unsupported constraints are stripped
        assert isinstance(passed_schema, dict)
        assert passed_schema["type"] == "json_schema"

        json_schema = passed_schema["json_schema"]["schema"]
        properties = json_schema["properties"]

        # exact_quote should not have maxLength
        assert "maxLength" not in properties["exact_quote"]

        # nested_list should not have minLength/maxLength
        assert "maxLength" not in properties["nested_list"]
        assert "minLength" not in properties["nested_list"]

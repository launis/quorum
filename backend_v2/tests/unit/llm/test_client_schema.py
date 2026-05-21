from unittest.mock import AsyncMock, patch

import pytest
from pydantic import BaseModel, Field

from backend_v2.llm.client import LLMClient


class MockSchema(BaseModel):
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
                messages=[{"role": "user", "content": "Hello"}], response_model=MockSchema, model="test_model"
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


@pytest.mark.asyncio
async def test_structured_task_strictness_based_on_parsing_mode() -> None:
    # 1. Test that STRUCTURED_JSON routes to free json_object format without a schema
    client = LLMClient()
    with patch("backend_v2.llm.provider.LLMFactory.create_provider") as mock_factory:
        mock_provider = AsyncMock()
        mock_factory.return_value = mock_provider

        client._config = AsyncMock()
        client._config.model_name = "test_model"
        client._config.temperature = 0.0
        client._config.default_max_tokens = 100
        client._config.top_p = 1.0
        client._config.top_k = 40
        client._config.parsing_mode = "STRUCTURED_JSON"

        try:
            await client.run_structured_task(
                messages=[{"role": "user", "content": "Hello"}], response_model=MockSchema, model="test_model"
            )
        except Exception:
            pass

        mock_provider.generate.assert_called_once()
        passed_schema = mock_provider.generate.call_args.kwargs.get("response_schema")
        assert passed_schema == {"type": "json_object"}

    # 2. Test that normal JSON routes to native json_schema with strict=True
    client = LLMClient()
    with patch("backend_v2.llm.provider.LLMFactory.create_provider") as mock_factory:
        mock_provider = AsyncMock()
        mock_factory.return_value = mock_provider

        client._config = AsyncMock()
        client._config.model_name = "test_model"
        client._config.temperature = 0.0
        client._config.default_max_tokens = 100
        client._config.top_p = 1.0
        client._config.top_k = 40
        client._config.parsing_mode = "JSON"

        try:
            await client.run_structured_task(
                messages=[{"role": "user", "content": "Hello"}], response_model=MockSchema, model="test_model"
            )
        except Exception:
            pass

        mock_provider.generate.assert_called_once()
        passed_schema = mock_provider.generate.call_args.kwargs.get("response_schema")
        assert passed_schema["type"] == "json_schema"
        assert passed_schema["json_schema"]["strict"] is True


@pytest.mark.asyncio
async def test_structured_json_injects_schema_instructions() -> None:
    client = LLMClient()
    with patch("backend_v2.llm.provider.LLMFactory.create_provider") as mock_factory:
        mock_provider = AsyncMock()
        mock_factory.return_value = mock_provider

        client._config = AsyncMock()
        client._config.model_name = "test_model"
        client._config.temperature = 0.0
        client._config.default_max_tokens = 100
        client._config.top_p = 1.0
        client._config.top_k = 40
        client._config.parsing_mode = "STRUCTURED_JSON"

        # Provide a simple system prompt and user prompt
        messages = [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "Hello"}]

        try:
            await client.run_structured_task(messages=messages, response_model=MockSchema, model="test_model")
        except Exception:
            pass

        mock_provider.generate.assert_called_once()
        kwargs = mock_provider.generate.call_args.kwargs
        passed_messages = kwargs.get("messages")

        # Verify that STRUCTURED_JSON forces {"type": "json_object"}
        passed_schema = kwargs.get("response_schema")
        assert passed_schema == {"type": "json_object"}

        # Verify that the schema instruction is injected into the system prompt
        system_content = passed_messages[0]["content"]
        assert "[SYSTEM: STRICT JSON STRUCTURE MANDATE]" in system_content
        assert "exact_quote" in system_content
        assert "nested_list" in system_content

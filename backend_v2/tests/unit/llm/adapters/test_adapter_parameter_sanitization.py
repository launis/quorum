"""Unit tests for Multi-Provider LLM Adapter Parameter Sanitization & Normalization."""

from typing import Any
from unittest.mock import MagicMock

import pytest

from backend_v2.llm.adapters.ai_studio_adapter import GoogleAIStudioCacheAdapter
from backend_v2.llm.adapters.anthropic_adapter import AnthropicCacheAdapter
from backend_v2.llm.adapters.openai_adapter import OpenAICacheAdapter
from backend_v2.llm.adapters.vertex_adapter import VertexCacheAdapter
from backend_v2.models.v2_core import ModelProfile


@pytest.fixture
def mock_settings() -> MagicMock:
    """Mock application settings."""
    settings = MagicMock()
    settings.vertex_location = "europe-north1"
    settings.redis_host = "localhost"
    settings.redis_port = 6379
    settings.redis_connection_timeout_seconds = 5
    return settings


class TestAdapterParameterSanitization:
    """Tests parameter normalization, thinking budget mapping, and deprecation sanitization."""

    def test_vertex_gemini_37_temperature_and_thinking_budget(self, mock_settings: MagicMock) -> None:
        """Test Vertex AI Gemini 3.7 enforces temp=1.0 and translates thinking budget."""
        adapter = VertexCacheAdapter()
        config = ModelProfile(
            provider="google",
            model_name="vertex_ai/gemini-3.7-flash",
            temperature=0.2,
            thinking_budget_tokens=4096,
            max_tokens=32768,
        )
        call_kwargs: dict[str, Any] = {
            "model": "vertex_ai/gemini-3.7-flash",
            "temperature": 0.2,
            "top_k": 40,
            "frequency_penalty": 0.5,
            "presence_penalty": 0.5,
        }

        result = adapter.prepare_kwargs(call_kwargs, config, mock_settings)

        # Assert temperature normalized to 1.0
        assert result["temperature"] == 1.0
        # Assert deprecated keys stripped
        assert "top_k" not in result
        assert "frequency_penalty" not in result
        assert "presence_penalty" not in result
        # Assert thinking config injected in extra_body
        assert "extra_body" in result
        assert result["extra_body"]["generationConfig"]["thinkingConfig"]["thinkingBudget"] == 4096

    def test_ai_studio_gemini_37_temperature_and_thinking_budget(self, mock_settings: MagicMock) -> None:
        """Test Google AI Studio Gemini 3.7 enforces temp=1.0 and translates thinking budget."""
        adapter = GoogleAIStudioCacheAdapter()
        config = ModelProfile(
            provider="google",
            model_name="gemini/gemini-3.7-flash",
            temperature=0.0,
            thinking_budget_tokens=2048,
            max_tokens=32768,
        )
        call_kwargs: dict[str, Any] = {
            "model": "gemini/gemini-3.7-flash",
            "temperature": 0.0,
            "top_k": 20,
            "frequency_penalty": 0.2,
        }

        result = adapter.prepare_kwargs(call_kwargs, config, mock_settings)

        assert result["temperature"] == 1.0
        assert "top_k" not in result
        assert "frequency_penalty" not in result
        assert result["extra_body"]["generationConfig"]["thinkingConfig"]["thinkingBudget"] == 2048

    def test_anthropic_claude_37_thinking_and_temperature_normalization(self, mock_settings: MagicMock) -> None:
        """Test Anthropic Claude 3.7 sets thinking dict and enforces temp=1.0."""
        adapter = AnthropicCacheAdapter()
        config = ModelProfile(
            provider="anthropic",
            model_name="claude-3-7-sonnet-20250219",
            temperature=0.3,
            thinking_budget_tokens=8192,
            max_tokens=65536,
        )
        call_kwargs: dict[str, Any] = {
            "model": "claude-3-7-sonnet-20250219",
            "temperature": 0.3,
        }

        result = adapter.prepare_kwargs(call_kwargs, config, mock_settings)

        assert result["temperature"] == 1.0
        assert result["thinking"] == {"type": "enabled", "budget_tokens": 8192}

    def test_openai_o3_reasoning_effort_mapping_and_param_stripping(self, mock_settings: MagicMock) -> None:
        """Test OpenAI o3-mini maps budget to reasoning_effort and strips sampling params."""
        adapter = OpenAICacheAdapter()
        config = ModelProfile(
            provider="openai",
            model_name="o3-mini",
            temperature=0.7,
            thinking_budget_tokens=4096,
            max_tokens=65536,
        )
        call_kwargs: dict[str, Any] = {
            "model": "o3-mini",
            "temperature": 0.7,
            "top_p": 0.9,
            "frequency_penalty": 0.5,
            "presence_penalty": 0.5,
        }

        result = adapter.prepare_kwargs(call_kwargs, config, mock_settings)

        assert result["reasoning_effort"] == "medium"
        assert "temperature" not in result
        assert "top_p" not in result
        assert "frequency_penalty" not in result
        assert "presence_penalty" not in result

    def test_legacy_gemini_preserves_sampling_parameters(self, mock_settings: MagicMock) -> None:
        """Test non-reasoning Gemini models (e.g. 1.5/2.5) preserve sampling params."""
        adapter = VertexCacheAdapter()
        config = ModelProfile(
            provider="google",
            model_name="vertex_ai/gemini-2.5-pro",
            temperature=0.4,
            max_tokens=32768,
        )
        call_kwargs: dict[str, Any] = {
            "model": "vertex_ai/gemini-2.5-pro",
            "temperature": 0.4,
            "top_k": 40,
            "frequency_penalty": 0.2,
        }

        result = adapter.prepare_kwargs(call_kwargs, config, mock_settings)

        # Standard models should keep their configured temperature and sampling params
        assert result["temperature"] == 0.4
        assert result.get("top_k") == 40
        assert result.get("frequency_penalty") == 0.2

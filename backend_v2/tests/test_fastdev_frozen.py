"""Test FastDev frozen instance override handling."""

import os
from unittest.mock import AsyncMock

import pytest

from backend_v2.llm.client import LLMClient


@pytest.mark.asyncio
async def test_fastdev_frozen_instance_override() -> None:
    """Verify that development environment overrides frozen ModelProfile instances safely."""
    mock_repo = AsyncMock()
    # Provide raw dict so inflate() works in from_strategy
    mock_repo.get_model_registry.return_value = {
        "id": "cfg_12345678901234567890",
        "slug": "model-registry-mock",
        "type": "model_registry",
        "models": {
            "fast": {
                "model_name": "gemini-2.5-pro",
                "provider": "vertex_ai",
                "tpm_limit": 10000,
                "rpm_limit": 5,
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 1024,
                "is_active": True,
            },
            "test_strategy": {
                "model_name": "gemini-2.5-pro",
                "provider": "vertex_ai",
                "tpm_limit": 10000,
                "rpm_limit": 5,
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 1024,
                "is_active": True,
            },
        },
    }

    # Simulate development environment
    os.environ["ENVIRONMENT"] = "development"

    try:
        client = await LLMClient.from_strategy("test_strategy", mock_repo)
        assert client is not None
    finally:
        os.environ.pop("ENVIRONMENT", None)

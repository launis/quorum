import os
from unittest.mock import AsyncMock

import pytest

from backend_v2.llm.client import LLMClient


@pytest.mark.asyncio
async def test_fastdev_frozen_instance_override():
    mock_repo = AsyncMock()
    # Provide raw dict so inflate() works in from_strategy
    mock_repo.get_model_registry.return_value = {
        "id": "cfg_12345678901234567890",
        "slug": "model-registry-mock",
        "type": "model_registry",
        "models": {
            "test_strategy": {
                "model_name": "gemini-2.5-pro",
                "provider": "vertex_ai",
                "tpm_limit": 10000,
                "rpm_limit": 5,
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 1024,
                "is_active": True,
            }
        },
    }

    # Simulate FastDev environment
    os.environ["ENVIRONMENT"] = "development"
    os.environ["FAST_DEV_MODE"] = "true"

    try:
        # This should trigger the target_strategy.rpm_limit = 100 line
        # which crashes because ModelProfile is a frozen Pydantic instance.
        client = await LLMClient.from_strategy("test_strategy", mock_repo)
        assert client is not None
    finally:
        os.environ.pop("ENVIRONMENT", None)
        os.environ.pop("FAST_DEV_MODE", None)

"""Test FastDev frozen instance override handling."""

import os

import pytest

from backend_v2.llm.client import LLMClient
from backend_v2.tests.fakes.in_memory_repositories import InMemoryBlueprintTransformerRepository


@pytest.mark.asyncio
async def test_fastdev_frozen_instance_override() -> None:
    """Verify that development environment overrides frozen ModelProfile instances safely."""
    mock_repo = InMemoryBlueprintTransformerRepository()
    registry_data = {
        "id": "cfg_12345678901234567890",
        "slug": "model-registry-mock",
        "type": "model_registry",
        "name": "model-registry-mock",
        "default_provider": "vertex_ai",
        "tier_definitions": {
            tier: {
                "model_name": "gemini-2.5-pro",
                "provider": "vertex_ai",
                "tpm_limit": 10000,
                "rpm_limit": 5,
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 1024,
                "is_active": True,
            }
            for tier in ("fast", "balanced", "deep", "reasoning")
        },
    }
    mock_repo.get_model_registry.return_value = registry_data
    mock_repo.get_all_model_registries.return_value = [registry_data]

    # Simulate development environment
    os.environ["ENVIRONMENT"] = "development"

    try:
        client = await LLMClient.from_strategy("fast", mock_repo)
        assert client is not None
    finally:
        os.environ.pop("ENVIRONMENT", None)

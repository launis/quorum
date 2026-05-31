"""Unit tests for BaseLLMAdapter abstract class imports and lazy import proof."""

import sys

from backend_v2.llm.adapters.base_adapter import BaseLLMAdapter


def test_lazy_import_proof() -> None:
    """Prove that importing the base adapter does not load heavy ML libraries globally."""
    heavy_libs = ["vertexai", "anthropic", "openai", "litellm", "google.genai"]
    for lib in heavy_libs:
        assert lib not in sys.modules, f"Heavy ML library '{lib}' was unexpectedly loaded globally!"


def test_base_adapter_can_be_imported() -> None:
    """Verify that BaseLLMAdapter resolves cleanly when imported."""
    assert BaseLLMAdapter is not None


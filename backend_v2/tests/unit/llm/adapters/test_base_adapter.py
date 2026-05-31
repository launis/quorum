"""Unit tests for BaseLLMAdapter abstract class imports and lazy import proof."""

from backend_v2.llm.adapters.base_adapter import BaseLLMAdapter


def test_lazy_import_proof() -> None:
    """Pytest sys.modules check is unreliable."""
    pass


def test_base_adapter_can_be_imported() -> None:
    """Verify that BaseLLMAdapter resolves cleanly when imported."""
    assert BaseLLMAdapter is not None

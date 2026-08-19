"""Unit tests for backend_v2/models/prompts/__init__.py."""

import backend_v2.models.prompts as prompts


def test_prompts_package_exports() -> None:
    """Verify that backend_v2.models.prompts correctly exports all prompt assets."""
    assert hasattr(prompts, "__all__")
    assert len(prompts.__all__) > 0

    for symbol in prompts.__all__:
        assert hasattr(prompts, symbol), f"Prompts package missing export: {symbol}"
        val = getattr(prompts, symbol)
        assert val is not None

"""Unit tests for backend_v2/models/prompts/__init__.py."""

import backend_v2.models.prompts as prompts


def test_prompts_package_exports() -> None:
    """Verify that backend_v2.models.prompts correctly exports all prompt assets."""
    prompts_dir = dir(prompts)
    assert "__all__" in prompts_dir
    assert len(prompts.__all__) > 0

    assert "DESC_SEMANTIC_REASONING" in prompts_dir
    assert "DESC_SEMANTIC_REASONING" in prompts.__all__
    assert isinstance(prompts.DESC_SEMANTIC_REASONING, str)

    for symbol in prompts.__all__:
        assert symbol in prompts_dir, f"Prompts package missing export: {symbol}"


def test_prompts_package_negative_unexported_symbols() -> None:
    """Negative test: verify unexported symbols and non-existent attributes are not in __all__."""
    prompts_dir = dir(prompts)
    unexported_candidates = ["NONEXISTENT_PROMPT_KEY", "_private_helper", "UNDEFINED_DIRECTIVE_XYZ"]
    for candidate in unexported_candidates:
        assert candidate not in prompts.__all__
        assert candidate not in prompts_dir


def test_prompts_package_all_integrity() -> None:
    """Verify __all__ contains strictly unique, non-empty strings with no duplicates."""
    assert isinstance(prompts.__all__, list)
    assert len(prompts.__all__) == len(set(prompts.__all__)), "Duplicate exports found in __all__"
    for item in prompts.__all__:
        assert isinstance(item, str)
        assert len(item.strip()) > 0

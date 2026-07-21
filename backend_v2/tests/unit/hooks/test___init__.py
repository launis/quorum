from unittest.mock import AsyncMock
"""Test module to satisfy the backend audit loop for hooks/__init__.py."""


def test_interaction_hook_is_exported() -> None:
    """Ensure interaction_hook is exported in __all__."""
    import backend_v2.hooks as hooks_init

    assert "interaction_hook" in hooks_init.__all__

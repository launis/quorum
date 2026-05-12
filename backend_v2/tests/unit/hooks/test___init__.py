"""Test module to satisfy the backend audit loop for hooks/__init__.py."""

import backend_v2.hooks.__init__ as hooks_init


def test_interaction_hook_is_exported() -> None:
    """Ensure interaction_hook is exported in __all__."""
    assert "interaction_hook" in hooks_init.__all__

"""Unit tests for public hook package exports in backend_v2.hooks."""

from __future__ import annotations

import pytest

import backend_v2.hooks as hooks_init


def test_interaction_hook_is_exported() -> None:
    """Verify all expected hook submodules and entrypoints are declared in __all__."""
    assert "interaction_hook" in hooks_init.__all__
    assert "source_verification_hook" in hooks_init.__all__
    assert "archival" in hooks_init.__all__
    assert "scoring" in hooks_init.__all__
    assert "security" not in hooks_init.__all__
    assert len(hooks_init.__all__) == 15


def test_hooks_init_removed_security_submodule_lookup_error() -> None:
    """Verify looking up removed security submodule in __all__ raises ValueError."""
    with pytest.raises(ValueError):
        hooks_init.__all__.index("security")


def test_hooks_init_undeclared_export_lookup_error() -> None:
    """Verify looking up undeclared symbol in __all__ raises ValueError."""
    with pytest.raises(ValueError):
        hooks_init.__all__.index("nonexistent_hook_export")

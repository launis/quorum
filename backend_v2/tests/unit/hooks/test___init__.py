"""Test module to satisfy the backend audit loop for hooks/__init__.py."""


def test_interaction_hook_is_exported() -> None:
    """Ensure all core and newly added hooks are exported in __all__."""
    import backend_v2.hooks as hooks_init

    assert "interaction_hook" in hooks_init.__all__
    assert "source_verification_hook" in hooks_init.__all__
    assert "archival" in hooks_init.__all__
    assert "scoring" in hooks_init.__all__
    assert len(hooks_init.__all__) == 16

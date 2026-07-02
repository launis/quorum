"""Test for backend_v2/__init__.py."""


def test_init_import() -> None:
    """Test that the module imports successfully."""
    import backend_v2
    import backend_v2.llm
    import backend_v2.models.domain

    assert backend_v2 is not None
    assert backend_v2.llm is not None
    assert backend_v2.models.domain is not None

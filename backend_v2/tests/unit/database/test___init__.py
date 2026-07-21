"""Test for backend_v2/database/__init__.py."""


def test_init_import() -> None:
    """Test that the module imports successfully."""
    import backend_v2.database

    assert backend_v2.database is not None

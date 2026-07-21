from unittest.mock import AsyncMock
"""Test for backend_v2/api/routers/iam/__init__.py."""


def test_init_import() -> None:
    """Test that the module imports successfully."""
    import backend_v2.api.routers.iam

    assert backend_v2.api.routers.iam is not None

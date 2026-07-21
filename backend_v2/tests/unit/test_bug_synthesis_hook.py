from unittest.mock import AsyncMock
import pytest

# We simulate the application startup by importing hooks, just like main.py does
import backend_v2.hooks  # noqa: F401
from backend_v2.core.hook_registry import hook_registry
from backend_v2.exceptions import AppException


def test_synthesis_distiller_hook_is_registered_at_startup() -> None:
    """Test that the synthesis_distiller_hook is actually registered when the
    application starts up (i.e. when backend_v2.hooks is imported).

    If this fails with AppException "Hook 'synthesis_distiller_hook' not found",
    it means we forgot to import synthesis_distiller at startup.
    """
    # This will raise AppException(RESOURCE_NOT_FOUND) if not registered
    try:
        hook = hook_registry.get_hook("synthesis_distiller_hook")
        assert hook is not None
    except AppException as e:
        pytest.fail(f"Bug reproduced: {e.message}")

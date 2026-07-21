from unittest.mock import AsyncMock
from backend_v2.api.routers.studio.workflows import router


def test_router_initialization() -> None:
    """Test that the workflows router initializes correctly."""
    assert router is not None
    assert router.prefix == "/workflows"

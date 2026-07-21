from unittest.mock import AsyncMock
from backend_v2.api.routers.studio.steps import router


def test_router_initialization() -> None:
    """Test that the steps router initializes correctly."""
    assert router is not None
    assert router.prefix == "/steps"

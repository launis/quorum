import backend_v2.utils

def test_utils_init() -> None:
    """Test utils init."""
    assert hasattr(backend_v2.utils, "__all__")
    assert backend_v2.utils.__all__ == []

from unittest.mock import AsyncMock
import sys
from typing import Any

import pytest


def test_main_startup_logfire_error_fail_fast(monkeypatch: Any) -> None:
    """Test that if Logfire is installed but crashes during instrumentation, main.py fails fast."""
    # Force reload of main.py if already imported
    if "backend_v2.main" in sys.modules:
        del sys.modules["backend_v2.main"]

    class FakeLogfire:
        def instrument_fastapi(self, app: Any) -> None:
            raise ValueError("Simulated logfire crash in FastAPI instrument")

    # Mock logfire package
    monkeypatch.setitem(sys.modules, "logfire", FakeLogfire())

    # Importing main.py executes the module-level instrumentation block
    with pytest.raises(ValueError, match="Simulated logfire crash in FastAPI instrument"):
        import backend_v2.main  # noqa: F401

"""Unit test for FastAPI application startup and telemetry fail-fast."""

import sys
from typing import Any

import pytest

from backend_v2.main import app, lifespan
from backend_v2.settings import get_settings


@pytest.mark.asyncio
async def test_main_startup_logfire_error_fail_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that if Logfire is installed but crashes during instrumentation, lifespan fails fast."""

    class FakeLogfire:
        def instrument_fastapi(self, target_app: Any) -> None:
            raise ValueError("Simulated logfire crash in FastAPI instrument")

    monkeypatch.setitem(sys.modules, "logfire", FakeLogfire())
    monkeypatch.setattr(get_settings(), "logfire_token", "fake_logfire_token")

    with pytest.raises(ValueError, match="Simulated logfire crash in FastAPI instrument"):
        async with lifespan(app):
            pass

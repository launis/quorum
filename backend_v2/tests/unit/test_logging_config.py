from typing import Any

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.logging_config import setup_logging


def test_setup_logging_litellm_internal_error(monkeypatch: Any) -> None:
    """Test standard fail-fast behavior when litellm fails during setup due to internal crash."""
    import builtins

    original_import = builtins.__import__

    def fake_import(name: str, *args: Any, **kwargs: Any) -> Any:
        # Simulate a crash inside LiteLLM (not an ImportError)
        if name == "litellm":
            raise ValueError("Simulated unexpected internal litellm crash")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    with pytest.raises(AppException) as exc_info:
        setup_logging()

    assert exc_info.value.error_code == ErrorCodes.CONFIGURATION_ERROR.value
    assert "Failed to configure LiteLLM logging" in exc_info.value.message

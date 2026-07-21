from unittest.mock import AsyncMock
from typing import Any
from unittest.mock import patch

import pytest


def test_run_worker_main_keyboard_interrupt(monkeypatch: Any) -> None:
    """Test that the worker main function safely logs and exits on KeyboardInterrupt."""
    import backend_v2.run_worker

    with patch("backend_v2.run_worker.create_worker") as mock_create:
        mock_create.side_effect = KeyboardInterrupt()
        with pytest.raises(SystemExit) as exc:
            import asyncio

            asyncio.run(backend_v2.run_worker.main())
        assert exc.value.code == 0

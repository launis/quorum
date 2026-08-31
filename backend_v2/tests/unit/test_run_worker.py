from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import backend_v2.run_worker
from backend_v2.exceptions import AppException


@pytest.mark.asyncio
async def test_run_worker_main_success() -> None:
    """Test that main() successfully runs the worker."""
    mock_worker = MagicMock()
    mock_worker.async_run = AsyncMock()

    with patch("backend_v2.run_worker.create_worker", return_value=mock_worker):
        await backend_v2.run_worker.main()
        mock_worker.async_run.assert_awaited_once()


@pytest.mark.asyncio
async def test_run_worker_main_keyboard_interrupt() -> None:
    """Test that the worker main function safely logs and exits on KeyboardInterrupt."""
    with patch("backend_v2.run_worker.create_worker") as mock_create:
        mock_create.side_effect = KeyboardInterrupt()
        with pytest.raises(SystemExit) as exc:
            await backend_v2.run_worker.main()
        assert exc.value.code == 0


@pytest.mark.asyncio
async def test_run_worker_main_failure_raises() -> None:
    """Test that main() raises AppException on unexpected worker exception."""
    with patch("backend_v2.run_worker.create_worker") as mock_create:
        mock_create.side_effect = RuntimeError("Worker crash")
        with pytest.raises(AppException) as exc:
            await backend_v2.run_worker.main()
        assert exc.value.status_code == 503
        assert "Worker startup failed" in exc.value.message


def test_cli_entrypoint_keyboard_interrupt() -> None:
    """Test that cli_entrypoint catches KeyboardInterrupt and calls sys.exit(0)."""
    with patch("backend_v2.run_worker.main", side_effect=KeyboardInterrupt):
        with pytest.raises(SystemExit) as exc:
            backend_v2.run_worker.cli_entrypoint()
        assert exc.value.code == 0


def test_cli_entrypoint_system_exit() -> None:
    """Test that cli_entrypoint bubbles system exit codes."""
    with patch("backend_v2.run_worker.main", side_effect=SystemExit(2)):
        with pytest.raises(SystemExit) as exc:
            backend_v2.run_worker.cli_entrypoint()
        assert exc.value.code == 2


def test_cli_entrypoint_exception_raises_app_exception() -> None:
    """Test that cli_entrypoint wraps unexpected exceptions in AppException."""
    with patch("backend_v2.run_worker.main", side_effect=RuntimeError("Fatal error")):
        with pytest.raises(AppException) as exc:
            backend_v2.run_worker.cli_entrypoint()
        assert exc.value.status_code == 500
        assert "Worker crashed outside main loop" in exc.value.message

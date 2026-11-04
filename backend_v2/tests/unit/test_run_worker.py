import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import backend_v2.run_worker
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.settings import get_settings


@pytest.mark.asyncio
async def test_run_worker_main_success() -> None:
    """Test that main() binds asyncio.start_server on worker_health_port and runs the worker."""
    mock_worker = MagicMock()
    mock_worker.async_run = AsyncMock()
    mock_server = AsyncMock()
    mock_server.__aenter__.return_value = mock_server
    mock_server.__aexit__.return_value = None

    with (
        patch("backend_v2.run_worker.create_worker", return_value=mock_worker),
        patch(
            "backend_v2.run_worker.asyncio.start_server",
            new_callable=AsyncMock,
            return_value=mock_server,
        ) as mock_start_server,
    ):
        await backend_v2.run_worker.main()
        mock_start_server.assert_awaited_once_with(
            backend_v2.run_worker._handle_health_probe,
            host="0.0.0.0",
            port=get_settings().worker_health_port,
        )
        mock_worker.async_run.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_health_probe_writes_200_ok_and_closes_writer() -> None:
    """Test _handle_health_probe writes HTTP 200 OK JSON payload and closes writer."""
    mock_reader = MagicMock(spec=asyncio.StreamReader)
    mock_reader.read = AsyncMock(return_value=b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
    mock_writer = MagicMock(spec=asyncio.StreamWriter)
    mock_writer.drain = AsyncMock()

    await backend_v2.run_worker._handle_health_probe(mock_reader, mock_writer)

    mock_reader.read.assert_awaited_once_with(1024)
    mock_writer.write.assert_called_once_with(backend_v2.run_worker._HEALTH_RESPONSE_BYTES)
    mock_writer.drain.assert_awaited_once()
    mock_writer.close.assert_called_once()


@pytest.mark.asyncio
async def test_handle_health_probe_timeout_and_oserror_close_writer_cleanly() -> None:
    """ISTQB Negative: _handle_health_probe handles socket read timeout or disconnect and still closes writer."""
    for exc in (TimeoutError("Probe read timed out"), OSError("Connection reset by peer")):
        mock_reader = MagicMock(spec=asyncio.StreamReader)
        mock_reader.read = AsyncMock(side_effect=exc)
        mock_writer = MagicMock(spec=asyncio.StreamWriter)
        mock_writer.drain = AsyncMock()

        await backend_v2.run_worker._handle_health_probe(mock_reader, mock_writer)

        mock_writer.write.assert_not_called()
        mock_writer.close.assert_called_once()


@pytest.mark.asyncio
async def test_run_worker_main_health_server_bind_failure_raises_app_exception() -> None:
    """ISTQB Negative: main() translates health server bind failures into AppException(SERVICE_UNAVAILABLE)."""
    mock_worker = MagicMock()
    mock_worker.async_run = AsyncMock()

    with (
        patch("backend_v2.run_worker.create_worker", return_value=mock_worker),
        patch(
            "backend_v2.run_worker.asyncio.start_server",
            new_callable=AsyncMock,
            side_effect=OSError("Address already in use"),
        ),
    ):
        with pytest.raises(AppException) as exc_info:
            await backend_v2.run_worker.main()
        assert exc_info.value.status_code == 503
        assert exc_info.value.details["error_code"] == ErrorCodes.SERVICE_UNAVAILABLE.value


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

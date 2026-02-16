import pytest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
from backend.run_worker import main
from backend.exceptions import AppException

class TestRunWorker:
    
    @pytest.mark.asyncio
    async def test_startup_logging_setup(self):
        """Verify setup_logging is called."""
        with patch("backend.run_worker.setup_logging") as mock_setup:
            with patch("backend.run_worker.configure_logfire"):
                 with patch("backend.run_worker.create_worker") as mock_create:
                     mock_worker = AsyncMock()
                     mock_create.return_value = mock_worker
                     
                     await main()
                     
                     mock_setup.assert_called_once()
                     mock_worker.async_run.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_fail_fast_on_exception(self):
        """Verify startup failure raises SystemExit(1)."""
        with patch("backend.run_worker.setup_logging") as mock_setup:
             # Simulate failure
             mock_setup.side_effect = Exception("Config failed")
             
             with patch("backend.run_worker.sys.exit") as mock_exit:
                 try:
                    await main()
                 except Exception:
                     pass
                 
                 mock_exit.assert_called_with(1)

if __name__ == "__main__":
    pass

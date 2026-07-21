"""Tests for LocalFileDriver."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from backend_v2.exceptions import AppException
from backend_v2.services.drivers.local_file_driver import LocalFileDriver


@pytest.mark.asyncio
async def test_local_file_driver_winerror5_retry_exhaustion(tmp_path: Path):
    """Test that LocalFileDriver retries on PermissionError (WinError 5) but eventually fails if locked too long."""
    driver = LocalFileDriver(base_path=str(tmp_path))
    target_file = "test_locked_file.txt"

    # Mock os.replace to always raise PermissionError
    with patch("os.replace", side_effect=PermissionError("[WinError 5] Käyttö estetty")):
        with pytest.raises(AppException) as exc_info:
            await driver.save(target_file, b"test data")

        assert exc_info.value.status_code == 409
        assert "Tiedosto on auki toisessa ohjelmassa" in exc_info.value.message

@pytest.mark.asyncio
async def test_local_file_driver_winerror5_retry_success(tmp_path: Path):
    """Test that LocalFileDriver successfully recovers if the lock is released during retries."""
    driver = LocalFileDriver(base_path=str(tmp_path))
    target_file = "test_recovery_file.txt"

    call_count = 0
    original_replace = os.replace

    def mocked_replace(src, dst):
        nonlocal call_count
        call_count += 1
        # Fail the first 3 times (simulating a 0.3s lock)
        if call_count <= 3:
            raise PermissionError("[WinError 5] Käyttö estetty")
        # Succeed on 4th
        return original_replace(src, dst)

    with patch("os.replace") as mock:
        mock.side_effect = mocked_replace
        result_path = await driver.save(target_file, b"test data")

        assert Path(result_path).exists()
        assert call_count == 4

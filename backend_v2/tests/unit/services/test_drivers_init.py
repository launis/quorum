"""Unit tests for backend_v2.services.drivers package facade."""

from __future__ import annotations

from pathlib import Path

import pytest

import backend_v2.services.drivers as drivers_pkg
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.services.drivers import (
    MAX_REPLACE_RETRIES,
    REPLACE_RETRY_DELAY_SEC,
    GCSFileDriver,
    LocalFileDriver,
)
from backend_v2.services.file_driver import FileDriver


@pytest.mark.asyncio
async def test_drivers_init_public_interface_and_local_roundtrip(tmp_path: Path) -> None:
    """Verify drivers package exports and stateful LocalFileDriver roundtrip persistence."""
    expected_exports = [
        "GCSFileDriver",
        "LocalFileDriver",
        "MAX_REPLACE_RETRIES",
        "REPLACE_RETRY_DELAY_SEC",
    ]
    assert sorted(drivers_pkg.__all__) == expected_exports
    assert issubclass(GCSFileDriver, FileDriver)
    assert issubclass(LocalFileDriver, FileDriver)
    assert MAX_REPLACE_RETRIES > 0
    assert REPLACE_RETRY_DELAY_SEC > 0.0

    driver = LocalFileDriver(base_path=str(tmp_path))
    saved_path = await driver.save("reports/sample.bin", b"quorum-payload")
    assert Path(saved_path).exists()
    assert await driver.read("reports/sample.bin") == b"quorum-payload"


def test_negative_drivers_init_local_driver_empty_base_path_fails_fast() -> None:
    """Negative test (ISTQB BVA): Empty base_path raises AppException STORAGE_CONFIG_ERROR."""
    with pytest.raises(AppException) as exc_info:
        LocalFileDriver(base_path="")

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.STORAGE_CONFIG_ERROR.value


def test_negative_drivers_init_gcs_driver_empty_bucket_fails_fast() -> None:
    """Negative test (ISTQB BVA): Empty bucket_name raises AppException STORAGE_BUCKET_NOT_FOUND."""
    with pytest.raises(AppException) as exc_info:
        GCSFileDriver(bucket_name="")

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.STORAGE_BUCKET_NOT_FOUND.value


@pytest.mark.asyncio
async def test_negative_drivers_init_local_driver_path_traversal_fails_fast(
    tmp_path: Path,
) -> None:
    """Negative test (ISTQB BVA): Path traversal outside base_path raises FILESYSTEM_VIOLATION."""
    driver = LocalFileDriver(base_path=str(tmp_path))
    with pytest.raises(AppException) as exc_info:
        await driver.read("../../escape.txt")

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.FILESYSTEM_VIOLATION.value

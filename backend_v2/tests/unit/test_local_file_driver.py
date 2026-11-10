"""Unit tests for LocalFileDriver.

Validates asynchronous local filesystem persistence roundtrips, atomic writes,
Windows file-lock retries, bounded Settings-governed timeouts, Fail-Fast RFC 7807
error semantics, and ISTQB negative boundary partitions.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.services.drivers.local_file_driver import (
    MAX_REPLACE_RETRIES,
    LocalFileDriver,
)
from backend_v2.settings import get_settings


@pytest.mark.parametrize("invalid_base_path", ["", "   ", "\t\n"])
def test_init_fails_fast_on_empty_or_whitespace_base_path(invalid_base_path: str) -> None:
    """Negative (ISTQB BVA): Empty or whitespace base_path raises 500 STORAGE_CONFIG_ERROR."""
    with pytest.raises(AppException) as exc_info:
        LocalFileDriver(base_path=invalid_base_path)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.STORAGE_CONFIG_ERROR.value


@pytest.mark.parametrize("invalid_timeout", [0.0, -0.01, -5.0])
def test_init_fails_fast_on_non_positive_timeout(tmp_path: Path, invalid_timeout: float) -> None:
    """Negative (ISTQB BVA): Non-positive timeout_seconds raises 500 STORAGE_CONFIG_ERROR."""
    with pytest.raises(AppException) as exc_info:
        LocalFileDriver(base_path=str(tmp_path), timeout_seconds=invalid_timeout)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.STORAGE_CONFIG_ERROR.value


def test_init_fails_fast_on_missing_directory(tmp_path: Path) -> None:
    """Negative: Non-existent base_path raises 500 STORAGE_ACCESS_FAILED."""
    missing_dir = tmp_path / "non_existent_dir"
    with pytest.raises(AppException) as exc_info:
        LocalFileDriver(base_path=str(missing_dir))

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value
    assert "does not exist or is not a directory" in exc_info.value.message


def test_init_fails_fast_on_not_a_directory(tmp_path: Path) -> None:
    """Negative: File path passed as base_path raises 500 STORAGE_ACCESS_FAILED."""
    regular_file = tmp_path / "regular_file.txt"
    regular_file.write_text("not a dir", encoding="utf-8")

    with pytest.raises(AppException) as exc_info:
        LocalFileDriver(base_path=str(regular_file))

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value
    assert "does not exist or is not a directory" in exc_info.value.message


@pytest.mark.asyncio
async def test_save_read_exists_delete_binary_and_string_roundtrip(tmp_path: Path) -> None:
    """Positive: Stateful roundtrip across binary and UTF-8 string payloads without leftover .tmp files."""
    driver = LocalFileDriver(base_path=str(tmp_path))

    saved_bin = await driver.save("nested/sub/payload.bin", b"\x00\x01quorum")
    assert Path(saved_bin) == (tmp_path / "nested" / "sub" / "payload.bin").resolve()
    assert await driver.exists("nested/sub/payload.bin") is True
    assert await driver.read("nested/sub/payload.bin") == b"\x00\x01quorum"
    assert list((tmp_path / "nested" / "sub").glob("*.tmp")) == []

    saved_txt = await driver.save("docs/note.txt", "Ääkköset UTF-8")
    assert Path(saved_txt).exists()
    assert (await driver.read("docs/note.txt")).decode("utf-8") == "Ääkköset UTF-8"

    assert await driver.delete("docs/note.txt") is True
    assert await driver.exists("docs/note.txt") is False


@pytest.mark.asyncio
async def test_delete_directory_success_and_missing_or_file_failures(tmp_path: Path) -> None:
    """Positive and negative tests for delete_directory."""
    driver = LocalFileDriver(base_path=str(tmp_path))

    with pytest.raises(AppException) as exc_missing:
        await driver.delete_directory("missing_dir")
    assert exc_missing.value.status_code == 404
    assert exc_missing.value.details["error_code"] == ErrorCodes.FILE_NOT_FOUND.value

    await driver.save("plain_file.txt", "content")
    with pytest.raises(AppException) as exc_not_dir:
        await driver.delete_directory("plain_file.txt")
    assert exc_not_dir.value.status_code == 400
    assert exc_not_dir.value.details["error_code"] == ErrorCodes.FILESYSTEM_VIOLATION.value

    await driver.save("executions/exe_01/report.pdf", b"%PDF-1.7")
    assert await driver.delete_directory("executions/exe_01") is True
    assert await driver.exists("executions/exe_01/report.pdf") is False


@pytest.mark.asyncio
async def test_read_and_delete_missing_file_fail_fast_404(tmp_path: Path) -> None:
    """Negative: read and delete on non-existent file raise 404 FILE_NOT_FOUND."""
    driver = LocalFileDriver(base_path=str(tmp_path))

    with pytest.raises(AppException) as exc_read:
        await driver.read("missing/report.pdf")
    assert exc_read.value.status_code == 404
    assert exc_read.value.details["error_code"] == ErrorCodes.FILE_NOT_FOUND.value

    with pytest.raises(AppException) as exc_del:
        await driver.delete("missing/report.pdf")
    assert exc_del.value.status_code == 404
    assert exc_del.value.details["error_code"] == ErrorCodes.FILE_NOT_FOUND.value


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "bad_path",
    ["", "   ", "/", "\\", ".", "./", "nested/..", "../../etc/passwd", "bad\x00name.txt"],
)
async def test_all_operations_reject_invalid_root_or_traversal_paths(
    tmp_path: Path,
    bad_path: str,
) -> None:
    """Negative (ISTQB BVA): Empty, root-self, null-byte, and traversal paths raise 400 FILESYSTEM_VIOLATION."""
    settings = get_settings()
    driver = LocalFileDriver(base_path=str(tmp_path), base_url=f"{settings.api_url}/files")

    for op in (
        lambda: driver.save(bad_path, b"payload"),
        lambda: driver.read(bad_path),
        lambda: driver.delete(bad_path),
        lambda: driver.delete_directory(bad_path),
        lambda: driver.exists(bad_path),
        lambda: driver.get_url(bad_path),
    ):
        with pytest.raises(AppException) as exc_info:
            await op()
        assert exc_info.value.status_code == 400
        assert exc_info.value.details["error_code"] == ErrorCodes.FILESYSTEM_VIOLATION.value


def test_validate_path_unexpected_resolution_error_translates_to_400(tmp_path: Path) -> None:
    """Negative: Unexpected exception during path resolution translates to 400 FILESYSTEM_VIOLATION."""
    driver = LocalFileDriver(base_path=str(tmp_path))
    with patch.object(Path, "is_relative_to", side_effect=ValueError("Unexpected path resolution failure")):
        with pytest.raises(AppException) as exc_generic:
            driver._validate_path("nested/file.txt")
        assert exc_generic.value.status_code == 400
        assert exc_generic.value.details["error_code"] == ErrorCodes.FILESYSTEM_VIOLATION.value


@pytest.mark.asyncio
async def test_get_url_normalization_and_missing_base_url_failure(tmp_path: Path) -> None:
    """Positive and negative tests for get_url using centralized settings base URL."""
    settings = get_settings()
    configured_base_url = f"{settings.api_url}/files/"
    driver = LocalFileDriver(base_path=str(tmp_path), base_url=configured_base_url)

    url = await driver.get_url(r"\reports\sub\file.pdf")
    assert url == f"{configured_base_url.rstrip('/')}/reports/sub/file.pdf"

    for blank_url in (None, "", "   "):
        driver_no_url = LocalFileDriver(base_path=str(tmp_path), base_url=blank_url)
        with pytest.raises(AppException) as exc_url:
            await driver_no_url.get_url("reports/file.pdf")
        assert exc_url.value.status_code == 500
        assert exc_url.value.details["error_code"] == ErrorCodes.STORAGE_CONFIG_ERROR.value


@pytest.mark.asyncio
async def test_save_transient_lock_recovers_and_exhaustion_cleans_tmp(tmp_path: Path) -> None:
    """Error-Path: save recovers from transient PermissionError and cleans up .tmp on exhaustion."""
    driver = LocalFileDriver(base_path=str(tmp_path))
    real_replace = os.replace
    attempts = 0

    def _flaky_replace(src: str | os.PathLike[str], dst: str | os.PathLike[str]) -> None:
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise PermissionError("Transient reader lock")
        real_replace(src, dst)

    with (
        patch("backend_v2.services.drivers.local_file_driver.os.replace", side_effect=_flaky_replace),
        patch("backend_v2.services.drivers.local_file_driver.asyncio.sleep", return_value=None),
    ):
        saved = await driver.save("flaky.bin", b"recovered")

    assert attempts == 3
    assert Path(saved).read_bytes() == b"recovered"

    with (
        patch(
            "backend_v2.services.drivers.local_file_driver.os.replace",
            side_effect=PermissionError("Permanent lock"),
        ) as mock_replace,
        patch("backend_v2.services.drivers.local_file_driver.asyncio.sleep", return_value=None),
    ):
        with pytest.raises(AppException) as exc_locked:
            await driver.save("locked.bin", b"blocked")

    assert mock_replace.call_count == MAX_REPLACE_RETRIES
    assert exc_locked.value.status_code == 409
    assert exc_locked.value.details["error_code"] == ErrorCodes.FILE_LOCKED_ERROR.value
    assert list(tmp_path.glob("*.tmp")) == []


@pytest.mark.asyncio
async def test_read_delete_and_delete_directory_locked_fail_409(tmp_path: Path) -> None:
    """Error-Path: PermissionError on read, delete, and delete_directory raises 409 FILE_LOCKED_ERROR."""
    driver = LocalFileDriver(base_path=str(tmp_path))
    await driver.save("doc.txt", b"content")
    await driver.save("locked_dir/item.txt", b"item")

    with (
        patch(
            "backend_v2.services.drivers.local_file_driver.aiofiles.open",
            side_effect=PermissionError("Locked read"),
        ) as mock_open,
        patch("backend_v2.services.drivers.local_file_driver.asyncio.sleep", return_value=None),
    ):
        with pytest.raises(AppException) as exc_read:
            await driver.read("doc.txt")
    assert mock_open.call_count == MAX_REPLACE_RETRIES
    assert exc_read.value.status_code == 409
    assert exc_read.value.details["error_code"] == ErrorCodes.FILE_LOCKED_ERROR.value

    with patch(
        "backend_v2.services.drivers.local_file_driver.os.remove",
        side_effect=PermissionError("Locked delete"),
    ):
        with pytest.raises(AppException) as exc_del:
            await driver.delete("doc.txt")
    assert exc_del.value.status_code == 409
    assert exc_del.value.details["error_code"] == ErrorCodes.FILE_LOCKED_ERROR.value

    with patch(
        "backend_v2.services.drivers.local_file_driver.shutil.rmtree",
        side_effect=PermissionError("Locked directory"),
    ):
        with pytest.raises(AppException) as exc_dir:
            await driver.delete_directory("locked_dir")
    assert exc_dir.value.status_code == 409
    assert exc_dir.value.details["error_code"] == ErrorCodes.FILE_LOCKED_ERROR.value


@pytest.mark.asyncio
async def test_generic_os_errors_and_timeout_translate_to_500_storage_access_failed(
    tmp_path: Path,
) -> None:
    """Error-Path: Unexpected OSError and asyncio.timeout translate to 500 STORAGE_ACCESS_FAILED."""
    driver = LocalFileDriver(base_path=str(tmp_path), timeout_seconds=0.02)
    await driver.save("existing.txt", b"data")
    await driver.save("existing_dir/child.txt", b"data")

    with patch("backend_v2.services.drivers.local_file_driver.aiofiles.open", side_effect=OSError("Write fault")):
        with pytest.raises(AppException) as exc_save:
            await driver.save("fault.txt", b"data")
        assert exc_save.value.status_code == 500
        assert exc_save.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

    with patch("backend_v2.services.drivers.local_file_driver.aiofiles.open", side_effect=OSError("Read fault")):
        with pytest.raises(AppException) as exc_read:
            await driver.read("existing.txt")
        assert exc_read.value.status_code == 500
        assert exc_read.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

    with patch("backend_v2.services.drivers.local_file_driver.os.remove", side_effect=OSError("Delete fault")):
        with pytest.raises(AppException) as exc_del:
            await driver.delete("existing.txt")
        assert exc_del.value.status_code == 500
        assert exc_del.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

    with patch("backend_v2.services.drivers.local_file_driver.shutil.rmtree", side_effect=OSError("Rmtree fault")):
        with pytest.raises(AppException) as exc_rmtree:
            await driver.delete_directory("existing_dir")
        assert exc_rmtree.value.status_code == 500
        assert exc_rmtree.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

    async def _slow_to_thread(*_args: object, **_kwargs: object) -> bool:
        await asyncio.sleep(0.2)
        return True

    with patch("backend_v2.services.drivers.local_file_driver.asyncio.to_thread", side_effect=_slow_to_thread):
        with pytest.raises(AppException) as exc_timeout:
            await driver.exists("existing.txt")
        assert exc_timeout.value.status_code == 500
        assert exc_timeout.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value

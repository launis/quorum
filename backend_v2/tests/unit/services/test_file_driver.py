"""Unit tests for the FileDriver asynchronous storage protocol."""

from __future__ import annotations

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.services.file_driver import FileDriver


class _InMemoryFileDriver:
    """Hermetic in-memory implementation verifying the FileDriver protocol contract."""

    def __init__(self) -> None:
        """Initializes in-memory blob storage."""
        self._blobs: dict[str, bytes] = {}

    def _validate_path(self, path: str) -> None:
        """Validates that the storage path is non-empty and free of traversal segments."""
        if not path.strip() or ".." in path:
            raise AppException(
                ErrorCodes.STORAGE_ACCESS_FAILED,
                500,
                {"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            )

    async def save(self, path: str, data: bytes | str) -> str:
        """Saves bytes or UTF-8 string content in memory."""
        self._validate_path(path)
        payload = data.encode("utf-8") if isinstance(data, str) else data
        self._blobs[path] = payload
        return f"mem://{path}"

    async def read(self, path: str) -> bytes:
        """Reads bytes from memory or raises FILE_NOT_FOUND."""
        self._validate_path(path)
        if path not in self._blobs:
            raise AppException(
                ErrorCodes.FILE_NOT_FOUND,
                404,
                {"error_code": ErrorCodes.FILE_NOT_FOUND.value},
            )
        return self._blobs[path]

    async def delete(self, path: str) -> bool:
        """Deletes a stored blob if present."""
        self._validate_path(path)
        if path in self._blobs:
            del self._blobs[path]
            return True
        return False

    async def delete_directory(self, prefix: str) -> bool:
        """Deletes all blobs matching the given directory prefix."""
        self._validate_path(prefix)
        matching = [key for key in self._blobs if key.startswith(prefix)]
        for key in matching:
            del self._blobs[key]
        return bool(matching)

    async def exists(self, path: str) -> bool:
        """Checks whether a blob exists at the given path."""
        self._validate_path(path)
        return path in self._blobs

    async def get_url(self, path: str) -> str | None:
        """Returns a synthetic URL if the blob exists."""
        self._validate_path(path)
        return f"https://storage.example/{path}" if path in self._blobs else None


class _IncompleteDriver:
    """Non-conforming class missing required FileDriver methods."""

    async def save(self, path: str, data: bytes | str) -> str:
        """Saves data only."""
        return path


@pytest.mark.asyncio
async def test_file_driver_protocol_roundtrip() -> None:
    """Verifies runtime protocol conformance and positive CRUD operations."""
    driver: FileDriver = _InMemoryFileDriver()
    assert isinstance(driver, FileDriver)

    uri = await driver.save("reports/doc.txt", "hello world")
    assert uri == "mem://reports/doc.txt"
    assert await driver.exists("reports/doc.txt") is True
    assert await driver.read("reports/doc.txt") == b"hello world"
    assert await driver.get_url("reports/doc.txt") == "https://storage.example/reports/doc.txt"
    assert await driver.delete_directory("reports/") is True
    assert await driver.exists("reports/doc.txt") is False
    assert await driver.delete("reports/doc.txt") is False


@pytest.mark.asyncio
async def test_file_driver_negative_missing_file_raises_app_exception() -> None:
    """Verifies reading a non-existent path raises AppException with FILE_NOT_FOUND."""
    driver: FileDriver = _InMemoryFileDriver()
    with pytest.raises(AppException) as exc_info:
        await driver.read("missing/artifact.pdf")
    assert exc_info.value.error_code == ErrorCodes.FILE_NOT_FOUND


@pytest.mark.asyncio
async def test_file_driver_negative_invalid_path_raises_app_exception() -> None:
    """Verifies boundary/invalid paths (empty or path traversal) raise STORAGE_ACCESS_FAILED."""
    driver: FileDriver = _InMemoryFileDriver()
    with pytest.raises(AppException) as exc_info:
        await driver.save("   ", b"data")
    assert exc_info.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED

    with pytest.raises(AppException) as traversal_exc:
        await driver.delete("../secret.txt")
    assert traversal_exc.value.error_code == ErrorCodes.STORAGE_ACCESS_FAILED

    assert not isinstance(_IncompleteDriver(), FileDriver)

"""Local File Driver Implementation."""

import asyncio
import logging
import os
import uuid
from pathlib import Path

import aiofiles

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.services.file_driver import FileDriver

logger = logging.getLogger(__name__)

# Constants for Windows os.replace retry logic
MAX_REPLACE_RETRIES = 5
REPLACE_RETRY_DELAY_SEC = 0.1


class LocalFileDriver(FileDriver):
    """Asynchronous Local File System Driver.

    Implements strict error handling and Fail Fast principles.
    """

    def __init__(self, base_path: str, base_url: str | None = None):
        """Initialize Local Driver.

        Args:
            base_path: Root directory for storage.
            base_url: Optional public base URL (e.g., http://localhost:8000/files).

        Raises:
            AppException: If base_path is empty or inaccessible.
        """
        if not base_path:
            msg = "Local Storage Base Path cannot be empty"
            logger.error("[LocalFileDriver] %s: %s", ErrorCodes.STORAGE_CONFIG_ERROR.name, msg)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_CONFIG_ERROR.value},
            )

        self.base_path = Path(base_path).resolve()
        # Enforce explicit os.path validation: no silent directory creation
        if not self.base_path.exists() or not self.base_path.is_dir():
            msg = f"Local storage directory '{base_path}' does not exist or is not a directory."
            logger.error("[LocalFileDriver] %s: %s", ErrorCodes.STORAGE_ACCESS_FAILED.name, msg)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            )

        self.base_url = base_url

    def _validate_path(self, path: str) -> Path:
        """Enforces strictly that path is within base_path.

        Prevents Path Traversal attacks (../../etc/passwd).

        Returns:
            Path: The resolved absolute path.

        Raises:
            AppException: If path attempts to escape base directory.
        """
        try:
            # clean inputs
            cleaned = path.strip().lstrip("/\\")
            if not cleaned:
                msg = "Empty path"
                logger.error("[LocalFileDriver] %s: %s", ErrorCodes.FILESYSTEM_VIOLATION.name, msg)
                raise AppException(
                    message=msg, status_code=400, details={"error_code": ErrorCodes.FILESYSTEM_VIOLATION.value}
                )

            # Resolve against base
            full_path = (self.base_path / cleaned).resolve()

            # Strict lineage check
            if not full_path.is_relative_to(self.base_path):
                msg = f"Path traversal attempt detected: {path}"
                logger.error("[LocalFileDriver] %s: %s", ErrorCodes.FILESYSTEM_VIOLATION.name, msg)
                raise AppException(
                    message=msg,
                    status_code=400,
                    details={"error_code": ErrorCodes.FILESYSTEM_VIOLATION.value},
                )
            return full_path
        except AppException:
            raise
        except Exception as e:
            msg = f"Invalid file path: {path}"
            logger.error("[LocalFileDriver] %s: %s", ErrorCodes.FILESYSTEM_VIOLATION.name, msg, exc_info=True)
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.FILESYSTEM_VIOLATION.value, "info": str(e)},
            ) from e

    async def save(self, path: str, data: bytes | str) -> str:
        """Saves data to local file system."""
        full_path = self._validate_path(path)

        try:
            # Explicitly create parent directories to maintain parity with cloud storage drivers
            # where paths are virtual keys and directory creation is implicit.
            full_path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = full_path.with_name(f"{full_path.name}.{uuid.uuid4().hex}.tmp")

            if isinstance(data, bytes):
                async with aiofiles.open(tmp_path, "wb") as f:
                    await f.write(data)
            else:
                async with aiofiles.open(tmp_path, "w", encoding="utf-8") as f:
                    await f.write(data)

            # Atomic replace prevents race conditions where another thread/process
            # might read a 0-byte truncated file during concurrent writes.
            # On Windows, os.replace throws PermissionError if the file is open by a reader (e.g. UI polling).
            for attempt in range(MAX_REPLACE_RETRIES):
                try:
                    os.replace(tmp_path, full_path)
                    break
                except PermissionError as e:
                    if attempt == MAX_REPLACE_RETRIES - 1:
                        raise e
                    logger.warning(
                        "[LocalFileDriver] WinError 5 on os.replace, retrying %d/%d for %s",
                        attempt + 1,
                        MAX_REPLACE_RETRIES,
                        full_path.name,
                    )
                    await asyncio.sleep(REPLACE_RETRY_DELAY_SEC)

            return str(full_path)
        except Exception as e:
            logger.error(
                f"[LocalFileDriver] {ErrorCodes.STORAGE_ACCESS_FAILED.name}: Failed to save file to {path}: {e}",
                exc_info=True,
            )
            raise AppException(
                message=f"Local Save Failed: {str(e)}",
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from e

    async def read(self, path: str) -> bytes:
        """Reads data from local file system."""
        full_path = self._validate_path(path)

        # FAIL FAST: Check existence before opening
        if not full_path.exists():
            msg = f"File not found: {path}"
            logger.error("[LocalFileDriver] %s: %s", ErrorCodes.FILE_NOT_FOUND.name, msg)
            raise AppException(message=msg, status_code=404, details={"error_code": ErrorCodes.FILE_NOT_FOUND.value})

        try:
            async with aiofiles.open(full_path, "rb") as f:
                data = await f.read()
                return data if isinstance(data, bytes) else bytes(data, "utf-8")
        except Exception as e:
            logger.error(
                f"[LocalFileDriver] {ErrorCodes.STORAGE_ACCESS_FAILED.name}: Failed to read file from {path}: {e}",
                exc_info=True,
            )
            raise AppException(
                message=f"Local Read Failed: {str(e)}",
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from e

    async def delete(self, path: str) -> bool:
        """Deletes file from local file system."""
        full_path = self._validate_path(path)
        if not full_path.exists():
            msg = f"Cannot delete non-existent local file: {path}"
            logger.error("[LocalFileDriver] %s: %s", ErrorCodes.FILE_NOT_FOUND.name, msg)
            raise AppException(message=msg, status_code=404, details={"error_code": ErrorCodes.FILE_NOT_FOUND.value})

        try:
            # Standard os.remove is sync but fast for local FS.
            os.remove(full_path)
            return True
        except Exception as e:
            logger.error(
                f"[LocalFileDriver] {ErrorCodes.STORAGE_ACCESS_FAILED.name}: Failed to delete file {path}: {e}",
                exc_info=True,
            )
            raise AppException(
                message=f"Local Delete Failed: {str(e)}",
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from e

    async def exists(self, path: str) -> bool:
        """Checks if file exists."""
        full_path = self._validate_path(path)
        return full_path.exists()

    async def get_url(self, path: str) -> str | None:
        """Returns public URL if configured."""
        if not self.base_url:
            msg = "Local base_url is missing. Zero-Compromise Fail-Fast enforced."
            logger.error("[LocalFileDriver] %s: %s", ErrorCodes.STORAGE_CONFIG_ERROR.name, msg)
            raise AppException(
                message=msg, status_code=500, details={"error_code": ErrorCodes.STORAGE_CONFIG_ERROR.value}
            )
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

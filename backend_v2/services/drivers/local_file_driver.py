"""Local File Driver Implementation."""

import asyncio
import logging
import os
import shutil
from pathlib import Path
from typing import override

import aiofiles

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import generate_uuid7
from backend_v2.services.file_driver import FileDriver

logger = logging.getLogger(__name__)
__all__ = ["LocalFileDriver", "MAX_REPLACE_RETRIES", "REPLACE_RETRY_DELAY_SEC"]

# Constants for Windows os.replace retry logic
MAX_REPLACE_RETRIES = 15
REPLACE_RETRY_DELAY_SEC = 0.5


class LocalFileDriver(FileDriver):
    """Asynchronous Local File System Driver.

    Implements strict error handling and Fail-Fast principles.

    Attributes:
        base_path: Resolved root directory path for local file storage.
        base_url: Optional public base URL prefix for serving stored files.
    """

    def __init__(self, base_path: str, base_url: str | None = None) -> None:
        """Initialize Local Driver.

        Args:
            base_path: Root directory for storage.
            base_url: Optional public base URL resolved from settings.

        Raises:
            AppException: With STORAGE_CONFIG_ERROR if base_path is empty, or
                STORAGE_ACCESS_FAILED if base_path does not exist or is not a directory.
        """
        if not base_path:
            msg = "Local Storage Base Path cannot be empty"
            logger.error(
                "[LocalFileDriver] %s: %s",
                ErrorCodes.STORAGE_CONFIG_ERROR.name,
                msg,
                extra={"error_code": ErrorCodes.STORAGE_CONFIG_ERROR.value},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_CONFIG_ERROR.value},
            )

        self.base_path = Path(base_path).resolve()
        # Enforce explicit pathlib validation: no silent directory creation
        if not self.base_path.exists() or not self.base_path.is_dir():
            msg = f"Local storage directory '{base_path}' does not exist or is not a directory."
            logger.error(
                "[LocalFileDriver] %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            )

        self.base_url = base_url

    def _validate_path(self, path: str) -> Path:
        """Enforce strictly that the target path resolves within base_path.

        Prevents Path Traversal attacks (../../etc/passwd).

        Args:
            path: Relative target file or directory path.

        Returns:
            The resolved absolute path inside base_path.

        Raises:
            AppException: With FILESYSTEM_VIOLATION if path is empty, malformed,
                or attempts to escape the base directory.
        """
        try:
            cleaned = path.strip().lstrip("/\\")
            if not cleaned:
                msg = "Empty path"
                logger.error(
                    "[LocalFileDriver] %s: %s",
                    ErrorCodes.FILESYSTEM_VIOLATION.name,
                    msg,
                    extra={"error_code": ErrorCodes.FILESYSTEM_VIOLATION.value},
                    exc_info=True,
                )
                raise AppException(
                    message=msg,
                    status_code=400,
                    details={"error_code": ErrorCodes.FILESYSTEM_VIOLATION.value},
                )

            full_path = (self.base_path / cleaned).resolve()

            if not full_path.is_relative_to(self.base_path):
                msg = f"Path traversal attempt detected: {path}"
                logger.error(
                    "[LocalFileDriver] %s: %s",
                    ErrorCodes.FILESYSTEM_VIOLATION.name,
                    msg,
                    extra={"error_code": ErrorCodes.FILESYSTEM_VIOLATION.value},
                    exc_info=True,
                )
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
            logger.error(
                "[LocalFileDriver] %s: %s",
                ErrorCodes.FILESYSTEM_VIOLATION.name,
                msg,
                extra={"error_code": ErrorCodes.FILESYSTEM_VIOLATION.value},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.FILESYSTEM_VIOLATION.value, "info": str(e)},
            ) from e

    @override
    async def save(self, path: str, data: bytes | str) -> str:
        """Save data to the local file system atomically.

        Args:
            path: Target relative file path.
            data: File content as bytes or UTF-8 string.

        Returns:
            The full resolved path of the saved file as a string.

        Raises:
            AppException: With FILESYSTEM_VIOLATION if path is invalid,
                FILE_LOCKED_ERROR if the target file remains locked across retries,
                or STORAGE_ACCESS_FAILED if writing fails.
        """
        full_path = self._validate_path(path)

        try:
            # Explicitly create parent directories to maintain parity with cloud storage drivers
            # where paths are virtual keys and directory creation is implicit.
            full_path.parent.mkdir(parents=True, exist_ok=True)
            tmp_path = full_path.with_name(f"{full_path.name}.{generate_uuid7().hex}.tmp")

            if isinstance(data, bytes):
                async with aiofiles.open(tmp_path, "wb") as f:
                    await f.write(data)
            else:
                async with aiofiles.open(tmp_path, "w", encoding="utf-8") as f:
                    await f.write(data)

            # Atomic replace prevents race conditions where another thread/process
            # might read a 0-byte truncated file during concurrent writes.
            # On Windows, os.replace throws PermissionError if the file is open by a reader.
            for attempt in range(MAX_REPLACE_RETRIES):
                try:
                    await asyncio.to_thread(os.replace, tmp_path, full_path)
                    break
                except PermissionError as e:
                    if attempt == MAX_REPLACE_RETRIES - 1:
                        logger.error(
                            "[LocalFileDriver] %s: File is locked: %s",
                            ErrorCodes.FILE_LOCKED_ERROR.name,
                            e,
                            extra={"error_code": ErrorCodes.FILE_LOCKED_ERROR.value},
                            exc_info=True,
                        )
                        raise AppException(
                            message=f"File is locked by another process: {e!s}",
                            status_code=409,
                            details={"error_code": ErrorCodes.FILE_LOCKED_ERROR.value},
                        ) from e
                    logger.warning(
                        "[LocalFileDriver] WinError 5 on os.replace, retrying %d/%d for %s",
                        attempt + 1,
                        MAX_REPLACE_RETRIES,
                        full_path.name,
                    )
                    await asyncio.sleep(REPLACE_RETRY_DELAY_SEC)

            return str(full_path)
        except AppException:
            raise
        except Exception as e:
            logger.error(
                "[LocalFileDriver] %s: Failed to save file to %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                path,
                e,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message=f"Local Save Failed: {e}",
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from e

    @override
    async def read(self, path: str) -> bytes:
        """Read raw bytes from the local file system.

        Args:
            path: Target relative file path.

        Returns:
            The raw binary file content.

        Raises:
            AppException: With FILESYSTEM_VIOLATION if path is invalid,
                FILE_NOT_FOUND if the file does not exist,
                FILE_LOCKED_ERROR if the file remains locked across retries,
                or STORAGE_ACCESS_FAILED if reading fails.
        """
        full_path = self._validate_path(path)

        if not full_path.exists():
            msg = f"File not found: {path}"
            logger.error(
                "[LocalFileDriver] %s: %s",
                ErrorCodes.FILE_NOT_FOUND.name,
                msg,
                extra={"error_code": ErrorCodes.FILE_NOT_FOUND.value},
                exc_info=True,
            )
            raise AppException(message=msg, status_code=404, details={"error_code": ErrorCodes.FILE_NOT_FOUND.value})

        attempt = 0
        while True:
            try:
                async with aiofiles.open(full_path, "rb") as f:
                    data = await f.read()
                    return data if isinstance(data, bytes) else bytes(data, "utf-8")
            except PermissionError as e:
                attempt += 1
                if attempt >= MAX_REPLACE_RETRIES:
                    logger.error(
                        "[LocalFileDriver] %s: File is locked after %d attempts: %s",
                        ErrorCodes.FILE_LOCKED_ERROR.name,
                        MAX_REPLACE_RETRIES,
                        e,
                        extra={"error_code": ErrorCodes.FILE_LOCKED_ERROR.value},
                        exc_info=True,
                    )
                    raise AppException(
                        message=f"Local Read Failed, file is locked: {e!s}",
                        status_code=409,
                        details={"error_code": ErrorCodes.FILE_LOCKED_ERROR.value},
                    ) from e
                logger.warning(
                    "[LocalFileDriver] WinError on aiofiles.open (read), retrying %d/%d for %s",
                    attempt,
                    MAX_REPLACE_RETRIES,
                    full_path.name,
                )
                await asyncio.sleep(REPLACE_RETRY_DELAY_SEC)
            except Exception as e:
                logger.error(
                    "[LocalFileDriver] %s: Failed to read file from %s: %s",
                    ErrorCodes.STORAGE_ACCESS_FAILED.name,
                    path,
                    e,
                    extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
                    exc_info=True,
                )
                raise AppException(
                    message=f"Local Read Failed: {e!s}",
                    status_code=500,
                    details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
                ) from e

    @override
    async def delete(self, path: str) -> bool:
        """Delete a file from the local file system.

        Args:
            path: Target relative file path.

        Returns:
            True if the file was deleted successfully.

        Raises:
            AppException: With FILESYSTEM_VIOLATION if path is invalid,
                FILE_NOT_FOUND if the file does not exist,
                FILE_LOCKED_ERROR if the file is locked by another process,
                or STORAGE_ACCESS_FAILED if deletion fails.
        """
        full_path = self._validate_path(path)
        if not full_path.exists():
            msg = f"Cannot delete non-existent local file: {path}"
            logger.error(
                "[LocalFileDriver] %s: %s",
                ErrorCodes.FILE_NOT_FOUND.name,
                msg,
                extra={"error_code": ErrorCodes.FILE_NOT_FOUND.value},
                exc_info=True,
            )
            raise AppException(message=msg, status_code=404, details={"error_code": ErrorCodes.FILE_NOT_FOUND.value})

        try:
            await asyncio.to_thread(os.remove, full_path)
            return True
        except PermissionError as e:
            logger.error(
                "[LocalFileDriver] %s: File is locked: %s",
                ErrorCodes.FILE_LOCKED_ERROR.name,
                e,
                extra={"error_code": ErrorCodes.FILE_LOCKED_ERROR.value},
                exc_info=True,
            )
            raise AppException(
                message=f"File is locked by another process: {e!s}",
                status_code=409,
                details={"error_code": ErrorCodes.FILE_LOCKED_ERROR.value},
            ) from e
        except Exception as e:
            logger.error(
                "[LocalFileDriver] %s: Failed to delete file %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                path,
                e,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message=f"Local Delete Failed: {e!s}",
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from e

    @override
    async def delete_directory(self, prefix: str) -> bool:
        """Delete a directory and all its contents locally.

        Args:
            prefix: Target relative directory path.

        Returns:
            True if the directory was deleted successfully.

        Raises:
            AppException: With FILESYSTEM_VIOLATION if path is invalid or not a directory,
                FILE_NOT_FOUND if the directory does not exist,
                FILE_LOCKED_ERROR if the directory is locked by another process,
                or STORAGE_ACCESS_FAILED if deletion fails.
        """
        full_path = self._validate_path(prefix)
        if not full_path.exists():
            msg = f"Cannot delete non-existent local directory: {prefix}"
            logger.error(
                "[LocalFileDriver] %s: %s",
                ErrorCodes.FILE_NOT_FOUND.name,
                msg,
                extra={"error_code": ErrorCodes.FILE_NOT_FOUND.value},
                exc_info=True,
            )
            raise AppException(message=msg, status_code=404, details={"error_code": ErrorCodes.FILE_NOT_FOUND.value})

        if not full_path.is_dir():
            msg = f"Path is not a directory: {prefix}"
            logger.error(
                "[LocalFileDriver] %s: %s",
                ErrorCodes.FILESYSTEM_VIOLATION.name,
                msg,
                extra={"error_code": ErrorCodes.FILESYSTEM_VIOLATION.value},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.FILESYSTEM_VIOLATION.value},
            )

        try:
            await asyncio.to_thread(shutil.rmtree, full_path)
            return True
        except PermissionError as e:
            logger.error(
                "[LocalFileDriver] %s: Directory is locked: %s",
                ErrorCodes.FILE_LOCKED_ERROR.name,
                e,
                extra={"error_code": ErrorCodes.FILE_LOCKED_ERROR.value},
                exc_info=True,
            )
            raise AppException(
                message=f"Directory is locked by another process: {e!s}",
                status_code=409,
                details={"error_code": ErrorCodes.FILE_LOCKED_ERROR.value},
            ) from e
        except Exception as e:
            logger.error(
                "[LocalFileDriver] %s: Failed to delete directory %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                prefix,
                e,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message=f"Local Directory Delete Failed: {e!s}",
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from e

    @override
    async def exists(self, path: str) -> bool:
        """Check whether a file exists in local storage.

        Args:
            path: Target relative file path.

        Returns:
            True if the file exists, False otherwise.

        Raises:
            AppException: With FILESYSTEM_VIOLATION if path is invalid or attempts path traversal.
        """
        full_path = self._validate_path(path)
        return full_path.exists()

    @override
    async def get_url(self, path: str) -> str | None:
        """Return the public URL for the target file path.

        Args:
            path: Target relative file path.

        Returns:
            The resolved public URL string.

        Raises:
            AppException: With STORAGE_CONFIG_ERROR if base_url is not configured.
        """
        if not self.base_url:
            msg = "Local base_url is missing. Zero-Compromise Fail-Fast enforced."
            logger.error(
                "[LocalFileDriver] %s: %s",
                ErrorCodes.STORAGE_CONFIG_ERROR.name,
                msg,
                extra={"error_code": ErrorCodes.STORAGE_CONFIG_ERROR.value},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_CONFIG_ERROR.value},
            )
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

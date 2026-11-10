"""Asynchronous Local Filesystem Storage Driver."""

from __future__ import annotations

import asyncio
import contextlib
import logging
import os
import shutil
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import override

import aiofiles

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import generate_uuid7
from backend_v2.services.file_driver import FileDriver
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)
__all__ = ["LocalFileDriver", "MAX_REPLACE_RETRIES", "REPLACE_RETRY_DELAY_SEC"]

MAX_REPLACE_RETRIES = 15
REPLACE_RETRY_DELAY_SEC = 0.5


class LocalFileDriver(FileDriver):
    """Asynchronous local filesystem driver implementing the FileDriver protocol.

    Enforces strict path-traversal containment, atomic temporary-file replacement,
    Windows file-lock retry resilience, Settings-governed execution timeouts, and
    RFC 7807 Fail-Fast error semantics.

    Attributes:
        base_path: Resolved absolute root directory path for local file storage.
        base_url: Optional normalized public base URL prefix for serving stored files.
        timeout_seconds: Bounded execution timeout in seconds for filesystem operations.
    """

    def __init__(
        self,
        base_path: str,
        base_url: str | None = None,
        *,
        timeout_seconds: float | None = None,
    ) -> None:
        """Initialize the local filesystem storage driver.

        Args:
            base_path: Root directory path for local file storage.
            base_url: Optional public base URL resolved from application settings.
            timeout_seconds: Optional explicit timeout override in seconds; resolves
                from settings.db_lock_timeout_seconds when omitted.

        Raises:
            AppException: With STORAGE_CONFIG_ERROR if base_path is blank or
                timeout_seconds is non-positive, or STORAGE_ACCESS_FAILED if
                base_path does not exist or is not a directory.
        """
        cleaned_base = base_path.strip()
        if not cleaned_base:
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

        resolved_timeout = get_settings().db_lock_timeout_seconds
        if timeout_seconds is not None:
            resolved_timeout = timeout_seconds

        if resolved_timeout <= 0:
            msg = f"Local storage operation timeout must be positive, got {resolved_timeout}"
            logger.error(
                "[LocalFileDriver] %s: %s",
                ErrorCodes.STORAGE_CONFIG_ERROR.name,
                msg,
                extra={"error_code": ErrorCodes.STORAGE_CONFIG_ERROR.value, "timeout_seconds": resolved_timeout},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_CONFIG_ERROR.value},
            )

        resolved_base = Path(cleaned_base).resolve()
        if not resolved_base.exists() or not resolved_base.is_dir():
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

        normalized_url: str | None = None
        if base_url is not None:
            stripped_url = base_url.strip()
            if stripped_url:
                normalized_url = stripped_url.rstrip("/")

        self.base_path = resolved_base
        self.base_url = normalized_url
        self.timeout_seconds = resolved_timeout

    def _validate_path(self, path: str) -> Path:
        """Enforce that the target relative path resolves strictly beneath base_path.

        Rejects empty keys, null bytes, root-self references, and path traversal escapes.

        Args:
            path: Relative target file or directory path.

        Returns:
            Resolved absolute descendant Path within base_path.

        Raises:
            AppException: With FILESYSTEM_VIOLATION if path is empty, malformed,
                targets base_path itself, or attempts to escape base_path.
        """
        try:
            cleaned = path.strip().lstrip("/\\")
            if not cleaned or "\x00" in cleaned:
                msg = "Invalid empty or null-byte file path"
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
            if full_path == self.base_path or not full_path.is_relative_to(self.base_path):
                msg = f"Path traversal or root target violation detected: {path}"
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

    def _ensure_target_exists(self, full_path: Path, *, missing_message: str) -> None:
        """Verify that a resolved target path exists before read or delete operations.

        Args:
            full_path: Resolved filesystem target path inside base_path.
            missing_message: Contextual error message to report when absent.

        Raises:
            AppException: With FILE_NOT_FOUND (404) if full_path does not exist.
        """
        if not full_path.exists():
            logger.error(
                "[LocalFileDriver] %s: %s",
                ErrorCodes.FILE_NOT_FOUND.name,
                missing_message,
                extra={"error_code": ErrorCodes.FILE_NOT_FOUND.value},
                exc_info=True,
            )
            raise AppException(
                message=missing_message,
                status_code=404,
                details={"error_code": ErrorCodes.FILE_NOT_FOUND.value},
            )

    async def _execute_io[T](
        self,
        operation: Callable[[], Awaitable[T]],
        *,
        operation_label: str,
        target_label: str,
        lock_message_prefix: str,
        max_attempts: int,
    ) -> T:
        """Execute a local filesystem coroutine with timeout and Windows lock handling.

        Consolidates Python 3.14 asyncio.timeout enforcement, transient PermissionError
        retries, and RFC 7807 Dual-Reporting exception translation across all operations.

        Args:
            operation: Zero-argument async callable performing filesystem I/O.
            operation_label: Human-readable label describing the operation for logs.
            target_label: Relative path or prefix string for structured diagnostics.
            lock_message_prefix: Error message prefix used when raising FILE_LOCKED_ERROR.
            max_attempts: Maximum execution attempts on transient PermissionError faults.

        Returns:
            Typed result produced by operation.

        Raises:
            AppException: With FILE_LOCKED_ERROR (409) when PermissionError persists,
                or STORAGE_ACCESS_FAILED (500) on timeout or unexpected OS failure.
        """
        attempt = 0
        try:
            async with asyncio.timeout(self.timeout_seconds):
                while True:
                    try:
                        return await operation()
                    except PermissionError as e:
                        attempt += 1
                        if attempt >= max_attempts:
                            logger.error(
                                "[LocalFileDriver] %s: %s for %s: %s",
                                ErrorCodes.FILE_LOCKED_ERROR.name,
                                lock_message_prefix,
                                target_label,
                                e,
                                extra={"error_code": ErrorCodes.FILE_LOCKED_ERROR.value, "target": target_label},
                                exc_info=True,
                            )
                            raise AppException(
                                message=f"{lock_message_prefix}: {e!s}",
                                status_code=409,
                                details={"error_code": ErrorCodes.FILE_LOCKED_ERROR.value},
                            ) from e
                        logger.warning(
                            "[LocalFileDriver] PermissionError during %s, retrying %d/%d for %s",
                            operation_label,
                            attempt,
                            max_attempts,
                            target_label,
                        )
                        await asyncio.sleep(REPLACE_RETRY_DELAY_SEC)
        except AppException:
            raise
        except Exception as e:
            logger.error(
                "[LocalFileDriver] %s: %s Failed for %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                operation_label,
                target_label,
                e,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value, "target": target_label},
                exc_info=True,
            )
            raise AppException(
                message=f"{operation_label} Failed: {e!s}",
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from e

    @override
    async def save(self, path: str, data: bytes | str) -> str:
        """Save binary or UTF-8 string content atomically via a temporary sibling file.

        Args:
            path: Target relative file path.
            data: File content as raw bytes or UTF-8 string.

        Returns:
            Full resolved filesystem path of the saved file as a string.

        Raises:
            AppException: With FILESYSTEM_VIOLATION if path is invalid,
                FILE_LOCKED_ERROR if the target file remains locked across retries,
                or STORAGE_ACCESS_FAILED if writing or replacement fails.
        """
        full_path = self._validate_path(path)
        tmp_path = full_path.with_name(f"{full_path.name}.{generate_uuid7().hex}.tmp")

        async def _stage_temp_file() -> None:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(data, bytes):
                async with aiofiles.open(tmp_path, "wb") as f:
                    await f.write(data)
            else:
                async with aiofiles.open(tmp_path, "w", encoding="utf-8") as f:
                    await f.write(data)

        try:
            await self._execute_io(
                _stage_temp_file,
                operation_label="Local Save",
                target_label=path,
                lock_message_prefix="File is locked by another process",
                max_attempts=1,
            )
            await self._execute_io(
                lambda: asyncio.to_thread(os.replace, tmp_path, full_path),
                operation_label="Local Save",
                target_label=path,
                lock_message_prefix="File is locked by another process",
                max_attempts=MAX_REPLACE_RETRIES,
            )
            return str(full_path)
        except Exception:
            with contextlib.suppress(OSError):
                tmp_path.unlink(missing_ok=True)
            raise

    @override
    async def read(self, path: str) -> bytes:
        """Read raw bytes from the local filesystem with transient lock retry support.

        Args:
            path: Target relative file path.

        Returns:
            Raw binary file content.

        Raises:
            AppException: With FILESYSTEM_VIOLATION if path is invalid,
                FILE_NOT_FOUND if the file does not exist,
                FILE_LOCKED_ERROR if the file remains locked across retries,
                or STORAGE_ACCESS_FAILED if reading fails.
        """
        full_path = self._validate_path(path)
        self._ensure_target_exists(full_path, missing_message=f"File not found: {path}")

        async def _read_bytes() -> bytes:
            async with aiofiles.open(full_path, "rb") as f:
                content: bytes = await f.read()
                return content

        return await self._execute_io(
            _read_bytes,
            operation_label="Local Read",
            target_label=path,
            lock_message_prefix="Local Read Failed, file is locked",
            max_attempts=MAX_REPLACE_RETRIES,
        )

    @override
    async def delete(self, path: str) -> bool:
        """Delete a file from the local filesystem on a worker thread.

        Args:
            path: Target relative file path.

        Returns:
            True when the file is deleted.

        Raises:
            AppException: With FILESYSTEM_VIOLATION if path is invalid,
                FILE_NOT_FOUND if the file does not exist,
                FILE_LOCKED_ERROR if the file is locked by another process,
                or STORAGE_ACCESS_FAILED if deletion fails.
        """
        full_path = self._validate_path(path)
        self._ensure_target_exists(
            full_path,
            missing_message=f"Cannot delete non-existent local file: {path}",
        )
        await self._execute_io(
            lambda: asyncio.to_thread(os.remove, full_path),
            operation_label="Local Delete",
            target_label=path,
            lock_message_prefix="File is locked by another process",
            max_attempts=1,
        )
        return True

    @override
    async def delete_directory(self, prefix: str) -> bool:
        """Delete a directory tree and all its contents locally on a worker thread.

        Args:
            prefix: Target relative directory path.

        Returns:
            True when the directory tree is deleted.

        Raises:
            AppException: With FILESYSTEM_VIOLATION if prefix is invalid or not a directory,
                FILE_NOT_FOUND if the directory does not exist,
                FILE_LOCKED_ERROR if the directory is locked by another process,
                or STORAGE_ACCESS_FAILED if deletion fails.
        """
        full_path = self._validate_path(prefix)
        self._ensure_target_exists(
            full_path,
            missing_message=f"Cannot delete non-existent local directory: {prefix}",
        )
        if not full_path.is_dir():
            msg = f"Path is not a directory: {prefix}"
            logger.error(
                "[LocalFileDriver] %s: %s",
                ErrorCodes.FILESYSTEM_VIOLATION.name,
                msg,
                extra={"error_code": ErrorCodes.FILESYSTEM_VIOLATION.value, "prefix": prefix},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.FILESYSTEM_VIOLATION.value},
            )

        await self._execute_io(
            lambda: asyncio.to_thread(shutil.rmtree, full_path),
            operation_label="Local Directory Delete",
            target_label=prefix,
            lock_message_prefix="Directory is locked by another process",
            max_attempts=1,
        )
        return True

    @override
    async def exists(self, path: str) -> bool:
        """Check whether a file or directory exists inside local storage.

        Args:
            path: Target relative file path.

        Returns:
            True if the path exists, False otherwise.

        Raises:
            AppException: With FILESYSTEM_VIOLATION if path is invalid or escapes base_path,
                or STORAGE_ACCESS_FAILED if filesystem stat times out or fails.
        """
        full_path = self._validate_path(path)
        return await self._execute_io(
            lambda: asyncio.to_thread(full_path.exists),
            operation_label="Local Exists Check",
            target_label=path,
            lock_message_prefix="File is locked by another process",
            max_attempts=1,
        )

    @override
    async def get_url(self, path: str) -> str | None:
        """Return the normalized public URL for a validated relative file path.

        Args:
            path: Target relative file path.

        Returns:
            Resolved public URL string with POSIX path separators.

        Raises:
            AppException: With STORAGE_CONFIG_ERROR if base_url is unconfigured,
                or FILESYSTEM_VIOLATION if path is invalid or attempts path traversal.
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
        full_path = self._validate_path(path)
        rel_posix = full_path.relative_to(self.base_path).as_posix()
        return f"{self.base_url}/{rel_posix}"

"""Local File Driver Implementation."""

import logging
import os
from pathlib import Path

import aiofiles  # type: ignore

from backend.exceptions import AppException, ErrorCodes
from backend.services.file_driver import FileDriver

logger = logging.getLogger(__name__)


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
            raise AppException(
                message="Local Storage Base Path cannot be empty",
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_CONFIG_ERROR},
            )

        self.base_path = Path(base_path).resolve()
        try:
            self.base_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise AppException(
                message=f"Failed to create/access local storage directory '{base_path}': {e}",
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED},
            ) from e

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
                raise ValueError("Empty path")

            # Resolve against base
            full_path = (self.base_path / cleaned).resolve()

            # Strict lineage check
            if not full_path.is_relative_to(self.base_path):
                raise AppException(
                    message=f"Path traversal attempt detected: {path}",
                    status_code=400,
                    details={"error_code": ErrorCodes.FILESYSTEM_VIOLATION},
                )
            return full_path
        except AppException:
            raise
        except Exception as e:
            raise AppException(
                message=f"Invalid file path: {path}",
                status_code=400,
                details={"error_code": ErrorCodes.FILESYSTEM_VIOLATION, "info": str(e)},
            ) from e

    async def save(self, path: str, data: bytes | str) -> str:
        """Saves data to local file system."""
        full_path = self._validate_path(path)

        try:
            # Ensure parent dir exists (Sync operation, but fast on local FS)
            full_path.parent.mkdir(parents=True, exist_ok=True)

            mode = "wb" if isinstance(data, bytes) else "w"
            encoding = None if isinstance(data, bytes) else "utf-8"

            async with aiofiles.open(full_path, mode, encoding=encoding) as f:
                await f.write(data)

            return str(full_path)
        except Exception as e:
            logger.error(f"Failed to save file to {path}: {e}")
            raise AppException(
                message=f"Local Save Failed: {str(e)}",
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED},
            ) from e

    async def read(self, path: str) -> bytes:
        """Reads data from local file system."""
        full_path = self._validate_path(path)

        # FAIL FAST: Check existence before opening
        if not full_path.exists():
            raise AppException(
                message=f"File not found: {path}", status_code=404, details={"error_code": ErrorCodes.FILE_NOT_FOUND}
            )

        try:
            async with aiofiles.open(full_path, "rb") as f:
                return await f.read()
        except Exception as e:
            logger.error(f"Failed to read file from {path}: {e}")
            raise AppException(
                message=f"Local Read Failed: {str(e)}",
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED},
            ) from e

    async def delete(self, path: str) -> bool:
        """Deletes file from local file system."""
        full_path = self._validate_path(path)
        if full_path.exists():
            try:
                # Standard os.remove is sync but fast for local FS.
                os.remove(full_path)
                return True
            except Exception as e:
                logger.error(f"Failed to delete file {path}: {e}")
                raise AppException(
                    message=f"Local Delete Failed: {str(e)}",
                    status_code=500,
                    details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED},
                ) from e
        return False

    async def exists(self, path: str) -> bool:
        """Checks if file exists."""
        full_path = self._validate_path(path)
        return full_path.exists()

    async def get_url(self, path: str) -> str | None:
        """Returns public URL if configured."""
        if self.base_url:
            return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        return None

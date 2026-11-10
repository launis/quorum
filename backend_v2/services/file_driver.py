"""Asynchronous file storage driver protocol.

Defines the abstract interface for asynchronous file storage operations,
maintaining parity between local and cloud storage environments.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

__all__ = ["FileDriver"]


@runtime_checkable
class FileDriver(Protocol):
    """Abstract interface for asynchronous file storage drivers.

    Adheres to the Quorum RFC 7807 error handling contract.
    Implementations raise `AppException` for predictable storage failures.
    """

    async def save(self, path: str, data: bytes | str) -> str:
        """Saves binary or text data to the specified relative path.

        Args:
            path: Relative storage path or object key.
            data: Binary or text content to persist.

        Returns:
            Resolved storage path or URI.

        Raises:
            AppException: If storage is inaccessible or write fails (STORAGE_ACCESS_FAILED).
        """
        ...

    async def read(self, path: str) -> bytes:
        """Reads raw bytes from the specified relative path.

        Args:
            path: Relative storage path or object key.

        Returns:
            Raw binary file content.

        Raises:
            AppException: If file is not found (FILE_NOT_FOUND) or read fails (STORAGE_ACCESS_FAILED).
        """
        ...

    async def delete(self, path: str) -> bool:
        """Deletes the file at the specified relative path.

        Args:
            path: Relative storage path or object key.

        Returns:
            True if the file was deleted, False if it was not found.

        Raises:
            AppException: If storage is inaccessible (STORAGE_ACCESS_FAILED).
        """
        ...

    async def delete_directory(self, prefix: str) -> bool:
        """Deletes a directory or all files matching a path prefix.

        Args:
            prefix: Relative directory path prefix.

        Returns:
            True if matching entries were deleted, False otherwise.

        Raises:
            AppException: If storage is inaccessible (STORAGE_ACCESS_FAILED).
        """
        ...

    async def exists(self, path: str) -> bool:
        """Checks whether a file exists at the specified relative path.

        Args:
            path: Relative storage path or object key.

        Returns:
            True if the file exists, False otherwise.

        Raises:
            AppException: If storage connectivity fails (STORAGE_ACCESS_FAILED).
        """
        ...

    async def get_url(self, path: str) -> str | None:
        """Returns a public or pre-signed URL for the file when supported.

        Args:
            path: Relative storage path or object key.

        Returns:
            Public or pre-signed URL if supported by the backend, or None.

        Raises:
            AppException: If URL generation fails (STORAGE_ACCESS_FAILED).
        """
        ...

"""File Driver Protocol (V2.9/V2026).

This module defines the abstract interface for asynchronous file storage,
maintaining parity between Local and Cloud environments.
"""
from typing import Protocol, runtime_checkable


@runtime_checkable
class FileDriver(Protocol):
    """Abstract interface for File Storage (Local/GCS/S3).
    
    Adheres to the Cognitive Quorum Error Handling Contract (RFC 7807).
    Implementations MUST raise `AppException` for predictable failures.
    """

    async def save(self, path: str, data: bytes | str) -> str:
        """Saves data (bytes or string) to the specified path.
        
        Args:
            path: Relative path/key.
            data: Content to save.
            
        Returns:
            str: Resolved path or URI.

        Raises:
            AppException: If storage is inaccessible or write fails (STORAGE_ACCESS_FAILED).
        """
        ...

    async def read(self, path: str) -> bytes:
        """Reads raw bytes from the specified path.
        
        Args:
            path: Relative path/key.
            
        Returns:
            bytes: Content.

        Raises:
            AppException: If file not found (FILE_NOT_FOUND) or read fails (STORAGE_ACCESS_FAILED).
        """
        ...

    async def delete(self, path: str) -> bool:
        """Deletes file at path.
        
        Args:
            path: Relative path/key.
            
        Returns:
            bool: True if deleted, False if not found (idempotent-ish check).

        Raises:
            AppException: If storage is inaccessible (STORAGE_ACCESS_FAILED).
        """
        ...

    async def exists(self, path: str) -> bool:
        """Checks if file exists.
        
        Args:
            path: Relative path/key.
            
        Returns:
            bool: True if exists.
        
        Raises:
            AppException: If storage connectivity fails (optional, usually merely returns False).
        """
        ...

    async def get_url(self, path: str) -> str | None:
        """Returns a public or pre-signed URL for the file.
        
        Args:
            path: Relative path/key.
            
        Returns:
            str | None: URL if supported, None otherwise.
        """
        ...

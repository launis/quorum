"""Google Cloud Storage File Driver Implementation."""

from __future__ import annotations

import asyncio
import importlib
import importlib.util
import logging
from collections.abc import Callable
from typing import Any, override

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.services.file_driver import FileDriver
from backend_v2.settings import get_settings

storage: Any = None
if importlib.util.find_spec("google.cloud.storage") is not None:
    storage = importlib.import_module("google.cloud.storage")

__all__ = [
    "GCSFileDriver",
]

logger = logging.getLogger(__name__)


class GCSFileDriver(FileDriver):
    """Google Cloud Storage driver implementing the asynchronous FileDriver protocol.

    Adapts the synchronous google-cloud-storage SDK to non-blocking async execution
    via asyncio.to_thread bounded by Settings-governed timeouts.

    Attributes:
        bucket_name: Target Google Cloud Storage bucket name.
        timeout_seconds: Bounded execution timeout in seconds for GCS operations.
    """

    def __init__(self, bucket_name: str, *, timeout_seconds: float | None = None) -> None:
        """Initialize the Google Cloud Storage driver.

        Args:
            bucket_name: Target GCS bucket name.
            timeout_seconds: Optional explicit timeout override in seconds; resolves
                from settings.http_client_timeout_seconds when omitted.

        Raises:
            AppException: With STORAGE_BUCKET_NOT_FOUND if bucket_name is blank,
                STORAGE_CONFIG_ERROR if timeout_seconds is non-positive, or
                SERVICE_DEPENDENCY_MISSING if google-cloud-storage is unavailable.
        """
        cleaned_bucket = bucket_name.strip()
        if not cleaned_bucket:
            msg = "GCS Bucket name cannot be empty"
            logger.error(
                "[GCSFileDriver] %s: %s",
                ErrorCodes.STORAGE_BUCKET_NOT_FOUND.name,
                msg,
                exc_info=True,
                extra={"error_code": ErrorCodes.STORAGE_BUCKET_NOT_FOUND.value},
            )
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_BUCKET_NOT_FOUND.value},
            )

        if storage is None:
            msg = "google-cloud-storage library not installed"
            logger.error(
                "[GCSFileDriver] %s: %s",
                ErrorCodes.SERVICE_DEPENDENCY_MISSING.name,
                msg,
                exc_info=True,
                extra={"error_code": ErrorCodes.SERVICE_DEPENDENCY_MISSING.value},
            )
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.SERVICE_DEPENDENCY_MISSING.value},
            )

        resolved_timeout = get_settings().http_client_timeout_seconds
        if timeout_seconds is not None:
            resolved_timeout = timeout_seconds

        if resolved_timeout <= 0:
            msg = f"GCS operation timeout must be positive, got {resolved_timeout}"
            logger.error(
                "[GCSFileDriver] %s: %s",
                ErrorCodes.STORAGE_CONFIG_ERROR.name,
                msg,
                exc_info=True,
                extra={"error_code": ErrorCodes.STORAGE_CONFIG_ERROR.value, "timeout_seconds": resolved_timeout},
            )
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_CONFIG_ERROR.value},
            )

        self.bucket_name = cleaned_bucket
        self.timeout_seconds = resolved_timeout
        self._client: Any = None
        self._bucket: Any = None

    def _validate_blob_key(self, key: str, *, context_key: str) -> str:
        """Validate that a target GCS blob path or prefix is non-empty.

        Args:
            key: Raw blob path or directory prefix.
            context_key: Structured logging field name ('path' or 'prefix').

        Returns:
            Normalized key stripped of surrounding whitespace and leading slashes.

        Raises:
            AppException: With FILESYSTEM_VIOLATION if the normalized key is empty.
        """
        cleaned = key.strip().lstrip("/")
        if not cleaned:
            msg = f"GCS {context_key} cannot be empty"
            logger.error(
                "[GCSFileDriver] %s: %s",
                ErrorCodes.FILESYSTEM_VIOLATION.name,
                msg,
                exc_info=True,
                extra={"error_code": ErrorCodes.FILESYSTEM_VIOLATION.value, context_key: key},
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.FILESYSTEM_VIOLATION.value},
            )
        return cleaned

    def _get_bucket(self) -> Any:
        """Lazily initialize and return the cached GCS bucket handle.

        Returns:
            GCS bucket instance bound to bucket_name.

        Raises:
            AppException: With STORAGE_ACCESS_FAILED if client or bucket initialization fails.
        """
        try:
            if not self._client:
                self._client = storage.Client()
            if not self._bucket:
                self._bucket = self._client.bucket(self.bucket_name)
            return self._bucket
        except AppException:
            raise
        except Exception as e:
            logger.error(
                "[GCSFileDriver] %s: Failed to initialize GCS client/bucket '%s': %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                self.bucket_name,
                e,
                exc_info=True,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value, "bucket_name": self.bucket_name},
            )
            raise AppException(
                message=f"GCS Initialization Failed: {e!s}",
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from e

    async def _run_gcs_operation[T](
        self,
        sync_fn: Callable[[], T],
        *,
        operation_label: str,
        context_key: str,
        context_value: str,
    ) -> T:
        """Execute a synchronous GCS SDK callable on a worker thread with bounded timeout.

        Consolidates thread dispatch, Python 3.14 asyncio.timeout enforcement, and
        RFC 7807 Dual-Reporting exception translation across all driver operations.

        Args:
            sync_fn: Zero-argument callable performing synchronous GCS SDK I/O.
            operation_label: Human-readable label describing the operation for error reporting.
            context_key: Structured logging metadata key ('path' or 'prefix').
            context_value: Target blob path or directory prefix value.

        Returns:
            Typed result returned by sync_fn.

        Raises:
            AppException: With FILE_NOT_FOUND (404) if sync_fn raises FileNotFoundError,
                or STORAGE_ACCESS_FAILED (500) on timeout or SDK transport failure.
        """
        try:
            async with asyncio.timeout(self.timeout_seconds):
                return await asyncio.to_thread(sync_fn)
        except FileNotFoundError as e:
            logger.error(
                "[GCSFileDriver] %s: %s",
                ErrorCodes.FILE_NOT_FOUND.name,
                e,
                exc_info=True,
                extra={"error_code": ErrorCodes.FILE_NOT_FOUND.value, context_key: context_value},
            )
            raise AppException(
                message=str(e),
                status_code=404,
                details={"error_code": ErrorCodes.FILE_NOT_FOUND.value},
            ) from e
        except AppException:
            raise
        except Exception as e:
            logger.error(
                "[GCSFileDriver] %s: %s Failed for %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                operation_label,
                context_value,
                e,
                exc_info=True,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value, context_key: context_value},
            )
            raise AppException(
                message=f"GCS {operation_label} Failed: {e!s}",
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from e

    @override
    async def save(self, path: str, data: bytes | str) -> str:
        """Upload string or bytes payload to the GCS bucket.

        Args:
            path: Target blob storage path.
            data: Binary payload or string content to persist.

        Returns:
            Canonical gs:// URI string of the persisted blob.

        Raises:
            AppException: With FILESYSTEM_VIOLATION if path is empty, or
                STORAGE_ACCESS_FAILED if upload times out or fails.
        """
        cleaned_path = self._validate_blob_key(path, context_key="path")

        def _sync_save() -> str:
            bucket = self._get_bucket()
            blob = bucket.blob(cleaned_path)
            content_type = "text/plain" if isinstance(data, str) else "application/octet-stream"
            blob.upload_from_string(data, content_type=content_type)
            return f"gs://{self.bucket_name}/{cleaned_path}"

        return await self._run_gcs_operation(
            _sync_save,
            operation_label="Save",
            context_key="path",
            context_value=cleaned_path,
        )

    @override
    async def read(self, path: str) -> bytes:
        """Download raw bytes content of a blob from GCS.

        Args:
            path: Target blob storage path.

        Returns:
            Downloaded raw bytes content.

        Raises:
            AppException: With FILESYSTEM_VIOLATION if path is empty,
                FILE_NOT_FOUND if blob does not exist, or
                STORAGE_ACCESS_FAILED if download times out or fails.
        """
        cleaned_path = self._validate_blob_key(path, context_key="path")

        def _sync_read() -> bytes:
            bucket = self._get_bucket()
            blob = bucket.blob(cleaned_path)
            if not blob.exists():
                raise FileNotFoundError(f"File not found in GCS: {cleaned_path}")
            res: bytes = blob.download_as_bytes()
            return res

        return await self._run_gcs_operation(
            _sync_read,
            operation_label="Read",
            context_key="path",
            context_value=cleaned_path,
        )

    @override
    async def delete(self, path: str) -> bool:
        """Delete a single blob from GCS.

        Args:
            path: Target blob storage path.

        Returns:
            True if deletion succeeded.

        Raises:
            AppException: With FILESYSTEM_VIOLATION if path is empty,
                FILE_NOT_FOUND if blob does not exist, or
                STORAGE_ACCESS_FAILED if deletion times out or fails.
        """
        cleaned_path = self._validate_blob_key(path, context_key="path")

        def _sync_delete() -> bool:
            bucket = self._get_bucket()
            blob = bucket.blob(cleaned_path)
            if not blob.exists():
                raise FileNotFoundError(f"Cannot delete non-existent GCS blob: {cleaned_path}")
            blob.delete()
            return True

        return await self._run_gcs_operation(
            _sync_delete,
            operation_label="Delete",
            context_key="path",
            context_value=cleaned_path,
        )

    @override
    async def delete_directory(self, prefix: str) -> bool:
        """Delete all blobs matching prefix directory from GCS.

        Args:
            prefix: Directory prefix key to delete.

        Returns:
            True if directory deletion succeeded.

        Raises:
            AppException: With FILESYSTEM_VIOLATION if prefix is empty,
                FILE_NOT_FOUND if no blobs match prefix, or
                STORAGE_ACCESS_FAILED if batch deletion times out or fails.
        """
        cleaned_prefix = self._validate_blob_key(prefix, context_key="prefix")

        def _sync_delete_directory() -> bool:
            bucket = self._get_bucket()
            prefix_with_slash = cleaned_prefix if cleaned_prefix.endswith("/") else f"{cleaned_prefix}/"
            blobs = list(bucket.list_blobs(prefix=prefix_with_slash))
            if not blobs:
                raise FileNotFoundError(f"Cannot delete non-existent GCS directory: {cleaned_prefix}")

            bucket.delete_blobs(blobs)
            return True

        return await self._run_gcs_operation(
            _sync_delete_directory,
            operation_label="Directory Delete",
            context_key="prefix",
            context_value=cleaned_prefix,
        )

    @override
    async def exists(self, path: str) -> bool:
        """Check whether a blob exists in GCS.

        Args:
            path: Target blob storage path.

        Returns:
            True if blob exists, False otherwise.

        Raises:
            AppException: With FILESYSTEM_VIOLATION if path is empty, or
                STORAGE_ACCESS_FAILED if connectivity times out or fails.
        """
        cleaned_path = self._validate_blob_key(path, context_key="path")

        def _sync_exists() -> bool:
            bucket = self._get_bucket()
            blob = bucket.blob(cleaned_path)
            exists: bool = blob.exists()
            return exists

        return await self._run_gcs_operation(
            _sync_exists,
            operation_label="Exists Check",
            context_key="path",
            context_value=cleaned_path,
        )

    @override
    async def get_url(self, path: str) -> str | None:
        """Return public HTTPS URL link for the target blob path.

        Args:
            path: Target blob storage path.

        Returns:
            Full public storage HTTPS URL string.

        Raises:
            AppException: With STORAGE_BUCKET_NOT_FOUND if bucket_name is blank, or
                FILESYSTEM_VIOLATION if path is empty.
        """
        if not self.bucket_name.strip():
            msg = "GCS bucket name is missing. Zero-Compromise Fail-Fast enforced."
            logger.error(
                "[GCSFileDriver] %s: %s",
                ErrorCodes.STORAGE_BUCKET_NOT_FOUND.name,
                msg,
                exc_info=True,
                extra={"error_code": ErrorCodes.STORAGE_BUCKET_NOT_FOUND.value},
            )
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_BUCKET_NOT_FOUND.value},
            )
        cleaned_path = self._validate_blob_key(path, context_key="path")
        return f"https://storage.googleapis.com/{self.bucket_name}/{cleaned_path}"

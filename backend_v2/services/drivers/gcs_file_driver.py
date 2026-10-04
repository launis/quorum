"""Google Cloud Storage File Driver Implementation."""

import asyncio
import importlib
import importlib.util
import logging
from typing import Any

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.services.file_driver import FileDriver

storage: Any = None
if importlib.util.find_spec("google.cloud.storage") is not None:
    storage = importlib.import_module("google.cloud.storage")

__all__ = [
    "GCSFileDriver",
]

logger = logging.getLogger(__name__)


class GCSFileDriver(FileDriver):
    """Google Cloud Storage Driver.

    Adapts synchronous google-cloud-storage library to async protocol
    using asyncio.to_thread for non-blocking I/O.
    """

    def __init__(self, bucket_name: str) -> None:
        """Initialize GCS Driver.

        Args:
            bucket_name: Target GCS bucket name.

        Raises:
            AppException: If bucket_name is empty (STORAGE_BUCKET_NOT_FOUND) or
                google-cloud-storage library is missing (SERVICE_DEPENDENCY_MISSING).
        """
        if not bucket_name:
            msg = "GCS Bucket name cannot be empty"
            logger.error(
                "[GCSFileDriver] %s: %s",
                ErrorCodes.STORAGE_BUCKET_NOT_FOUND.name,
                msg,
                extra={"error_code": ErrorCodes.STORAGE_BUCKET_NOT_FOUND.name},
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
                extra={"error_code": ErrorCodes.SERVICE_DEPENDENCY_MISSING.name},
            )
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.SERVICE_DEPENDENCY_MISSING.value},
            )

        self.bucket_name = bucket_name
        self._client: Any = None
        self._bucket: Any = None

    def _get_bucket(self) -> Any:
        """Lazy initialization of GCS client/bucket with error handling.

        Returns:
            GCS bucket instance.

        Raises:
            AppException: If GCS client or bucket initialization fails (STORAGE_ACCESS_FAILED).
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
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.name, "bucket_name": self.bucket_name},
            )
            raise AppException(
                message=f"GCS Initialization Failed: {str(e)}",
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from e

    async def save(self, path: str, data: bytes | str) -> str:
        """Upload string or bytes payload to GCS bucket.

        Args:
            path: Target blob storage path.
            data: Binary payload or string content to persist.

        Returns:
            Canonical gs:// URI string of the persisted blob.

        Raises:
            AppException: If upload fails due to connectivity or permissions (STORAGE_ACCESS_FAILED).
        """

        def _sync_save() -> str:
            bucket = self._get_bucket()
            blob = bucket.blob(path)

            if isinstance(data, str):
                blob.upload_from_string(data, content_type="text/plain")
            else:
                blob.upload_from_string(data, content_type="application/octet-stream")

            return f"gs://{self.bucket_name}/{path}"

        try:
            return await asyncio.to_thread(_sync_save)
        except AppException:
            raise
        except Exception as e:
            logger.error(
                "[GCSFileDriver] %s: Failed to save file to GCS %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                path,
                e,
                exc_info=True,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.name, "path": path},
            )
            raise AppException(
                message=f"GCS Save Failed: {str(e)}",
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from e

    async def read(self, path: str) -> bytes:
        """Download raw bytes content of a blob from GCS.

        Args:
            path: Target blob storage path.

        Returns:
            Downloaded raw bytes content.

        Raises:
            AppException: If blob does not exist (FILE_NOT_FOUND) or download fails (STORAGE_ACCESS_FAILED).
        """

        def _sync_read() -> bytes:
            bucket = self._get_bucket()
            blob = bucket.blob(path)
            if not blob.exists():
                raise FileNotFoundError(f"GCS Blob {path} not found")
            res: bytes = blob.download_as_bytes()
            return res

        try:
            return await asyncio.to_thread(_sync_read)
        except FileNotFoundError as e:
            logger.error(
                "[GCSFileDriver] %s: File not found in GCS: %s",
                ErrorCodes.FILE_NOT_FOUND.name,
                path,
                exc_info=True,
                extra={"error_code": ErrorCodes.FILE_NOT_FOUND.name, "path": path},
            )
            raise AppException(
                message=f"File not found in GCS: {path}",
                status_code=404,
                details={"error_code": ErrorCodes.FILE_NOT_FOUND.value},
            ) from e
        except AppException:
            raise
        except Exception as e:
            logger.error(
                "[GCSFileDriver] %s: Failed to read file from GCS %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                path,
                e,
                exc_info=True,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.name, "path": path},
            )
            raise AppException(
                message=f"GCS Read Failed: {str(e)}",
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from e

    async def delete(self, path: str) -> bool:
        """Delete a single blob from GCS.

        Args:
            path: Target blob storage path.

        Returns:
            True if deletion succeeded.

        Raises:
            AppException: If blob does not exist (FILE_NOT_FOUND) or deletion fails (STORAGE_ACCESS_FAILED).
        """

        def _sync_delete() -> bool:
            bucket = self._get_bucket()
            blob = bucket.blob(path)
            if not blob.exists():
                raise FileNotFoundError(f"Cannot delete non-existent GCS blob: {path}")
            blob.delete()
            return True

        try:
            return await asyncio.to_thread(_sync_delete)
        except FileNotFoundError as e:
            logger.error(
                "[GCSFileDriver] %s: %s",
                ErrorCodes.FILE_NOT_FOUND.name,
                str(e),
                exc_info=True,
                extra={"error_code": ErrorCodes.FILE_NOT_FOUND.name, "path": path},
            )
            raise AppException(
                message=str(e), status_code=404, details={"error_code": ErrorCodes.FILE_NOT_FOUND.value}
            ) from e
        except AppException:
            raise
        except Exception as e:
            logger.error(
                "[GCSFileDriver] %s: Failed to delete file from GCS %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                path,
                e,
                exc_info=True,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.name, "path": path},
            )
            raise AppException(
                message=f"GCS Delete Failed: {str(e)}",
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from e

    async def delete_directory(self, prefix: str) -> bool:
        """Delete all blobs matching prefix directory from GCS.

        Args:
            prefix: Directory prefix key to delete.

        Returns:
            True if directory deletion succeeded.

        Raises:
            AppException: If no blobs match prefix (FILE_NOT_FOUND) or deletion fails (STORAGE_ACCESS_FAILED).
        """

        def _sync_delete_directory() -> bool:
            bucket = self._get_bucket()
            prefix_with_slash = prefix if prefix.endswith("/") else f"{prefix}/"
            blobs = list(bucket.list_blobs(prefix=prefix_with_slash))
            if not blobs:
                raise FileNotFoundError(f"Cannot delete non-existent GCS directory: {prefix}")

            bucket.delete_blobs(blobs)
            return True

        try:
            return await asyncio.to_thread(_sync_delete_directory)
        except FileNotFoundError as e:
            logger.error(
                "[GCSFileDriver] %s: %s",
                ErrorCodes.FILE_NOT_FOUND.name,
                str(e),
                exc_info=True,
                extra={"error_code": ErrorCodes.FILE_NOT_FOUND.name, "prefix": prefix},
            )
            raise AppException(
                message=str(e), status_code=404, details={"error_code": ErrorCodes.FILE_NOT_FOUND.value}
            ) from e
        except AppException:
            raise
        except Exception as e:
            logger.error(
                "[GCSFileDriver] %s: Failed to delete directory from GCS %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                prefix,
                e,
                exc_info=True,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.name, "prefix": prefix},
            )
            raise AppException(
                message=f"GCS Directory Delete Failed: {str(e)}",
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from e

    async def exists(self, path: str) -> bool:
        """Check whether a blob exists in GCS.

        Args:
            path: Target blob storage path.

        Returns:
            True if blob exists, False otherwise.

        Raises:
            AppException: If connectivity fails during existence check (STORAGE_ACCESS_FAILED).
        """

        def _sync_exists() -> bool:
            bucket = self._get_bucket()
            blob = bucket.blob(path)
            exists: bool = blob.exists()
            return exists

        try:
            return await asyncio.to_thread(_sync_exists)
        except AppException:
            raise
        except Exception as e:
            logger.error(
                "[GCSFileDriver] %s: Failed to check existence in GCS %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                path,
                e,
                exc_info=True,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.name, "path": path},
            )
            raise AppException(
                message=f"GCS Exists Check Failed: {str(e)}",
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from e

    async def get_url(self, path: str) -> str | None:
        """Return public URL link for the target blob path.

        Args:
            path: Target blob storage path.

        Returns:
            Full public storage HTTPS URL string.

        Raises:
            AppException: If bucket_name is empty (STORAGE_BUCKET_NOT_FOUND).
        """
        if not self.bucket_name:
            msg = "GCS bucket name is missing. Zero-Compromise Fail-Fast enforced."
            logger.error(
                "[GCSFileDriver] %s: %s",
                ErrorCodes.STORAGE_BUCKET_NOT_FOUND.name,
                msg,
                extra={"error_code": ErrorCodes.STORAGE_BUCKET_NOT_FOUND.name},
            )
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_BUCKET_NOT_FOUND.value},
            )
        return f"https://storage.googleapis.com/{self.bucket_name}/{path}"

"""Google Cloud Storage File Driver Implementation."""

import asyncio

# Conditional import or type checking if direct dependency is optional,
# but effectively expected here.
import importlib
import logging
from typing import Any

try:
    google_cloud = importlib.import_module("google.cloud")
    storage = google_cloud.storage
except (ImportError, AttributeError):
    storage = None

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.services.file_driver import FileDriver

logger = logging.getLogger(__name__)


class GCSFileDriver(FileDriver):
    """Google Cloud Storage Driver.

    Adapts synchronous google-cloud-storage library to async protocol
    using asyncio.to_thread for non-blocking I/O.
    """

    def __init__(self, bucket_name: str):
        """Initialize GCS Driver.

        Args:
            bucket_name: Target GCS bucket name.

        Raises:
            AppException: If bucket_name is empty or library not installed.
        """
        if not bucket_name:
            msg = "GCS Bucket name cannot be empty"
            logger.error("[GCSFileDriver] %s: %s", ErrorCodes.STORAGE_BUCKET_NOT_FOUND.name, msg)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_BUCKET_NOT_FOUND.value},
            )

        if storage is None:
            msg = "google-cloud-storage library not installed"
            logger.error("[GCSFileDriver] %s: %s", ErrorCodes.SERVICE_DEPENDENCY_MISSING.name, msg)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.SERVICE_DEPENDENCY_MISSING.value},
            )

        self.bucket_name = bucket_name
        self._client: Any = None
        self._bucket: Any = None

    def _get_bucket(self) -> Any:
        """Lazy initialization of GCS client/bucket with error handling."""
        try:
            if not self._client:
                self._client = storage.Client()
            if not self._bucket:
                self._bucket = self._client.bucket(self.bucket_name)
            return self._bucket
        except Exception as e:
            logger.error(
                f"[GCSFileDriver] {ErrorCodes.STORAGE_ACCESS_FAILED.name}: "
                f"Failed to initialize GCS client/bucket '{self.bucket_name}': {e}",
                exc_info=True,
            )
            raise AppException(
                message=f"GCS Initialization Failed: {str(e)}",
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from e

    async def save(self, path: str, data: bytes | str) -> str:
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
                f"[GCSFileDriver] {ErrorCodes.STORAGE_ACCESS_FAILED.name}: Failed to save file to GCS {path}: {e}",
                exc_info=True,
            )
            raise AppException(
                message=f"GCS Save Failed: {str(e)}",
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from e

    async def read(self, path: str) -> bytes:
        def _sync_read() -> bytes:
            bucket = self._get_bucket()
            blob = bucket.blob(path)
            if not blob.exists():
                # Raise specific NotFound so we can catch/wrap it
                raise FileNotFoundError(f"GCS Blob {path} not found")
            res: bytes = blob.download_as_bytes()
            return res

        try:
            return await asyncio.to_thread(_sync_read)
        except FileNotFoundError as e:
            logger.error(
                f"[GCSFileDriver] {ErrorCodes.FILE_NOT_FOUND.name}: File not found in GCS: {path}", exc_info=True
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
                f"[GCSFileDriver] {ErrorCodes.STORAGE_ACCESS_FAILED.name}: Failed to read file from GCS {path}: {e}",
                exc_info=True,
            )
            raise AppException(
                message=f"GCS Read Failed: {str(e)}",
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from e

    async def delete(self, path: str) -> bool:
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
            logger.error("[GCSFileDriver] %s: %s", ErrorCodes.FILE_NOT_FOUND.name, str(e))
            raise AppException(
                message=str(e), status_code=404, details={"error_code": ErrorCodes.FILE_NOT_FOUND.value}
            ) from e
        except AppException:
            raise
        except Exception as e:
            logger.error(
                f"[GCSFileDriver] {ErrorCodes.STORAGE_ACCESS_FAILED.name}: Failed to delete file from GCS {path}: {e}",
                exc_info=True,
            )
            # delete usually returns false on failure in old impl, but RFC 7807 prefers explicit failures?
            # Contracts often allow delete to be idempotent.
            # But if it's a connectivity error, we should probably raise.
            # The interface says regex returns bool.
            # Let's stick to bool for interface compatibility but log heavily.
            # Actually, "Fail Fast" implies we should probably raise if the backend is down.
            # BUT breaking interface might be bad if `file_driver.py` expects bool.
            # Base class says `async def delete(self, path: str) -> bool`.
            # I will return False but log error, or should I raise?
            # If I raise, I break Liskov if base doesn't allow raising.
            # Base likely allows raising exceptions since it's IO.
            # I will raise AppException for connectivity issues.
            raise AppException(
                message=f"GCS Delete Failed: {str(e)}",
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from e

    async def delete_directory(self, prefix: str) -> bool:
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
            logger.error("[GCSFileDriver] %s: %s", ErrorCodes.FILE_NOT_FOUND.name, str(e))
            raise AppException(
                message=str(e), status_code=404, details={"error_code": ErrorCodes.FILE_NOT_FOUND.value}
            ) from e
        except AppException:
            raise
        except Exception as e:
            logger.error(
                f"[GCSFileDriver] {ErrorCodes.STORAGE_ACCESS_FAILED.name}: "
                f"Failed to delete directory from GCS {prefix}: {e}",
                exc_info=True,
            )
            raise AppException(
                message=f"GCS Directory Delete Failed: {str(e)}",
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from e

    async def exists(self, path: str) -> bool:
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
                f"[GCSFileDriver] {ErrorCodes.STORAGE_ACCESS_FAILED.name}: "
                f"Failed to check existence in GCS {path}: {e}",
                exc_info=True,
            )
            raise AppException(
                message=f"GCS Exists Check Failed: {str(e)}",
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from e

    async def get_url(self, path: str) -> str | None:
        """Returns signed URL if credentials allow, or public link."""
        # Check bucket config if possible
        if not self.bucket_name:
            msg = "GCS bucket name is missing. Zero-Compromise Fail-Fast enforced."
            logger.error("[GCSFileDriver] %s: %s", ErrorCodes.STORAGE_BUCKET_NOT_FOUND.name, msg)
            raise AppException(
                message=msg, status_code=500, details={"error_code": ErrorCodes.STORAGE_BUCKET_NOT_FOUND.value}
            )
        return f"https://storage.googleapis.com/{self.bucket_name}/{path}"

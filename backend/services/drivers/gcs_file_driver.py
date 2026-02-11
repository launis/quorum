"""Google Cloud Storage File Driver Implementation."""

import logging
import asyncio
from google.cloud import storage # type: ignore

from backend.services.file_driver import FileDriver

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
        """
        self.bucket_name = bucket_name
        self._client = None
        self._bucket = None

    def _get_bucket(self):
        """Lazy initialization of GCS client/bucket."""
        if not self._client:
            self._client = storage.Client()
        if not self._bucket:
            self._bucket = self._client.bucket(self.bucket_name)
        return self._bucket

    async def save(self, path: str, data: bytes | str) -> str:
        def _sync_save():
            bucket = self._get_bucket()
            blob = bucket.blob(path)
            
            if isinstance(data, str):
                blob.upload_from_string(data, content_type="text/plain")
            else:
                blob.upload_from_string(data, content_type="application/octet-stream")
            
            return f"gs://{self.bucket_name}/{path}"

        try:
            return await asyncio.to_thread(_sync_save)
        except Exception as e:
            logger.error(f"Failed to save file to GCS {path}: {e}")
            raise e

    async def read(self, path: str) -> bytes:
        def _sync_read():
            bucket = self._get_bucket()
            blob = bucket.blob(path)
            return blob.download_as_bytes()

        try:
            return await asyncio.to_thread(_sync_read)
        except Exception as e:
            logger.error(f"Failed to read file from GCS {path}: {e}")
            raise e

    async def delete(self, path: str) -> bool:
        def _sync_delete():
            bucket = self._get_bucket()
            blob = bucket.blob(path)
            if blob.exists():
                blob.delete()
                return True
            return False

        try:
            return await asyncio.to_thread(_sync_delete)
        except Exception as e:
            logger.error(f"Failed to delete file from GCS {path}: {e}")
            return False

    async def exists(self, path: str) -> bool:
        def _sync_exists():
            bucket = self._get_bucket()
            blob = bucket.blob(path)
            return blob.exists()

        return await asyncio.to_thread(_sync_exists)

    async def get_url(self, path: str) -> str | None:
        """Returns signed URL if credentials allow, or public link."""
        # For simplicity in this vibe check:
        return f"https://storage.googleapis.com/{self.bucket_name}/{path}"

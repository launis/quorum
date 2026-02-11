"""Storage Service abstraction for local and cloud backends (Async).

Updated V2.9: Fits File Driver Pattern.
"""

import logging
from typing import cast
from backend.services.file_driver import FileDriver
from backend.services.drivers.local_file_driver import LocalFileDriver
from backend.services.drivers.gcs_file_driver import GCSFileDriver
from backend.settings import get_settings

logger = logging.getLogger(__name__)

# Re-export FileDriver as AbstractStorage for backward compatibility (typing only)
# But users should migrate to FileDriver
AbstractStorage = FileDriver


def get_storage_client() -> FileDriver:
    """Factory function to return the configured ASYNC storage client."""
    settings = get_settings()

    if settings.environment == "production" and settings.storage_bucket_name:
        logger.info(f"Using GCS Storage Driver (Bucket: {settings.storage_bucket_name})")
        return GCSFileDriver(bucket_name=settings.storage_bucket_name)

    # Default to Local
    base_url = str(settings.api_url) if settings.api_url else "http://localhost:8000"
    # Construct base URL for files if needed, e.g. /files/
    # For now, just pass base_url
    
    return LocalFileDriver(base_path=settings.files_dir, base_url=base_url)


# Deprecated synchronous classes are removed.
# Any outstanding usage will fail fast (AttributeError/TypeError), signaling required refactor.

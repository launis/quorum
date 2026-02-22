"""Storage Service Factory (V2026).

This module provides a singleton factory for obtaining the active StorageDriver
based on the application configuration.
"""

import logging
from functools import lru_cache

from backend.exceptions import AppException, ErrorCodes
from backend.services.drivers.gcs_file_driver import GCSFileDriver
from backend.services.drivers.local_file_driver import LocalFileDriver
from backend.services.file_driver import FileDriver
from backend.settings import StorageBackend, get_settings

logger = logging.getLogger(__name__)


@lru_cache
def get_storage_driver() -> FileDriver:
    """Returns the singleton StorageDriver instance.

    The driver is selected based on settings.storage_backend:
    - FIRESTORE -> GCSFileDriver (using settings.storage_bucket_name)
    - LOCAL -> LocalFileDriver (using settings.files_dir)
    - MOCK -> LocalFileDriver (using settings.files_dir)

    Returns:
        FileDriver: The initialized driver.

    Raises:
        ValueError: If FIRESTORE backend is selected but storage_bucket_name is missing.
    """
    settings = get_settings()
    backend = settings.active_backend

    if backend == StorageBackend.FIRESTORE:
        bucket_name = settings.storage_bucket_name
        if not bucket_name:
            raise AppException(
                message="CRITICAL: STORAGE_BACKEND=FIRESTORE requires STORAGE_BUCKET_NAME to be set.",
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_CONFIG_ERROR},
            )
        logger.info(f"Initializing GCSFileDriver with bucket: {bucket_name}")
        return GCSFileDriver(bucket_name=bucket_name)

    # Default to Local for LOCAL and MOCK backends
    base_path = settings.files_dir
    base_url = f"{settings.api_url}/files" if settings.api_url else None

    logger.info(f"Initializing LocalFileDriver at: {base_path}")
    return LocalFileDriver(base_path=base_path, base_url=base_url)

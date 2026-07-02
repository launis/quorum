"""Storage Service Factory (V2026).

This module provides a singleton factory for obtaining the active StorageDriver
based on the application configuration.
"""

import logging
from functools import lru_cache

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.services.drivers.gcs_file_driver import GCSFileDriver
from backend_v2.services.drivers.local_file_driver import LocalFileDriver
from backend_v2.services.file_driver import FileDriver
from backend_v2.settings import StorageBackend, get_settings

logger = logging.getLogger(__name__)


@lru_cache
def get_storage_driver() -> FileDriver:
    """Returns the singleton StorageDriver instance.

    The driver is selected based on settings.storage_backend:
    - FIRESTORE -> GCSFileDriver (using settings.storage_bucket_name)
    - LOCAL -> LocalFileDriver (using settings.files_dir)

    Returns:
        FileDriver: The initialized driver.

    Raises:
        AppException: If FIRESTORE backend is selected but storage_bucket_name is missing,
            or if an unknown StorageBackend is configured.
    """
    settings = get_settings()
    backend = settings.active_backend

    if backend == StorageBackend.FIRESTORE:
        bucket_name = settings.storage_bucket_name
        if not bucket_name:
            msg = "CRITICAL: STORAGE_BACKEND=FIRESTORE requires STORAGE_BUCKET_NAME to be set."
            logger.error("[StorageService] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
            )
        logger.info("Initializing GCSFileDriver with bucket: %s", bucket_name)
        return GCSFileDriver(bucket_name=bucket_name)

    if backend == StorageBackend.LOCAL:
        base_path = settings.files_dir
        base_url = f"{settings.api_url}/files" if settings.api_url else None

        logger.info("Initializing LocalFileDriver at: %s", base_path)
        return LocalFileDriver(base_path=base_path, base_url=base_url)

    # Fail Fast on unknown backends
    msg = f"Unsupported StorageBackend configured: {backend}"
    logger.error("[StorageService] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
    raise AppException(
        message=msg,
        status_code=500,
        details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
    )

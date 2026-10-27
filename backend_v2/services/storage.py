"""Storage Service Factory (V2026).

This module provides a singleton factory for obtaining the active FileDriver
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
    """Returns the singleton FileDriver instance for PostgreSQL 19 runtime.

    The driver is selected based on settings.active_backend (StorageBackend.POSTGRES):
    - GCSFileDriver if settings.storage_bucket_name is configured.
    - LocalFileDriver (using settings.files_dir) otherwise.

    Returns:
        FileDriver: The initialized file storage driver.

    Raises:
        AppException: If an unsupported StorageBackend is configured.
    """
    settings = get_settings()
    backend = settings.active_backend

    if backend == StorageBackend.POSTGRES:
        if settings.storage_bucket_name:
            logger.info("Initializing GCSFileDriver for POSTGRES with bucket: %s", settings.storage_bucket_name)
            return GCSFileDriver(bucket_name=settings.storage_bucket_name)

        base_path = settings.files_dir
        base_url = None
        if settings.api_url:
            base_url = f"{settings.api_url}/files"

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

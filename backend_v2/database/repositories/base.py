"""Database repository implementation module."""

from backend_v2.database.driver import StorageDriver


class BaseRepository:
    """Base repository providing access to the injected StorageDriver."""

    def __init__(self, driver: StorageDriver):
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        self.driver = driver


class AppendOnlyRepositoryBase(BaseRepository):
    """Base repository for entities that require append-only versioning."""

    def _increment_version(self, id_str: str) -> tuple[str, str, int]:
        """Parses an ID into (base_id, full_new_id, version)."""
        if "_v" in id_str:
            base_id, v_str = id_str.rsplit("_v", 1)
            try:
                version = int(v_str) + 1
            except ValueError:
                version = 2
        else:
            base_id = id_str
            version = 2

        new_id = f"{base_id}_v{version}"
        return base_id, new_id, version

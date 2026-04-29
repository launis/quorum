from backend_v2.database.driver import StorageDriver


class BaseRepository:
    """Base repository providing access to the injected StorageDriver."""

    def __init__(self, driver: StorageDriver):
        self.driver = driver


class AppendOnlyRepositoryBase(BaseRepository):
    """Base repository for entities that require append-only versioning."""

    def _increment_version(self, id_str: str) -> tuple[str, str, int]:
        """Parses an ID into (slug, full_new_id, version)."""
        if "_v" in id_str:
            slug, v_str = id_str.rsplit("_v", 1)
            try:
                version = int(v_str) + 1
            except ValueError:
                version = 2
        else:
            slug = id_str
            version = 2

        new_id = f"{slug}_v{version}"
        return slug, new_id, version

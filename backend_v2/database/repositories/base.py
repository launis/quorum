"""Database repository implementation module."""

from typing import Annotated

from pydantic import ConfigDict, Field

from backend_v2.database.driver import StorageDriver
from backend_v2.models.core_base import V2CoreBase

__all__ = [
    "AppendOnlyRepositoryBase",
    "BaseRepository",
    "VersionIncrementDTO",
]


class VersionIncrementDTO(V2CoreBase):
    """Result of incrementing an entity version identifier."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    base_id: Annotated[str, Field(description="Base identifier prefix before version suffix.")]
    new_id: Annotated[str, Field(description="Newly generated identifier with incremented version suffix.")]
    version: Annotated[int, Field(description="Incremented integer version.")]


class BaseRepository:
    """Base repository providing access to the injected StorageDriver."""

    def __init__(self, driver: StorageDriver) -> None:
        """Initialize the repository with an injected storage driver.

        Args:
            driver: Injected storage driver.
        """
        self.driver = driver


class AppendOnlyRepositoryBase(BaseRepository):
    """Base repository for entities that require append-only versioning."""

    def _increment_version(self, id_str: str) -> VersionIncrementDTO:
        """Parse an ID into VersionIncrementDTO containing base_id, new_id, and version.

        Args:
            id_str: Entity identifier to inspect and increment.

        Returns:
            VersionIncrementDTO containing the extracted base ID, newly generated versioned ID, and version number.
        """
        if "_v" in id_str:
            base_id, v_str = id_str.rsplit("_v", 1)
            if v_str.isdigit():
                version = int(v_str) + 1
            else:
                version = 2
        else:
            base_id = id_str
            version = 2

        new_id = f"{base_id}_v{version}"
        return VersionIncrementDTO(base_id=base_id, new_id=new_id, version=version)

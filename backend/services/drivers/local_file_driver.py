"""Local File Driver Implementation."""

import logging
import os
import aiofiles
from pathlib import Path

from backend.services.file_driver import FileDriver

logger = logging.getLogger(__name__)


class LocalFileDriver(FileDriver):
    """Asynchronous Local File System Driver."""

    def __init__(self, base_path: str, base_url: str | None = None):
        """Initialize Local Driver.
        
        Args:
            base_path: Root directory for storage.
            base_url: Optional public base URL (e.g., http://localhost:8000/files).
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.base_url = base_url

    async def save(self, path: str, data: bytes | str) -> str:
        try:
            full_path = self.base_path / path
            
            # Ensure parent dir exists (Sync operation, but fast on local FS)
            full_path.parent.mkdir(parents=True, exist_ok=True)

            mode = "wb" if isinstance(data, bytes) else "w"
            encoding = None if isinstance(data, bytes) else "utf-8"

            async with aiofiles.open(full_path, mode, encoding=encoding) as f:
                await f.write(data)

            return str(full_path)
        except Exception as e:
            logger.error(f"Failed to save file to {path}: {e}")
            raise e

    async def read(self, path: str) -> bytes:
        try:
            full_path = self.base_path / path
            async with aiofiles.open(full_path, "rb") as f:
                return await f.read()
        except Exception as e:
            logger.error(f"Failed to read file from {path}: {e}")
            raise e

    async def delete(self, path: str) -> bool:
        full_path = self.base_path / path
        if full_path.exists():
            try:
                # brave attempt to use aiofiles.os if available, else os.remove
                # standard os.remove is sync but fast.
                os.remove(full_path)
                return True
            except Exception as e:
                logger.error(f"Failed to delete file {path}: {e}")
                return False
        return False

    async def exists(self, path: str) -> bool:
        full_path = self.base_path / path
        return full_path.exists()

    async def get_url(self, path: str) -> str | None:
        if self.base_url:
            # Simple concatenation, assumes standard web server serving base_path
            return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        return None

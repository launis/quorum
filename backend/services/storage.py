from abc import ABC, abstractmethod
from typing import Union, Optional
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class AbstractStorage(ABC):
    """
    Abstract base class for storage backends.
    """
    
    @abstractmethod
    def save(self, path: str, data: Union[bytes, str]) -> str:
        """
        Saves data to the specified path.
        Returns the saved location (compilable URI or path).
        """
        pass

    @abstractmethod
    def read(self, path: str) -> bytes:
        """
        Reads data from the specified path.
        """
        pass

    @abstractmethod
    def exists(self, path: str) -> bool:
        """
        Checks if the path exists.
        """
        pass

class LocalFileStorage(AbstractStorage):
    """
    Local file system implementation of AbstractStorage.
    """
    def __init__(self, base_path: str = "backend/files/executions"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save(self, path: str, data: Union[bytes, str]) -> str:
        """
        Saves file locally. 'path' is treated as relative to base_path.
        """
        try:
            full_path = self.base_path / path
            
            # Ensure parent dir exists
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            mode = "wb" if isinstance(data, bytes) else "w"
            encoding = None if isinstance(data, bytes) else "utf-8"
            
            with open(full_path, mode, encoding=encoding) as f:
                f.write(data)
                
            return str(full_path)
        except Exception as e:
            logger.error(f"Failed to save file to {path}: {e}")
            raise e

    def read(self, path: str) -> bytes:
        try:
            full_path = self.base_path / path
            with open(full_path, "rb") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read file from {path}: {e}")
            raise e

    def exists(self, path: str) -> bool:
        full_path = self.base_path / path
        return full_path.exists()

class NoOpStorage(AbstractStorage):
    """
    Storage implementation that does nothing (for when storage is disabled).
    """
    def save(self, path: str, data: Union[bytes, str]) -> str:
        return f"NOT_SAVED (NoOp): {path}"

    def read(self, path: str) -> bytes:
        raise FileNotFoundError(f"NoOpStorage does not store files: {path}")

    def exists(self, path: str) -> bool:
        return False

def get_storage_client() -> AbstractStorage:
    """
    Factory to get the configured storage client.
    """
    from backend.config import STORAGE_BACKEND
    
    if STORAGE_BACKEND == "NONE":
        return NoOpStorage()
    elif STORAGE_BACKEND == "LOCAL":
        return LocalFileStorage()
    # Future expansion:
    # elif STORAGE_BACKEND == "FIRESTORE":
    #    return FirestoreStorage()
    else:
        logger.warning(f"Unknown STORAGE_BACKEND '{STORAGE_BACKEND}'. Defaulting to LOCAL.")
        return LocalFileStorage()

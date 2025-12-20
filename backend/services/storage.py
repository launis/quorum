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


# --- Firebase Implementation ---

class FirebaseStorage(AbstractStorage):
    """
    Firebase Storage implementation of AbstractStorage.
    Uses firebase-admin SDK.
    """
    def __init__(self, bucket_name: Optional[str] = None):
        import firebase_admin
        from firebase_admin import storage
        
        # Ensure app is initialized (usually done in database/wrapper.py or main.py)
        # We check just in case
        if not firebase_admin._apps:
             from firebase_admin import credentials
             cred = credentials.ApplicationDefault()
             firebase_admin.initialize_app(cred)
             
        self.bucket = storage.bucket(name=bucket_name)

    def save(self, path: str, data: Union[bytes, str]) -> str:
        """
        Saves file to Firebase Storage bucket.
        """
        try:
            blob = self.bucket.blob(path)
            
            if isinstance(data, str):
                blob.upload_from_string(data, content_type="text/plain")
            else:
                blob.upload_from_string(data, content_type="application/octet-stream")
                
            # Return a GCS path or Signed URL? 
            # For strict backend usage, path is enough.
            # If front-end needs access, we might need signed URL or public URL.
            # Keeping it simple: return internal reference path
            return f"gs://{self.bucket.name}/{path}"
            
        except Exception as e:
            logger.error(f"Failed to save file to Firebase {path}: {e}")
            raise e

    def read(self, path: str) -> bytes:
        try:
            blob = self.bucket.blob(path)
            return blob.download_as_bytes()
        except Exception as e:
            logger.error(f"Failed to read file from Firebase {path}: {e}")
            raise e

    def exists(self, path: str) -> bool:
        blob = self.bucket.blob(path)
        return blob.exists()

def get_storage_client() -> AbstractStorage:
    """
    Factory to get the configured storage client.
    """
    from backend.settings import get_settings
    settings = get_settings()
    
    # Simple Logic: LOCAL vs FIREBASE
    # User requested: Local in Dev, Firebase in Prod.
    # Controlled by storage_backend setting.
    
    if settings.storage_backend == "NONE":
        return NoOpStorage()
        
    elif settings.storage_backend == "FIREBASE":
        try:
            return FirebaseStorage()
        except Exception as e:
            logger.error(f"Failed to initialize FirebaseStorage: {e}. Fallback to LOCAL.")
            return LocalFileStorage()
            
    else:
        # Default to LOCAL (Dev)
        return LocalFileStorage()

"""Storage Service abstraction for local and cloud backends."""
import logging
from abc import ABC, abstractmethod
from pathlib import Path

logger = logging.getLogger(__name__)


class AbstractStorage(ABC):
    """Abstract base class defining the contract for file storage backends."""

    @abstractmethod
    def save(self, path: str, data: bytes | str) -> str:
        """Saves data (bytes or string) to the specified path.

        Args:
            path (str): Relative path/key for the file.
            data (Union[bytes, str]): Content to save.

        Returns:
            str: The resolved path or URI of the saved file.

        """
        pass

    @abstractmethod
    def read(self, path: str) -> bytes:
        """Reads raw bytes from the specified path.

        Args:
            path (str): Relative path/key.

        Returns:
            bytes: The file content.

        """
        pass

    @abstractmethod
    def exists(self, path: str) -> bool:
        """Checks existence of the file.

        Args:
            path (str): Relative path/key.

        Returns:
            bool: True if exists, else False.

        """
        pass


class LocalFileStorage(AbstractStorage):
    """Local file system implementation of AbstractStorage.

    Stores files in a local directory (e.g., 'backend/files/executions').
    """

    def __init__(self, base_path: str = "backend/files/executions"):
        """Initializes local storage.

        Args:
            base_path (str): Root directory for file storage.

        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save(self, path: str, data: bytes | str) -> str:
        """Saves file locally. 'path' is treated as relative to base_path.

        Args:
            path (str): Relative path.
            data (Union[bytes, str]): Content.

        Returns:
            str: Absolute path to the saved file.

        Raises:
            IOError: If write fails.

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
            raise e from e

    def read(self, path: str) -> bytes:
        """Reads file from local system.

        Args:
            path (str): Relative path.

        Returns:
            bytes: Content.

        """
        try:
            full_path = self.base_path / path
            with open(full_path, "rb") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read file from {path}: {e}")
            raise e from e

    def exists(self, path: str) -> bool:
        """Checks if local file exists.

        Args:
            path (str): Relative path.

        Returns:
            bool: Existence status.

        """
        full_path = self.base_path / path
        return full_path.exists()


class NoOpStorage(AbstractStorage):
    """Storage implementation that does nothing (for when storage is disabled)."""

    def save(self, path: str, data: bytes | str) -> str:
        """Mock save."""
        return f"NOT_SAVED (NoOp): {path}"

    def read(self, path: str) -> bytes:
        """Mock read."""
        raise FileNotFoundError(f"NoOpStorage does not store files: {path}")

    def exists(self, path: str) -> bool:
        """Mock exists."""
        return False


# --- Firebase Implementation ---


class FirebaseStorage(AbstractStorage):
    """Firebase Storage implementation of AbstractStorage.

    Uses firebase-admin SDK.
    """

    def __init__(self, bucket_name: str | None = None):
        """Initializes Firebase Storage client.

        Args:
            bucket_name (Optional[str]): Target bucket name.

        """
        import firebase_admin
        from firebase_admin import storage

        # Ensure app is initialized (usually done in database/wrapper.py or main.py)
        # We check just in case
        if not firebase_admin._apps:
            from firebase_admin import credentials

            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred)

        self.bucket = storage.bucket(name=bucket_name)

    def save(self, path: str, data: bytes | str) -> str:
        """Saves file to Firebase Storage bucket.

        Args:
            path (str): Blob path.
            data (Union[bytes, str]): Content.

        Returns:
            str: gs:// URI of the saved blob.

        """
        try:
            blob = self.bucket.blob(path)

            if isinstance(data, str):
                blob.upload_from_string(data, content_type="text/plain")
            else:
                blob.upload_from_string(data, content_type="application/octet-stream")

            return f"gs://{self.bucket.name}/{path}"

        except Exception as e:
            msg = f"Failed to save file to Firebase {path}: {e}"
            logger.error(msg)
            # Using logger.critical/warning instead of print for better visibility in logs
            logger.critical(f"!!! FIREBASE STORAGE ERROR: {msg}")
            logger.critical("!!! HINT: Did you enable 'Storage' in the Firebase Console?")
            raise e from e

    def read(self, path: str) -> bytes:
        """Reads file from Firebase bucket.

        Args:
            path (str): Blob path.

        Returns:
            bytes: Content.

        """
        try:
            blob = self.bucket.blob(path)
            return blob.download_as_bytes()
        except Exception as e:
            logger.error(f"Failed to read file from Firebase {path}: {e}")
            raise e

    def exists(self, path: str) -> bool:
        """Checks if blob exists in Firebase.

        Args:
            path (str): Blob path.

        Returns:
            bool: Status.

        """
        blob = self.bucket.blob(path)
        return blob.exists()


def get_storage_client() -> AbstractStorage:
    """Factory function to return the configured storage client.

    Defaults to LocalFileStorage in development.
    """
    from backend.settings import get_settings

    settings = get_settings()

    if settings.environment == "production" and settings.storage_bucket_name:
        return FirebaseStorage(bucket_name=settings.storage_bucket_name)
    else:
        return LocalFileStorage()

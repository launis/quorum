"""Database wrapper implementations."""

from __future__ import annotations

import importlib.util
import json
import logging
import os
import threading
import time
import types
import uuid
from abc import ABC, abstractmethod
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from tinydb import Storage, TinyDB
from tinydb.table import Table

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.settings import get_settings

# Logger
logger = logging.getLogger(__name__)

# --- Firestore Imports (Conditional) ---
if importlib.util.find_spec("firebase_admin") is not None:
    import firebase_admin
    from firebase_admin import credentials, firestore

    FIRESTORE_AVAILABLE = True
else:
    FIRESTORE_AVAILABLE = False
    logger.warning("firebase_admin not installed or import failed. Firestore functionality will be unavailable.")


# --- Cross-Process and Cross-Thread locking for TinyDB ---
_thread_lock = threading.Lock()

HAS_MSVCRT = importlib.util.find_spec("msvcrt") is not None
if HAS_MSVCRT:
    import msvcrt

fcntl: types.ModuleType
if importlib.util.find_spec("fcntl") is not None:
    import fcntl

    HAS_FCNTL = True
else:
    fcntl = types.ModuleType("fcntl")
    HAS_FCNTL = False


MAX_REPLACE_RETRIES: int = 20
REPLACE_RETRY_DELAY_SEC: float = 0.05

__all__ = [
    "FIRESTORE_AVAILABLE",
    "MAX_REPLACE_RETRIES",
    "REPLACE_RETRY_DELAY_SEC",
    "AbstractDatabase",
    "AbstractTable",
    "AtomicJSONStorage",
    "FirestoreClient",
    "FirestoreTable",
    "TinyDBClient",
    "TinyDBTable",
    "db_lock",
    "get_db_client",
]


@contextmanager
def db_lock(db_path: str) -> Generator[None]:
    """Acquire cross-process and cross-thread lock for TinyDB file access.

    Args:
        db_path: Path to the database file to lock.

    Yields:
        None when the lock is successfully held.

    Raises:
        TimeoutError: If the database lock cannot be acquired within the configured timeout.
    """
    lock_file_path = db_path + ".lock"
    start_time = time.time()
    settings = get_settings()
    lock_timeout = settings.db_lock_timeout_seconds
    poll_interval = settings.db_lock_poll_interval_seconds
    stale_threshold = settings.db_lock_stale_threshold_seconds
    with _thread_lock:
        if HAS_MSVCRT:
            fd = os.open(lock_file_path, os.O_CREAT | os.O_RDWR)
            try:
                while True:
                    try:
                        os.lseek(fd, 0, os.SEEK_SET)
                        msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
                        break
                    except OSError as e:
                        if time.time() - start_time > lock_timeout:
                            raise TimeoutError(f"Database lock timeout on {lock_file_path}") from e
                        time.sleep(poll_interval)
                wait_time_ms = (time.time() - start_time) * 1000
                logger.debug("[TinyDB Lock] Acquired MSVCRT lock on %s in %.1f ms", lock_file_path, wait_time_ms)
                yield
            finally:
                try:
                    os.lseek(fd, 0, os.SEEK_SET)
                    msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
                except OSError:
                    pass
                os.close(fd)
        elif HAS_FCNTL:
            f = open(lock_file_path, "w")
            try:
                while True:
                    try:
                        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
                        break
                    except BlockingIOError as e:
                        if time.time() - start_time > lock_timeout:
                            raise TimeoutError(f"Database lock timeout on {lock_file_path}") from e
                        time.sleep(poll_interval)
                wait_time_ms = (time.time() - start_time) * 1000
                logger.debug("[TinyDB Lock] Acquired FCNTL lock on %s in %.1f ms", lock_file_path, wait_time_ms)
                yield
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
                f.close()
        else:
            lock_dir = db_path + ".lock_dir"
            acquired = False
            while not acquired:
                try:
                    os.makedirs(lock_dir)
                    acquired = True
                except FileExistsError as e:
                    try:
                        mtime = os.path.getmtime(lock_dir)
                        if time.time() - mtime > stale_threshold:
                            os.rmdir(lock_dir)
                            continue
                    except OSError as os_err:
                        if time.time() - start_time > lock_timeout:
                            raise TimeoutError(f"Database lock timeout on {lock_dir}: {os_err}") from e
                    if time.time() - start_time > lock_timeout:
                        raise TimeoutError(f"Database lock timeout on {lock_dir}") from e
                    time.sleep(poll_interval)
            try:
                wait_time_ms = (time.time() - start_time) * 1000
                logger.debug("[TinyDB Lock] Acquired directory lock on %s in %.1f ms", lock_dir, wait_time_ms)
                yield
            finally:
                try:
                    os.rmdir(lock_dir)
                except OSError:
                    pass


# --- Abstract Base Classes ---


class AbstractTable(ABC):
    """Abstract base class for database tables."""

    @abstractmethod
    def insert(self, document: dict[str, Any]) -> Any:
        """Insert a document.

        Args:
            document: Document data dictionary to insert.

        Returns:
            Identifier of inserted document.
        """
        pass

    @abstractmethod
    def all(self) -> list[dict[str, Any]]:
        """Retrieve all documents.

        Returns:
            List of all documents in the table.
        """
        pass

    @abstractmethod
    def search(self, query: Any) -> list[dict[str, Any]]:
        """Search documents matching a query.

        Args:
            query: Query predicate.

        Returns:
            List of matching documents.
        """
        pass

    @abstractmethod
    def get(self, query: Any) -> dict[str, Any] | None:
        """Get a single document matching a query.

        Args:
            query: Query predicate.

        Returns:
            Matching document dictionary if found, otherwise None.
        """
        pass

    @abstractmethod
    def update(self, fields: dict[str, Any], query: Any = None, doc_ids: list[int] | None = None) -> list[int]:
        """Update documents.

        Args:
            fields: Dictionary of fields to update.
            query: Optional query predicate.
            doc_ids: Optional document ID list.

        Returns:
            List of affected document IDs.
        """
        pass

    @abstractmethod
    def upsert(self, document: dict[str, Any], query: Any) -> list[int]:
        """Upsert a document.

        Args:
            document: Document data dictionary.
            query: Query predicate.

        Returns:
            List of affected document IDs.
        """
        pass

    @abstractmethod
    def remove(self, query: Any = None, doc_ids: list[int] | None = None) -> list[int]:
        """Remove documents.

        Args:
            query: Optional query predicate.
            doc_ids: Optional document ID list.

        Returns:
            List of affected document IDs.
        """
        pass

    @abstractmethod
    def truncate(self) -> None:
        """Truncate the table."""
        pass

    @abstractmethod
    def count(self, query: Any = None) -> int:
        """Count documents.

        Args:
            query: Optional query predicate.

        Returns:
            Count of documents matching query.
        """
        pass

    @abstractmethod
    def contains(self, query: Any) -> bool:
        """Check if document exists.

        Args:
            query: Query predicate.

        Returns:
            True if matching document exists, False otherwise.
        """
        pass


class AbstractDatabase(ABC):
    """Abstract base class for database clients."""

    @abstractmethod
    def table(self, name: str) -> AbstractTable:
        """Get a table by name.

        Args:
            name: Table name.

        Returns:
            AbstractTable instance.
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the database connection."""
        pass


# --- TinyDB Implementation ---


class AtomicJSONStorage(Storage):
    """Atomic JSON storage for TinyDB that writes to a temporary file and renames it atomically.

    Prevents partial write corruption on Windows NTFS by eliminating in-place truncation
    and retrying atomic replace operations when encountering transient file locks.
    """

    def __init__(self, path: str, encoding: str = "utf-8", create_dirs: bool = True, **kwargs: Any) -> None:
        """Initialize AtomicJSONStorage.

        Args:
            path: Target file path for the database.
            encoding: Text encoding for JSON file.
            create_dirs: Whether to create parent directories if missing.
            **kwargs: Extra serialization arguments forwarded to json.dump.
        """
        self._path = path
        self._encoding = encoding
        self.kwargs = kwargs
        if create_dirs:
            parent_dir = Path(path).parent
            parent_dir.mkdir(parents=True, exist_ok=True)

    def read(self) -> dict[str, dict[str, Any]] | None:
        """Read the current state of the database.

        Returns:
            Parsed database dictionary, or None if the file is missing or empty.
        """
        p = Path(self._path)
        if not p.is_file() or p.stat().st_size == 0:
            return None
        with open(self._path, encoding=self._encoding) as f:
            data: dict[str, dict[str, Any]] = json.load(f)
            return data

    def write(self, data: dict[str, dict[str, Any]]) -> None:
        """Write current database state atomically via temporary file replacement.

        Args:
            data: Current state of the database.

        Raises:
            PermissionError: If atomic file replacement fails after exhausting retries.
        """
        temp_path = f"{self._path}.{uuid.uuid4().hex[:8]}.tmp"
        try:
            with open(temp_path, "w", encoding=self._encoding) as f:
                json.dump(data, f, ensure_ascii=False, **self.kwargs)
                f.flush()
                os.fsync(f.fileno())

            for attempt in range(MAX_REPLACE_RETRIES):
                try:
                    os.replace(temp_path, self._path)
                    break
                except PermissionError as e:
                    if attempt == MAX_REPLACE_RETRIES - 1:
                        logger.error(
                            "[AtomicJSONStorage] %s: Failed to atomically replace %s after %d attempts: %s",
                            ErrorCodes.STORAGE_ACCESS_FAILED.name,
                            self._path,
                            MAX_REPLACE_RETRIES,
                            e,
                            exc_info=True,
                        )
                        raise
                    logger.warning(
                        "[AtomicJSONStorage] Windows NTFS lock on %s (attempt %d/%d). Retrying in %.2fs...",
                        self._path,
                        attempt + 1,
                        MAX_REPLACE_RETRIES,
                        REPLACE_RETRY_DELAY_SEC,
                    )
                    time.sleep(REPLACE_RETRY_DELAY_SEC)
        finally:
            temp_p = Path(temp_path)
            if temp_p.is_file():
                try:
                    temp_p.unlink()
                except OSError:
                    pass

    def close(self) -> None:
        """Close storage handles (no-op for atomic file storage)."""
        pass


class TinyDBTable(AbstractTable):
    """TinyDB implementation of AbstractTable."""

    def __init__(self, db_path: str, table_name: str) -> None:
        """Initialize TinyDB table.

        Args:
            db_path: Path to TinyDB JSON file.
            table_name: Name of table inside database.
        """
        self._path = db_path
        self._name = table_name

    @contextmanager
    def _open_db(self) -> Generator[TinyDB]:
        """Open TinyDB safely under cross-process lock with AtomicJSONStorage."""
        with db_lock(self._path):
            with TinyDB(self._path, encoding="utf-8", storage=AtomicJSONStorage) as db:
                yield db

    def _get_table(self, db: TinyDB) -> Table:
        return db.table(self._name)

    def insert(self, document: dict[str, Any]) -> int:
        """Insert document into table.

        Args:
            document: Document data dictionary.

        Returns:
            Inserted document internal ID.
        """
        db_start = time.time()
        with self._open_db() as db:
            res = self._get_table(db).insert(document)
        db_time = (time.time() - db_start) * 1000
        logger.debug("[TinyDBTable:%s] Insert completed in %.1f ms", self._name, db_time)
        return res

    def all(self) -> list[dict[str, Any]]:
        """Retrieve all documents.

        Returns:
            List of all documents in the table.
        """
        db_start = time.time()
        with self._open_db() as db:
            res = self._get_table(db).all()
        db_time = (time.time() - db_start) * 1000
        logger.debug("[TinyDBTable:%s] Retrieve all completed in %.1f ms", self._name, db_time)
        return list(res)

    def search(self, query: Any) -> list[dict[str, Any]]:
        """Search documents matching query.

        Args:
            query: Query predicate.

        Returns:
            List of matching documents.
        """
        db_start = time.time()
        with self._open_db() as db:
            res = self._get_table(db).search(query)
        db_time = (time.time() - db_start) * 1000
        logger.debug("[TinyDBTable:%s] Search completed in %.1f ms", self._name, db_time)
        return list(res)

    def get(self, query: Any) -> dict[str, Any] | None:
        """Get single document matching query.

        Args:
            query: Query predicate.

        Returns:
            Matching document or None.
        """
        db_start = time.time()
        with self._open_db() as db:
            res = self._get_table(db).get(query)
        db_time = (time.time() - db_start) * 1000
        logger.debug("[TinyDBTable:%s] Get completed in %.1f ms", self._name, db_time)
        if isinstance(res, list):
            if res:
                res = res[0]
            else:
                res = None
        return res

    def update(self, fields: dict[str, Any], query: Any = None, doc_ids: list[int] | None = None) -> list[int]:
        """Update documents matching query.

        Args:
            fields: Fields to update.
            query: Optional query predicate.
            doc_ids: Optional document IDs.

        Returns:
            List of updated document IDs.
        """
        db_start = time.time()
        with self._open_db() as db:
            res = self._get_table(db).update(fields, cond=query, doc_ids=doc_ids)
        db_time = (time.time() - db_start) * 1000
        logger.debug("[TinyDBTable:%s] Update completed in %.1f ms", self._name, db_time)
        return res

    def upsert(self, document: dict[str, Any], query: Any) -> list[int]:
        """Upsert document.

        Args:
            document: Document data.
            query: Query predicate.

        Returns:
            List of upserted document IDs.
        """
        db_start = time.time()
        with self._open_db() as db:
            res = self._get_table(db).upsert(document, query)
        db_time = (time.time() - db_start) * 1000
        logger.debug("[TinyDBTable:%s] Upsert completed in %.1f ms", self._name, db_time)
        return res

    def remove(self, query: Any = None, doc_ids: list[int] | None = None) -> list[int]:
        """Remove documents.

        Args:
            query: Optional query predicate.
            doc_ids: Optional document IDs.

        Returns:
            List of removed document IDs.
        """
        db_start = time.time()
        with self._open_db() as db:
            res = self._get_table(db).remove(query, doc_ids=doc_ids)
        db_time = (time.time() - db_start) * 1000
        logger.debug("[TinyDBTable:%s] Remove completed in %.1f ms", self._name, db_time)
        return res

    def truncate(self) -> None:
        """Truncate table."""
        db_start = time.time()
        with self._open_db() as db:
            self._get_table(db).truncate()
        db_time = (time.time() - db_start) * 1000
        logger.debug("[TinyDBTable:%s] Truncate completed in %.1f ms", self._name, db_time)

    def count(self, query: Any = None) -> int:
        """Count documents matching query.

        Args:
            query: Optional query predicate.

        Returns:
            Document count.
        """
        db_start = time.time()
        with self._open_db() as db:
            if query:
                res = self._get_table(db).count(query)
            else:
                res = len(self._get_table(db))
        db_time = (time.time() - db_start) * 1000
        logger.debug("[TinyDBTable:%s] Count completed in %.1f ms", self._name, db_time)
        return res

    def contains(self, query: Any) -> bool:
        """Check if document exists.

        Args:
            query: Query predicate.

        Returns:
            True if matching document exists, False otherwise.
        """
        db_start = time.time()
        with self._open_db() as db:
            res = self._get_table(db).contains(query)
        db_time = (time.time() - db_start) * 1000
        logger.debug("[TinyDBTable:%s] Contains completed in %.1f ms", self._name, db_time)
        return res


class TinyDBClient(AbstractDatabase):
    """TinyDB implementation of AbstractDatabase."""

    def __init__(self, path: str) -> None:
        """Initialize TinyDB Client.

        Args:
            path: Target database file path.
        """
        parent_dir = Path(path).parent
        parent_dir.mkdir(parents=True, exist_ok=True)
        self.path = path
        # Verify creation/access under lock but don't hold connection
        with db_lock(self.path):
            with TinyDB(path, encoding="utf-8", storage=AtomicJSONStorage) as _:
                pass

    def table(self, name: str) -> AbstractTable:
        """Get table by name.

        Args:
            name: Name of table.

        Returns:
            TinyDBTable instance.
        """
        return TinyDBTable(self.path, name)

    def close(self) -> None:
        """Close client."""
        pass


# --- Firestore Implementation ---


class FirestoreTable(AbstractTable):
    """Firestore implementation of AbstractTable."""

    def __init__(self, collection_ref: Any) -> None:
        """Initialize Firestore Table.

        Args:
            collection_ref: Firestore CollectionReference instance.
        """
        self._collection = collection_ref

    def insert(self, document: dict[str, Any]) -> Any:
        """Insert document into Firestore collection.

        Args:
            document: Document data dictionary.

        Returns:
            Created document ID.
        """
        _, doc_ref = self._collection.add(document)
        return doc_ref.id

    def all(self) -> list[dict[str, Any]]:
        """Retrieve all documents.

        Returns:
            List of all document data dictionaries.
        """
        docs = self._collection.stream()
        return [doc.to_dict() for doc in docs]

    def search(self, query: Any) -> list[dict[str, Any]]:
        """Search documents matching query.

        Args:
            query: Query predicate function.

        Returns:
            List of matching document dictionaries.
        """
        docs = self._collection.stream()
        results = []
        for doc in docs:
            data = doc.to_dict()
            if query(data):
                results.append(data)
        return results

    def get(self, query: Any) -> dict[str, Any] | None:
        """Get single document matching query.

        Args:
            query: Query predicate function.

        Returns:
            First matching document dictionary or None.
        """
        docs = self._collection.stream()
        for doc in docs:
            data = doc.to_dict()
            if query(data):
                res: dict[str, Any] = data
                return res
        return None

    def update(self, fields: dict[str, Any], query: Any = None, doc_ids: list[int] | None = None) -> list[int]:
        """Update documents matching query.

        Args:
            fields: Fields dictionary to update.
            query: Optional query predicate function.
            doc_ids: Ignored by Firestore.

        Returns:
            List of count indicators for updated documents.
        """
        docs = self._collection.stream()
        updated_count = 0
        for doc in docs:
            data = doc.to_dict()
            if query and query(data):
                doc.reference.update(fields)
                updated_count += 1
        return [1] * updated_count

    def upsert(self, document: dict[str, Any], query: Any) -> list[int]:
        """Upsert document.

        Args:
            document: Document data dictionary.
            query: Query predicate function.

        Returns:
            List indicating affected document count.
        """
        docs = self._collection.stream()
        matches = []
        for doc in docs:
            if query(doc.to_dict()):
                matches.append(doc)

        if matches:
            for doc in matches:
                doc.reference.update(document)
            return [1] * len(matches)
        else:
            if "id" in document and document["id"]:
                self._collection.document(str(document["id"])).set(document)
            else:
                self._collection.add(document)
            return [1]

    def remove(self, query: Any = None, doc_ids: list[int] | None = None) -> list[int]:
        """Remove documents matching query.

        Args:
            query: Query predicate function.
            doc_ids: Ignored by Firestore.

        Returns:
            List indicating removed document count.

        Raises:
            AppException: If document deletion fails (ErrorCodes.STORAGE_ACCESS_FAILED).
        """
        docs = self._collection.stream()
        removed_count = 0
        to_delete = []

        for doc in docs:
            if query and query(doc.to_dict()):
                to_delete.append(doc.reference)

        for ref in to_delete:
            try:
                ref.delete()
                removed_count += 1
            except Exception as e:
                logger.error(
                    "[FirestoreTable] %s: Failed to delete doc %s: %s",
                    ErrorCodes.STORAGE_ACCESS_FAILED.name,
                    ref.id,
                    e,
                    exc_info=True,
                )
                raise AppException(
                    message=f"Failed to delete document {ref.id}: {e}",
                    status_code=500,
                    details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED},
                ) from e

        return [1] * removed_count

    def truncate(self) -> None:
        """Truncate the table by batch deleting documents."""
        batch_size = 500
        docs = self._collection.limit(batch_size).stream()
        deleted = 0

        for doc in docs:
            doc.reference.delete()
            deleted += 1

        if deleted >= batch_size:
            self.truncate()

    def count(self, query: Any = None) -> int:
        """Count documents matching query.

        Args:
            query: Optional query predicate function.

        Returns:
            Document count.

        Raises:
            AppException: If aggregate count query fails (ErrorCodes.STORAGE_ACCESS_FAILED).
        """
        if query:
            docs = self._collection.stream()
            c = 0
            for doc in docs:
                if query(doc.to_dict()):
                    c += 1
            return c
        else:
            try:
                aggregate_query = self._collection.count()
                snapshots = aggregate_query.get()
                return int(snapshots[0][0].value)
            except Exception as e:
                logger.error(
                    "[FirestoreTable] %s: Firestore aggregate count failed: %s",
                    ErrorCodes.STORAGE_ACCESS_FAILED.name,
                    e,
                    exc_info=True,
                )
                raise AppException(
                    message=f"Firestore count operation failed: {e}",
                    status_code=500,
                    details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED},
                ) from e

    def contains(self, query: Any) -> bool:
        """Check if document exists.

        Args:
            query: Query predicate function.

        Returns:
            True if matching document exists, False otherwise.
        """
        matches = self.search(query)
        return len(matches) > 0

    def close(self) -> None:
        """Close the table connection (no-op for Firestore)."""
        pass


class FirestoreClient(AbstractDatabase):
    """Firestore implementation of AbstractDatabase."""

    def __init__(self) -> None:
        """Initialize Firestore Client and verify connectivity.

        Raises:
            AppException: If Firestore connection verification fails (ErrorCodes.STORAGE_ACCESS_FAILED).
        """
        settings = get_settings()

        if not firebase_admin._apps:
            root_dir = Path(settings.base_dir).parent
            sa_path = root_dir / "service-account.json"

            if not sa_path.is_file():
                logger.error("Service Account not found at %s", sa_path)

            cred = credentials.Certificate(str(sa_path))
            firebase_admin.initialize_app(cred)

        self.db = firestore.client()

        try:
            logger.info("[Firestore] Verifying connection...")
            list(self.db.collection("connectivity_test").limit(1).stream())
            logger.info("[Firestore] Connection VERIFIED successfully.")
        except Exception as e:
            logger.error(
                "[FirestoreClient] %s: Connection ping FAILED: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                e,
                exc_info=True,
            )
            raise AppException(
                message=f"Firestore connectivity test failed. Error: {e}",
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED},
            ) from e

    def table(self, name: str) -> AbstractTable:
        """Get table by name.

        Args:
            name: Table name.

        Returns:
            FirestoreTable instance.
        """
        return FirestoreTable(self.db.collection(name))

    def close(self) -> None:
        """Close client."""
        pass


def get_db_client() -> AbstractDatabase:
    """Factory to get the appropriate database client based on configuration.

    Returns:
        Configured AbstractDatabase client instance.

    Raises:
        ImportError: If STORAGE_BACKEND is FIRESTORE but firebase_admin is missing.
        ValueError: If active_backend is unknown or unsupported.
    """
    settings = get_settings()

    backend = settings.active_backend

    if backend == "FIRESTORE":
        if not FIRESTORE_AVAILABLE:
            raise ImportError("CRITICAL: STORAGE_BACKEND=FIRESTORE but firebase_admin is not installed.")
        return FirestoreClient()
    elif backend == "LOCAL":
        return TinyDBClient(settings.prod_db_path)
    else:
        raise ValueError(f"CRITICAL: Unknown/Unsupported BACKEND '{backend}'.")

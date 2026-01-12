"""Database wrapper implementations."""

import logging
import os
from abc import ABC, abstractmethod
from typing import Any

from tinydb import TinyDB

# from backend.config import USE_MOCK_DB, DB_PATH # Removed


# Logger
logger = logging.getLogger(__name__)

# --- Firestore Imports (Conditional) ---
try:
    import firebase_admin
    from firebase_admin import credentials, firestore

    FIRESTORE_AVAILABLE = True
except ImportError:
    FIRESTORE_AVAILABLE = False
    logger.warning("firebase_admin not installed or import failed. Firestore functionality will be unavailable.")

# --- Abstract Base Classes ---


class AbstractTable(ABC):
    """Abstract base class for database tables."""

    @abstractmethod
    def insert(self, document: dict[str, Any]) -> Any:
        """Insert a document."""
        pass

    @abstractmethod
    def all(self) -> list[dict[str, Any]]:
        """Retrieve all documents."""
        pass

    @abstractmethod
    def search(self, query: Any) -> list[dict[str, Any]]:
        """Search documents matching a query."""
        pass

    @abstractmethod
    def get(self, query: Any) -> dict[str, Any] | None:
        """Get a single document matching a query."""
        pass

    @abstractmethod
    def update(self, fields: dict[str, Any], query: Any = None, doc_ids: list[int] | None = None) -> list[int]:
        """Update documents."""
        pass

    @abstractmethod
    def upsert(self, document: dict[str, Any], query: Any) -> list[int]:
        """Upsert a document."""
        pass

    @abstractmethod
    def remove(self, query: Any) -> list[int]:
        """Remove documents."""
        pass


class AbstractDatabase(ABC):
    """Abstract base class for database clients."""

    @abstractmethod
    def table(self, name: str) -> AbstractTable:
        """Get a table by name."""
        pass

    @abstractmethod
    def close(self):
        """Close the database connection."""
        pass


# --- TinyDB Implementation ---


class TinyDBTable(AbstractTable):
    """TinyDB implementation of AbstractTable."""

    def __init__(self, db_path: str, table_name: str):
        """Initialize TinyDB table."""
        self._path = db_path
        self._name = table_name

    def _get_table(self, db):
        return db.table(self._name)

    def insert(self, document: dict[str, Any]) -> int:
        """Insert document."""
        with TinyDB(self._path, encoding="utf-8") as db:
            return self._get_table(db).insert(document)

    def all(self) -> list[dict[str, Any]]:
        """Retrieve all documents."""
        with TinyDB(self._path, encoding="utf-8") as db:
            return self._get_table(db).all()

    def search(self, query: Any) -> list[dict[str, Any]]:
        """Search documents."""
        with TinyDB(self._path, encoding="utf-8") as db:
            return self._get_table(db).search(query)

    def get(self, query: Any) -> dict[str, Any] | None:
        """Get document."""
        with TinyDB(self._path, encoding="utf-8") as db:
            return self._get_table(db).get(query)

    def update(self, fields: dict[str, Any], query: Any = None, doc_ids: list[int] | None = None) -> list[int]:
        """Update documents."""
        with TinyDB(self._path, encoding="utf-8") as db:
            return self._get_table(db).update(fields, cond=query, doc_ids=doc_ids)

    def upsert(self, document: dict[str, Any], query: Any) -> list[int]:
        """Upsert document."""
        with TinyDB(self._path, encoding="utf-8") as db:
            return self._get_table(db).upsert(document, query)

    def remove(self, query: Any) -> list[int]:
        """Remove documents."""
        with TinyDB(self._path, encoding="utf-8") as db:
            return self._get_table(db).remove(query)


class TinyDBClient(AbstractDatabase):
    """TinyDB implementation of AbstractDatabase."""

    def __init__(self, path: str):
        """Initialize TinyDB Client."""
        import os

        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.path = path
        # Verify creation/access but don't hold connection
        with TinyDB(path, encoding="utf-8") as _:
            pass

    def table(self, name: str) -> AbstractTable:
        """Get table."""
        return TinyDBTable(self.path, name)

    def close(self):
        """Close client."""
        pass


# --- Firestore Implementation ---


class FirestoreTable(AbstractTable):
    """Firestore implementation of AbstractTable."""

    def __init__(self, collection_ref):
        """Initialize Firestore Table."""
        self._collection = collection_ref

    def insert(self, document: dict[str, Any]) -> Any:
        """Insert document."""
        _, doc_ref = self._collection.add(document)
        return doc_ref.id

    def all(self) -> list[dict[str, Any]]:
        """Retrieve all documents."""
        docs = self._collection.stream()
        return [doc.to_dict() for doc in docs]

    def search(self, query: Any) -> list[dict[str, Any]]:
        """Search documents."""
        # Fetch all and filter in memory using TinyDB query evaluation
        # This is inefficient for large datasets but acceptable for configuration tables.
        docs = self._collection.stream()
        results = []
        for doc in docs:
            data = doc.to_dict()
            if query(data):
                results.append(data)
        return results

    def get(self, query: Any) -> dict[str, Any] | None:
        """Get document."""
        # Return the first match
        docs = self._collection.stream()
        for doc in docs:
            data = doc.to_dict()
            if query(data):
                return data
        return None

    def update(self, fields: dict[str, Any], query: Any = None, doc_ids: list[int] | None = None) -> list[int]:
        """Update documents."""
        # Firestore implementation ignores doc_ids (int) as it uses string IDs.
        # Ideally, repository should use Query for compatibility.
        docs = self._collection.stream()
        updated_count = 0
        for doc in docs:
            data = doc.to_dict()
            # If query is None and we intend to update all or singleton?
            # Existing implementation required query.
            if query and query(data):
                doc.reference.update(fields)
                updated_count += 1
        return [1] * updated_count

    def upsert(self, document: dict[str, Any], query: Any) -> list[int]:
        """Upsert document."""
        docs = self._collection.stream()
        matches = []
        for doc in docs:
            if query(doc.to_dict()):
                matches.append(doc)

            return [1] * len(matches)

        else:
            # Insert new
            doc_id = document.get("id")
            if doc_id:
                self._collection.document(str(doc_id)).set(document)
            else:
                self._collection.add(document)
            return [1]

    def remove(self, query: Any) -> list[int]:
        """Remove documents."""
        docs = self._collection.stream()
        removed_count = 0
        to_delete = []

        # 1. Identify docs (Scan)
        for doc in docs:
            if query(doc.to_dict()):
                to_delete.append(doc.reference)

        # 2. Delete (Batch/Serial)
        # Note: We do serial delete here to match interface, but batching would be better for performance.
        # For safety/simplicity in this wrapper, we keep it serial but decoupled from stream.
        for ref in to_delete:
            try:
                ref.delete()
                removed_count += 1
            except Exception as e:
                logger.error(f"[FirestoreTable] Failed to delete doc {ref.id}: {e}")

        return [1] * removed_count

    def close(self):
        """Close the table connection (no-op for Firestore)."""
        pass


class FirestoreClient(AbstractDatabase):
    """Firestore implementation of AbstractDatabase."""

    def __init__(self):
        """Initialize Firestore Client and verify connection."""
        # Lazy import settings to avoid circular deps if any
        from backend.settings import get_settings

        settings = get_settings()

        if not firebase_admin._apps:
            # Locate service-account.json in project root
            root_dir = os.path.dirname(settings.base_dir)
            sa_path = os.path.join(root_dir, "service-account.json")

            if not os.path.exists(sa_path):
                # Fallback check or error
                logger.error(f"Service Account not found at {sa_path}")

            cred = credentials.Certificate(sa_path)
            firebase_admin.initialize_app(cred)

        self.db = firestore.client()

        # ACTIVE PING TEST (Strict Zero-Fallback)
        try:
            # Attempt to access a collection (lightweight validation)
            # Note: list_collections is a generator, so we just get the first one or simply call it.
            # Better: try to get a non-existent doc to prove connectivity without permissions error
            # if list is restricted
            # But list_collections is standard matching `wrapper.py` previous intent.
            # Actually, just next(self.db.collections(), None) is enough to verify auth.
            logger.info("[Firestore] Verifying connection...")
            # self.db.collection('system_settings').limit(1).get() # Might fail if empty? No, returns empty list.
            # Simpler:
            list(self.db.collection("connectivity_test").limit(1).stream())
            logger.info("[Firestore] Connection VERIFIED successfully.")
        except Exception as e:
            logger.critical(f"[Firestore] Connection ping FAILED: {e}")
            raise RuntimeError(f"Firestore connectivity test failed. Error: {e}") from e

    def table(self, name: str) -> AbstractTable:
        """Get table."""
        return FirestoreTable(self.db.collection(name))

    def close(self):
        """Close client."""
        pass


# --- Factory Function ---


def get_db_client() -> AbstractDatabase:
    """Factory to get the appropriate database client based on configuration."""
    from backend.settings import get_settings

    settings = get_settings()

    # 1. Mock Mode (Priority)
    if settings.use_mock_db:
        return TinyDBClient(settings.mock_db_path)

    # 2. Production Modes
    backend = settings.storage_backend.strip().upper()

    match backend:
        case "FIRESTORE":
            if not FIRESTORE_AVAILABLE:
                raise RuntimeError(
                    "CRITICAL: Firestore requested (STORAGE_BACKEND=FIRESTORE) "
                    "but 'firebase_admin' or 'google-cloud-firestore' is not installed."
                )

            try:
                return FirestoreClient()
            except Exception as e:
                logger.critical(f"Failed to connect to Firestore: {e}")
                raise RuntimeError(f"CRITICAL: Firestore connection failed: {e}. Zero-fallback policy in effect.") from e

        case "LOCAL":
            # Standard Production JSON DB
            return TinyDBClient(settings.prod_db_path)

        case _:
            # Default fallback
            logger.warning(f"Unknown storage_backend '{backend}'. Defaulting to LOCAL.")
            return TinyDBClient(settings.prod_db_path)

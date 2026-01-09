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
    @abstractmethod
    def insert(self, document: dict[str, Any]) -> Any:
        pass

    @abstractmethod
    def all(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def search(self, query: Any) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    def get(self, query: Any) -> dict[str, Any] | None:
        pass

    @abstractmethod
    def update(self, fields: dict[str, Any], query: Any = None, doc_ids: list[int] | None = None) -> list[int]:
        pass

    @abstractmethod
    def upsert(self, document: dict[str, Any], query: Any) -> list[int]:
        pass

    @abstractmethod
    def remove(self, query: Any) -> list[int]:
        pass


class AbstractDatabase(ABC):
    @abstractmethod
    def table(self, name: str) -> AbstractTable:
        pass

    @abstractmethod
    def close(self):
        pass


# --- TinyDB Implementation ---


class TinyDBTable(AbstractTable):
    def __init__(self, db_path: str, table_name: str):
        self._path = db_path
        self._name = table_name

    def _get_table(self, db):
        return db.table(self._name)

    def insert(self, document: dict[str, Any]) -> int:
        with TinyDB(self._path, encoding="utf-8") as db:
             return self._get_table(db).insert(document)

    def all(self) -> list[dict[str, Any]]:
        with TinyDB(self._path, encoding="utf-8") as db:
            return self._get_table(db).all()

    def search(self, query: Any) -> list[dict[str, Any]]:
        with TinyDB(self._path, encoding="utf-8") as db:
            return self._get_table(db).search(query)

    def get(self, query: Any) -> dict[str, Any] | None:
        with TinyDB(self._path, encoding="utf-8") as db:
            return self._get_table(db).get(query)

    def update(self, fields: dict[str, Any], query: Any = None, doc_ids: list[int] | None = None) -> list[int]:
        with TinyDB(self._path, encoding="utf-8") as db:
            return self._get_table(db).update(fields, cond=query, doc_ids=doc_ids)

    def upsert(self, document: dict[str, Any], query: Any) -> list[int]:
        with TinyDB(self._path, encoding="utf-8") as db:
            return self._get_table(db).upsert(document, query)

    def remove(self, query: Any) -> list[int]:
        with TinyDB(self._path, encoding="utf-8") as db:
            return self._get_table(db).remove(query)


class TinyDBClient(AbstractDatabase):
    def __init__(self, path: str):
        import os
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.path = path
        # Verify creation/access but don't hold connection
        with TinyDB(path, encoding="utf-8") as _:
            pass

    def table(self, name: str) -> AbstractTable:
        return TinyDBTable(self.path, name)

    def close(self):
        pass


# --- Firestore Implementation ---


class FirestoreTable(AbstractTable):
    def __init__(self, collection_ref):
        self._collection = collection_ref

    def insert(self, document: dict[str, Any]) -> Any:
        _, doc_ref = self._collection.add(document)
        return doc_ref.id

    def all(self) -> list[dict[str, Any]]:
        docs = self._collection.stream()
        return [doc.to_dict() for doc in docs]

    def search(self, query: Any) -> list[dict[str, Any]]:
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
        # Return the first match
        docs = self._collection.stream()
        for doc in docs:
            data = doc.to_dict()
            if query(data):
                return data
        return None

    def update(self, fields: dict[str, Any], query: Any = None, doc_ids: list[int] | None = None) -> list[int]:
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
            # Insert new
            doc_id = document.get("id")
            if doc_id:
                self._collection.document(str(doc_id)).set(document)
            else:
                self._collection.add(document)
            return [1]

    def remove(self, query: Any) -> list[int]:
        docs = self._collection.stream()
        removed_count = 0
        for doc in docs:
            if query(doc.to_dict()):
                doc.reference.delete()
                removed_count += 1
        return [1] * removed_count

    def close(self):
        pass


class FirestoreClient(AbstractDatabase):
    def __init__(self):
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
             # Better: try to get a non-existent doc to prove connectivity without permissions error if list is restricted
             # But list_collections is standard matching `wrapper.py` previous intent.
             # Actually, just `next(self.db.collections(), None)` is enough to verify auth works.
             # Or `self.db.collection('system_settings').limit(1).get()`
             logger.info("[Firestore] Verifying connection...")
             # self.db.collection('system_settings').limit(1).get() # Might fail if empty? No, returns empty list.
             # Simpler:
             list(self.db.collection("connectivity_test").limit(1).stream())
             logger.info("[Firestore] Connection VERIFIED successfully.")
        except Exception as e:
            logger.critical(f"[Firestore] Connection ping FAILED: {e}")
            raise RuntimeError(f"Firestore connectivity test failed. Check internet/VPN/Credentials. Error: {e}")

    def table(self, name: str) -> AbstractTable:
        return FirestoreTable(self.db.collection(name))

    def close(self):
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

    if backend == "FIRESTORE":
        if not FIRESTORE_AVAILABLE:
            raise RuntimeError("CRITICAL: Firestore requested (STORAGE_BACKEND=FIRESTORE) but 'firebase_admin' or 'google-cloud-firestore' is not installed.")

        try:
            return FirestoreClient()
        except Exception as e:
            logger.critical(f"Failed to connect to Firestore: {e}")
            raise RuntimeError(f"CRITICAL: Firestore connection failed: {e}. Zero-fallback policy in effect.")

    elif backend == "LOCAL":
        # Standard Production JSON DB
        return TinyDBClient(settings.prod_db_path)

    else:
        # Default fallback
        logger.warning(f"Unknown storage_backend '{backend}'. Defaulting to LOCAL.")
        return TinyDBClient(settings.prod_db_path)

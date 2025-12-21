from abc import ABC, abstractmethod
from typing import Any, List, Dict, Optional, Union
import logging
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
    def insert(self, document: Dict[str, Any]) -> Any:
        pass

    @abstractmethod
    def all(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def search(self, query: Any) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get(self, query: Any) -> Optional[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def update(self, fields: Dict[str, Any], query: Any) -> List[int]:
        pass
        
    @abstractmethod
    def upsert(self, document: Dict[str, Any], query: Any) -> List[int]:
        pass

    @abstractmethod
    def remove(self, query: Any) -> List[int]:
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
    def __init__(self, table):
        self._table = table

    def insert(self, document: Dict[str, Any]) -> int:
        return self._table.insert(document)

    def all(self) -> List[Dict[str, Any]]:
        return self._table.all()

    def search(self, query: Any) -> List[Dict[str, Any]]:
        return self._table.search(query)

    def get(self, query: Any) -> Optional[Dict[str, Any]]:
        return self._table.get(query)

    def update(self, fields: Dict[str, Any], query: Any) -> List[int]:
        return self._table.update(fields, query)

    def upsert(self, document: Dict[str, Any], query: Any) -> List[int]:
         return self._table.upsert(document, query)

    def remove(self, query: Any) -> List[int]:
        return self._table.remove(query)

class TinyDBClient(AbstractDatabase):
    def __init__(self, path: str):
        import os
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.db = TinyDB(path, encoding='utf-8')

    def table(self, name: str) -> AbstractTable:
        return TinyDBTable(self.db.table(name))

    def close(self):
        self.db.close()

# --- Firestore Implementation ---

class FirestoreTable(AbstractTable):
    def __init__(self, collection_ref):
        self._collection = collection_ref

    def insert(self, document: Dict[str, Any]) -> Any:
        _, doc_ref = self._collection.add(document)
        return doc_ref.id

    def all(self) -> List[Dict[str, Any]]:
        docs = self._collection.stream()
        return [doc.to_dict() for doc in docs]

    def search(self, query: Any) -> List[Dict[str, Any]]:
        # NOTE: This requires significant translation from TinyDB queries to Firestore filters.
        # For now, we raise NotImplementedError as this depends on the specific query format used.
        raise NotImplementedError("Direct search query translation to Firestore is not yet implemented.")

    def get(self, query: Any) -> Optional[Dict[str, Any]]:
        raise NotImplementedError("Direct get query translation to Firestore is not yet implemented.")

    def update(self, fields: Dict[str, Any], query: Any) -> List[int]:
        raise NotImplementedError("Direct update query translation to Firestore is not yet implemented.")

    def upsert(self, document: Dict[str, Any], query: Any) -> List[int]:
         raise NotImplementedError("Direct upsert query translation to Firestore is not yet implemented.")

    def remove(self, query: Any) -> List[int]:
         raise NotImplementedError("Direct remove query translation to Firestore is not yet implemented.")

class FirestoreClient(AbstractDatabase):
    def __init__(self):
        if not FIRESTORE_AVAILABLE:
            raise ImportError("firebase_admin is not installed.")
        
        try:
            if not firebase_admin._apps:
                cred = credentials.ApplicationDefault()
                firebase_admin.initialize_app(cred)
            self.db = firestore.client()
        except Exception as e:
            logger.error(f"Failed to initialize Firestore: {e}")
            raise e

    def table(self, name: str) -> AbstractTable:
        return FirestoreTable(self.db.collection(name))

    def close(self):
        pass

# --- Factory Function ---

def get_db_client() -> AbstractDatabase:
    """
    Factory to get the appropriate database client based on configuration.
    """
    from backend.settings import get_settings
    settings = get_settings()

    if settings.use_mock_db:
        return TinyDBClient(settings.start_db_path)
    else:
        if not FIRESTORE_AVAILABLE:
            logger.warning("Firestore requested but not available. Falling back to TinyDB.")
            return TinyDBClient(settings.start_db_path)
        
        try:
            return FirestoreClient()
        except Exception as e:
            logger.error(f"Failed to create FirestoreClient: {e}. Falling back to TinyDB.")
            return TinyDBClient(settings.start_db_path)

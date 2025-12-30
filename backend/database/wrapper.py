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
        # Fetch all and filter in memory using TinyDB query evaluation
        # This is inefficient for large datasets but acceptable for configuration tables.
        docs = self._collection.stream()
        results = []
        for doc in docs:
            data = doc.to_dict()
            if query(data):
                results.append(data)
        return results

    def get(self, query: Any) -> Optional[Dict[str, Any]]:
        # Return the first match
        docs = self._collection.stream()
        for doc in docs:
            data = doc.to_dict()
            if query(data):
                return data
        return None

    def update(self, fields: Dict[str, Any], query: Any) -> List[int]:
        docs = self._collection.stream()
        updated_count = 0
        for doc in docs:
            data = doc.to_dict()
            if query(data):
                doc.reference.update(fields)
                updated_count += 1
        return [1] * updated_count

    def upsert(self, document: Dict[str, Any], query: Any) -> List[int]:
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
            doc_id = document.get('id')
            if doc_id:
                self._collection.document(str(doc_id)).set(document)
            else:
                self._collection.add(document)
            return [1]

    def remove(self, query: Any) -> List[int]:
        docs = self._collection.stream()
        removed_count = 0
        for doc in docs:
            if query(doc.to_dict()):
                doc.reference.delete()
                removed_count += 1
        return [1] * removed_count

    def close(self):
        pass

# --- Factory Function ---

def get_db_client() -> AbstractDatabase:
    """
    Factory to get the appropriate database client based on configuration.
    """
    from backend.settings import get_settings
    settings = get_settings()

    # 1. Mock Mode (Priority)
    if settings.use_mock_db:
        return TinyDBClient(settings.mock_db_path)

    # 2. Production Modes
    backend = settings.storage_backend.strip().upper()
    
    if backend == "FIRESTORE":
        if not FIRESTORE_AVAILABLE:
            logger.warning("Firestore requested but not available. Falling back to Local TinyDB.")
            return TinyDBClient(settings.prod_db_path)
        
        try:
            return FirestoreClient()
        except Exception as e:
            logger.error(f"Failed to create FirestoreClient: {e}. Falling back to Local TinyDB.")
            return TinyDBClient(settings.prod_db_path)
            
    elif backend == "LOCAL":
        # Standard Production JSON DB
        return TinyDBClient(settings.prod_db_path)
        
    else:
        # Default fallback
        logger.warning(f"Unknown storage_backend '{backend}'. Defaulting to LOCAL.")
        return TinyDBClient(settings.prod_db_path)

from typing import Any
from tinydb import Query
from src.database.client import DatabaseClient
import uuid

class TinyDBAdapter:
    """
    Adapter for TinyDB to match FirestoreClient interface.
    Enables local execution without Google Cloud.
    """
    def __init__(self):
        self.client = DatabaseClient()

    def get_document(self, collection_name: str, doc_id: str) -> dict[str, Any] | None:
        table = self.client.get_table(collection_name)
        # Assuming 'id' field is used for lookups, or we use doc_id if it's an int?
        # Firestore uses string IDs. TinyDB uses int doc_ids by default but we store 'id' field.
        # Let's assume we query by 'id' field.
        User = Query()
        result = table.search(User.id == doc_id)
        if result:
            return result[0]
        return None

    def upsert_document(self, collection_name: str, doc_id: str, data: dict[str, Any]):
        table = self.client.get_table(collection_name)
        User = Query()
        # Check if exists
        if table.search(User.id == doc_id):
            table.update(data, User.id == doc_id)
        else:
            # Ensure ID is in data
            if 'id' not in data:
                data['id'] = doc_id
            table.insert(data)
        return doc_id

    def add_document(self, collection_name: str, data: dict[str, Any]) -> str:
        """Adds a document with an auto-generated ID."""
        table = self.client.get_table(collection_name)
        doc_id = str(uuid.uuid4())
        data['id'] = doc_id
        table.insert(data)
        return doc_id

    def get_all(self, collection_name: str) -> list[dict[str, Any]]:
        table = self.client.get_table(collection_name)
        return table.all()

    def query(self, collection_name: str, field: str, operator: str, value: Any) -> list[dict[str, Any]]:
        """
        Simple query wrapper.
        Only supports '==' for now in this adapter for simplicity.
        """
        table = self.client.get_table(collection_name)
        User = Query()
        if operator == "==":
            return table.search(getattr(User, field) == value)
        else:
            # Fallback: return all and filter in memory (not efficient but works for local)
            all_docs = table.all()
            # TODO: Implement other operators if needed
            return all_docs

from typing import Dict, Any, List, Optional
from google.cloud import firestore
import os
import json

class FirestoreClient:
    """
    Database client for Google Cloud Firestore.
    Implements a similar interface to TinyDB for compatibility, but adapted for NoSQL.
    """
    def __init__(self, project_id: str = None):
        # If project_id is not provided, it will be inferred from the environment
        self.db = firestore.Client(project=project_id)
        print(f"[FirestoreClient] Connected to project: {self.db.project}")

    def get_collection(self, collection_name: str):
        return self.db.collection(collection_name)

    def get_document(self, collection_name: str, doc_id: str) -> Optional[Dict[str, Any]]:
        doc_ref = self.db.collection(collection_name).document(doc_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None

    def upsert_document(self, collection_name: str, doc_id: str, data: Dict[str, Any]):
        doc_ref = self.db.collection(collection_name).document(doc_id)
        doc_ref.set(data, merge=True)
        return doc_id

    def add_document(self, collection_name: str, data: Dict[str, Any]) -> str:
        """Adds a document with an auto-generated ID."""
        update_time, doc_ref = self.db.collection(collection_name).add(data)
        return doc_ref.id

    def get_all(self, collection_name: str) -> List[Dict[str, Any]]:
        docs = self.db.collection(collection_name).stream()
        return [doc.to_dict() for doc in docs]

    def query(self, collection_name: str, field: str, operator: str, value: Any) -> List[Dict[str, Any]]:
        """
        Simple query wrapper.
        Operator symbols: ==, <, <=, >, >=, !=, array_contains, etc.
        """
        docs = self.db.collection(collection_name).where(field, operator, value).stream()
        return [doc.to_dict() for doc in docs]

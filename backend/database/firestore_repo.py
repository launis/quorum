from typing import List, Optional, Dict, Any, Union
import logging
from backend.database.repository import AbstractWorkflowRepository
from backend.database.wrapper import AbstractDatabase

# Check for Firestore availability
try:
    from firebase_admin import firestore
except ImportError:
    firestore = None

logger = logging.getLogger(__name__)

class FirestoreWorkflowRepository(AbstractWorkflowRepository):
    """
    Firestore Implementation of the Workflow Repository.
    """
    def __init__(self, db_client: AbstractDatabase):
        if not firestore:
            raise ImportError("firebase_admin module not found. cannot use FirestoreWorkflowRepository.")
        
        # We assume db_client is an instance of FirestoreClient from backend.database.wrapper
        if hasattr(db_client, 'db'):
            self.client = db_client.db  # type: firestore.Client
        else:
            raise ValueError("FirestoreWorkflowRepository expects a FirestoreClient with a .db attribute.")

    def _get_doc(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        doc = self.client.collection(collection).document(doc_id).get()
        if doc.exists:
            return doc.to_dict()
        return None

    def _find_one_by_field(self, collection: str, field: str, value: Any) -> Optional[Dict[str, Any]]:
        docs = self.client.collection(collection).where(field, "==", value).limit(1).stream()
        for doc in docs:
            return doc.to_dict()
        return None

    def _get_all(self, collection: str) -> List[Dict[str, Any]]:
        docs = self.client.collection(collection).stream()
        return [doc.to_dict() for doc in docs]

    # --- Components ---
    def get_component_by_id(self, component_id: str) -> Optional[Dict[str, Any]]:
        # Try direct lookup if ID is the key, otherwise search
        # We enforce ID-as-Key for new insertions, but handle legacy/mixed
        return self._find_one_by_field('components', 'id', component_id)

    def get_component_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        return self._find_one_by_field('components', 'name', name)

    def register_component(self, component_data: Dict[str, Any]):
        # Use 'id' or 'name' as document key if possible to ensure uniqueness
        doc_id = component_data.get('id', component_data.get('name'))
        if doc_id:
            self.client.collection('components').document(doc_id).set(component_data)
        else:
            self.client.collection('components').add(component_data)

    def update_component_metadata(self, name: str, module: str, component_class: str):
        # First find the document
        docs = self.client.collection('components').where('name', '==', name).limit(1).stream()
        for doc in docs:
            doc.reference.update({
                "module": module,
                "class": component_class
            })

    def get_all_components(self) -> List[Dict[str, Any]]:
        return self._get_all('components')

    # --- Steps ---
    def get_step_by_id(self, step_id: str) -> Optional[Dict[str, Any]]:
        return self._find_one_by_field('steps', 'id', step_id)

    def get_all_steps(self) -> List[Dict[str, Any]]:
        return self._get_all('steps')

    # --- Workflows ---
    def get_workflow_by_id(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        return self._find_one_by_field('workflows', 'id', workflow_id)

    def create_workflow(self, workflow_data: Dict[str, Any]) -> Union[int, str]:
        wf_id = workflow_data.get('id')
        if wf_id:
            self.client.collection('workflows').document(str(wf_id)).set(workflow_data)
            return wf_id
        else:
            _, doc_ref = self.client.collection('workflows').add(workflow_data)
            return doc_ref.id

    def get_all_workflows(self) -> List[Dict[str, Any]]:
        return self._get_all('workflows')

    # --- Executions ---
    def create_execution(self, execution_data: Dict[str, Any]) -> Union[int, str]:
        exec_id = execution_data.get('execution_id')
        if exec_id:
            # Use execution_id as the document ID for O(1) access
            self.client.collection('executions').document(str(exec_id)).set(execution_data)
            return exec_id
        else:
            _, doc_ref = self.client.collection('executions').add(execution_data)
            return doc_ref.id

    def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        # Try direct access first (fastest)
        doc = self.client.collection('executions').document(str(execution_id)).get()
        if doc.exists:
            return doc.to_dict()
        
        # Fallback to field search if not found (in case ID format mismatched legacy)
        return self._find_one_by_field('executions', 'execution_id', execution_id)

    def update_execution(self, execution_id: str, updates: Dict[str, Any]):
        # Try direct access
        doc_ref = self.client.collection('executions').document(str(execution_id))
        if doc_ref.get().exists:
            doc_ref.update(updates)
        else:
            # Fallback search
            docs = self.client.collection('executions').where('execution_id', '==', str(execution_id)).limit(1).stream()
            for doc in docs:
                doc.reference.update(updates)

    def get_all_executions(self) -> List[Dict[str, Any]]:
        return self._get_all('executions')

    # --- Config ---
    def get_model_registry(self) -> Optional[Dict[str, Any]]:
        return self._find_one_by_field('system_config', 'type', 'model_registry')

    def get_banned_phrases(self) -> List[Dict[str, Any]]:
        return self._get_all('banned_phrases')

    def add_banned_phrase(self, phrase: str, **kwargs):
        # Check specific existence
        existing = self.client.collection('banned_phrases').where('phrase', '==', phrase).limit(1).get()
        if not existing:
            data = {"phrase": phrase}
            data.update(kwargs)
            self.client.collection('banned_phrases').add(data)

    def remove_banned_phrase(self, phrase: str):
         docs = self.client.collection('banned_phrases').where('phrase', '==', phrase).stream()
         for doc in docs:
             doc.reference.delete()

    # --- Knowledge Base ---
    def get_knowledge_base_items(self) -> List[Dict[str, Any]]:
        return self._get_all('knowledge_base')

    def add_knowledge_base_item(self, item_data: Dict[str, Any]):
        self.client.collection('knowledge_base').add(item_data)

    def clear_knowledge_base(self):
        # Firestore doesn't have a simple truncate. We must delete individually or use batch.
        # For safety/simplicity in this context, we iterate and delete.
        # This might be slow for large datasets.
        batch_size = 500
        docs = self.client.collection('knowledge_base').limit(batch_size).stream()
        count = 0
        for doc in docs:
            doc.reference.delete()
            count += 1
        
        # If there were more than batch_size, we might need a loop, but simple implementation for now.
        if count >= batch_size:
            self.clear_knowledge_base() # Recurse/Loop until empty

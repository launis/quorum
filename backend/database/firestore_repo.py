from typing import List, Optional, Dict, Any, Union
import logging
from backend.database.repository import AbstractWorkflowRepository
from backend.database.wrapper import AbstractDatabase

# Check for Firestore availability
try:
    from firebase_admin import firestore
    try:
         from google.cloud import firestore as google_cloud_firestore
         FIRESTORE_LIB_AVAILABLE = True
    except ImportError:
         FIRESTORE_LIB_AVAILABLE = False
except ImportError:
    firestore = None
    FIRESTORE_LIB_AVAILABLE = False

logger = logging.getLogger(__name__)

class FirestoreWorkflowRepository(AbstractWorkflowRepository):
    """
    Firestore Implementation of the Workflow Repository.
    Native Async Implementation.
    """
    def __init__(self, db_client: AbstractDatabase):
        if not FIRESTORE_LIB_AVAILABLE:
            raise ImportError("backend.database.firestore_repo requires google-cloud-firestore for Native Async mode.")
        
        # We assume db_client is an instance of FirestoreClient from backend.database.wrapper
        # But for Native Async, we usually need the AsyncClient, not the Admin Client.
        # The AbstractDatabase wrapper usually wraps the Admin SDK.
        # Here we initialize a Native Async Client separately or reuse if possible.
        
        # NOTE: For simplicity in this architectural refactor, we are instantiating a new AsyncClient.
        # In production, this should likely be passed in via DI properly.
        self.db = google_cloud_firestore.AsyncClient()

    # --- Core Helpers ---
    async def _get_doc(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        doc = await self.db.collection(collection).document(str(doc_id)).get()
        if doc.exists:
            return doc.to_dict()
        return None

    async def _find_one_by_field(self, collection: str, field: str, value: Any) -> Optional[Dict[str, Any]]:
        docs = self.db.collection(collection).where(field, '==', value).limit(1).stream()
        async for doc in docs:
            return doc.to_dict()
        return None

    async def _get_all(self, collection: str) -> List[Dict[str, Any]]:
        docs = self.db.collection(collection).stream()
        return [doc.to_dict() async for doc in docs]

    async def _delete_doc(self, collection: str, doc_key: str, doc_value: str):
         docs = self.db.collection(collection).where(doc_key, '==', doc_value).stream()
         async for doc in docs:
             await doc.reference.delete()

    async def _update_doc(self, collection: str, doc_key: str, doc_value: str, updates: Dict[str, Any]):
         docs = self.db.collection(collection).where(doc_key, '==', doc_value).stream()
         async for doc in docs:
             await doc.reference.update(updates)

    # --- Components ---
    async def get_component_by_id(self, component_id: str) -> Optional[Dict[str, Any]]:
        return await self._find_one_by_field('components', 'id', component_id)

    async def get_component_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        return await self._find_one_by_field('components', 'name', name)

    async def register_component(self, component_data: Dict[str, Any]):
        doc_id = component_data.get('id', component_data.get('name'))
        if doc_id:
            await self.db.collection('components').document(doc_id).set(component_data)
        else:
            await self.db.collection('components').add(component_data)

    async def update_component_metadata(self, name: str, module: str, component_class: str):
        await self._update_doc('components', 'name', name, {
            "module": module,
            "class": component_class
        })

    async def get_all_components(self) -> List[Dict[str, Any]]:
        return await self._get_all('components')

    # --- Steps ---
    async def get_step_by_id(self, step_id: str) -> Optional[Dict[str, Any]]:
        return await self._find_one_by_field('steps', 'id', step_id)

    async def get_all_steps(self) -> List[Dict[str, Any]]:
        return await self._get_all('steps')
    
    async def create_step(self, step_data: Dict[str, Any]) -> str:
        s_id = step_data.get('id')
        if s_id:
            await self.db.collection('steps').document(str(s_id)).set(step_data)
            return s_id
        else:
            _, ref = await self.db.collection('steps').add(step_data)
            return ref.id

    async def update_step(self, step_id: str, updates: Dict[str, Any]):
        await self._update_doc('steps', 'id', step_id, updates)

    async def delete_step(self, step_id: str):
        await self._delete_doc('steps', 'id', step_id)

    # --- Workflows ---
    async def get_workflow_by_id(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        return await self._find_one_by_field('workflows', 'id', workflow_id)

    async def create_workflow(self, workflow_data: Dict[str, Any]) -> Union[int, str]:
        wf_id = workflow_data.get('id')
        if wf_id:
            await self.db.collection('workflows').document(str(wf_id)).set(workflow_data)
            return wf_id
        else:
            _, doc_ref = await self.db.collection('workflows').add(workflow_data)
            return doc_ref.id

    async def get_all_workflows(self, organization_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if organization_id:
            docs = self.db.collection('workflows').where('organization_id', '==', organization_id).stream()
            return [doc.to_dict() async for doc in docs]
        return await self._get_all('workflows')
    
    async def update_workflow(self, workflow_id: str, updates: Dict[str, Any]):
        await self._update_doc('workflows', 'id', workflow_id, updates)

    async def delete_workflow(self, workflow_id: str):
        await self._delete_doc('workflows', 'id', workflow_id)

    # --- Executions ---
    async def create_execution(self, execution_data: Dict[str, Any]) -> Union[int, str]:
        exec_id = execution_data.get('execution_id')
        if exec_id:
            await self.db.collection('executions').document(str(exec_id)).set(execution_data)
            return exec_id
        else:
            _, doc_ref = await self.db.collection('executions').add(execution_data)
            return doc_ref.id

    async def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        doc = await self.db.collection('executions').document(str(execution_id)).get()
        if doc.exists:
            return doc.to_dict()
        return await self._find_one_by_field('executions', 'execution_id', execution_id)

    async def update_execution(self, execution_id: str, updates: Dict[str, Any]):
         doc_ref = self.db.collection('executions').document(str(execution_id))
         snp = await doc_ref.get()
         if snp.exists:
             await doc_ref.update(updates)
         else:
             await self._update_doc('executions', 'execution_id', str(execution_id), updates)

    async def get_all_executions(self, organization_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if organization_id:
            docs = self.db.collection('executions').where('organization_id', '==', organization_id).stream()
            return [doc.to_dict() async for doc in docs]
        return await self._get_all('executions')

    # --- Config ---
    async def get_model_registry(self) -> Optional[Dict[str, Any]]:
        return await self._find_one_by_field('system_config', 'type', 'model_registry')

    async def get_banned_phrases(self) -> List[Dict[str, Any]]:
        return await self._get_all('banned_phrases')

    async def add_banned_phrase(self, phrase: str, **kwargs):
        existing = await self._find_one_by_field('banned_phrases', 'phrase', phrase)
        if not existing:
            data = {"phrase": phrase}
            data.update(kwargs)
            await self.db.collection('banned_phrases').add(data)

    async def remove_banned_phrase(self, phrase: str):
         await self._delete_doc('banned_phrases', 'phrase', phrase)

    # --- Knowledge Base ---
    async def get_knowledge_base_items(self) -> List[Dict[str, Any]]:
        return await self._get_all('knowledge_base')

    async def add_knowledge_base_item(self, item_data: Dict[str, Any]):
        await self.db.collection('knowledge_base').add(item_data)

    async def clear_knowledge_base(self):
        docs = self.db.collection('knowledge_base').limit(500).stream()
        async for doc in docs:
            await doc.reference.delete()

    # --- Organization Management ---
    async def create_organization(self, org_data: Dict[str, Any]) -> str:
        org_id = org_data.get('id')
        if org_id:
            await self.db.collection('organizations').document(str(org_id)).set(org_data)
            return org_id
        else:
            _, doc_ref = await self.db.collection('organizations').add(org_data)
            return doc_ref.id

    async def get_organization(self, org_id: str) -> Optional[Dict[str, Any]]:
        return await self._get_doc('organizations', org_id)

    async def update_organization(self, org_id: str, updates: Dict[str, Any]):
        await self.db.collection('organizations').document(str(org_id)).update(updates)

    async def list_organizations(self) -> List[Dict[str, Any]]:
        return await self._get_all('organizations')

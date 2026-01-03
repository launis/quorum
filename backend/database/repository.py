import asyncio
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Union
from backend.database.wrapper import AbstractDatabase
from tinydb import Query

class AbstractWorkflowRepository(ABC):
    """
    Universal Async Interface for Workflow Data Access.
    
    This replaces the old Sync/Async split. All repositories are now Async First.
    TinyDB implementations must use asyncio.to_thread internally.
    """
    
    # --- Components ---
    @abstractmethod
    async def get_component_by_id(self, component_id: str) -> Optional[Dict[str, Any]]: pass

    @abstractmethod
    async def get_component_by_name(self, name: str) -> Optional[Dict[str, Any]]: pass

    @abstractmethod
    async def register_component(self, component_data: Dict[str, Any]): pass

    @abstractmethod
    async def update_component_metadata(self, name: str, module: str, component_class: str): pass

    @abstractmethod
    async def get_all_components(self) -> List[Dict[str, Any]]: pass

    # --- Steps ---
    @abstractmethod
    async def get_step_by_id(self, step_id: str) -> Optional[Dict[str, Any]]: pass

    @abstractmethod
    async def get_all_steps(self) -> List[Dict[str, Any]]: pass

    @abstractmethod
    async def create_step(self, step_data: Dict[str, Any]) -> str: pass

    @abstractmethod
    async def update_step(self, step_id: str, updates: Dict[str, Any]): pass

    @abstractmethod
    async def delete_step(self, step_id: str): pass

    # --- Workflows ---
    @abstractmethod
    async def get_workflow_by_id(self, workflow_id: str) -> Optional[Dict[str, Any]]: pass

    @abstractmethod
    async def create_workflow(self, workflow_data: Dict[str, Any]) -> Union[int, str]: pass

    @abstractmethod
    async def get_all_workflows(self, organization_id: Optional[str] = None, role: Optional[str] = None) -> List[Dict[str, Any]]: pass

    @abstractmethod
    async def update_workflow(self, workflow_id: str, updates: Dict[str, Any]): pass

    @abstractmethod
    async def delete_workflow(self, workflow_id: str): pass

    # --- Executions ---
    @abstractmethod
    async def create_execution(self, execution_data: Dict[str, Any]) -> Union[int, str]: pass

    @abstractmethod
    async def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]: pass

    @abstractmethod
    async def update_execution(self, execution_id: str, updates: Dict[str, Any]): pass

    @abstractmethod
    async def get_all_executions(self, organization_id: Optional[str] = None) -> List[Dict[str, Any]]: pass

    # --- Config ---
    @abstractmethod
    async def get_model_registry(self) -> Optional[Dict[str, Any]]: pass

    @abstractmethod
    async def get_banned_phrases(self) -> List[Dict[str, Any]]: pass

    @abstractmethod
    async def add_banned_phrase(self, phrase: str, **kwargs): pass

    @abstractmethod
    async def remove_banned_phrase(self, phrase: str): pass

    # --- Knowledge Base ---
    @abstractmethod
    async def get_knowledge_base_items(self) -> List[Dict[str, Any]]: pass

    @abstractmethod
    async def add_knowledge_base_item(self, item_data: Dict[str, Any]): pass
    
    @abstractmethod
    async def clear_knowledge_base(self): pass

    # --- Organization Management ---
    @abstractmethod
    async def create_organization(self, org_data: Dict[str, Any]) -> str: pass

    @abstractmethod
    async def get_organization(self, org_id: str) -> Optional[Dict[str, Any]]: pass

    @abstractmethod
    async def update_organization(self, org_id: str, updates: Dict[str, Any]): pass

    @abstractmethod
    async def list_organizations(self) -> List[Dict[str, Any]]: pass

    @abstractmethod
    async def delete_organization(self, org_id: str): pass

    @abstractmethod
    async def delete_org_data(self, org_id: str): pass


class TinyDBRepository(AbstractWorkflowRepository):
    """
    Async-First TinyDB Repository.
    Wraps synchronous TinyDB calls in asyncio.to_thread.
    """
    def __init__(self, db_client: AbstractDatabase):
        self.db = db_client
        self.components = self.db.table('components')
        self.steps = self.db.table('steps')
        self.workflows = self.db.table('workflows')
        self.executions = self.db.table('executions')
        self.banned_phrases = self.db.table('banned_phrases')
        self.knowledge_base = self.db.table('knowledge_base')
        self.system_config = self.db.table('system_config')
        self.organizations = self.db.table('organizations')

    async def _run(self, func, *args, **kwargs):
        """Helper to run sync DB calls in thread."""
        return await asyncio.to_thread(func, *args, **kwargs)

    # --- Components ---
    async def get_component_by_id(self, component_id: str) -> Optional[Dict[str, Any]]:
        def _get():
            Q = Query()
            res = self.components.search(Q.id == component_id)
            return res[0] if res else None
        return await self._run(_get)

    async def get_component_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        def _get():
            Q = Query()
            res = self.components.search(Q.name == name)
            return res[0] if res else None
        return await self._run(_get)

    async def register_component(self, component_data: Dict[str, Any]):
        await self._run(self.components.insert, component_data)

    async def update_component_metadata(self, name: str, module: str, component_class: str):
        def _update():
            Q = Query()
            self.components.update({
                 "module": module,
                 "class": component_class
            }, Q.name == name)
        await self._run(_update)

    async def get_all_components(self) -> List[Dict[str, Any]]:
        return await self._run(self.components.all)

    # --- Steps ---
    async def get_step_by_id(self, step_id: str) -> Optional[Dict[str, Any]]:
        def _get():
            Q = Query()
            res = self.steps.search(Q.id == step_id)
            return res[0] if res else None
        return await self._run(_get)

    async def get_all_steps(self) -> List[Dict[str, Any]]:
        return await self._run(self.steps.all)

    async def create_step(self, step_data: Dict[str, Any]) -> str:
        # TinyDB insert returns document ID (int), we convert to str/int
        res = await self._run(self.steps.insert, step_data)
        return str(res)

    async def update_step(self, step_id: str, updates: Dict[str, Any]):
        def _update():
            Q = Query()
            self.steps.update(updates, Q.id == step_id)
        await self._run(_update)

    async def delete_step(self, step_id: str):
        def _delete():
            Q = Query()
            self.steps.remove(Q.id == step_id)
        await self._run(_delete)

    # --- Workflows ---
    async def get_workflow_by_id(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        def _get():
            Q = Query()
            res = self.workflows.search(Q.id == workflow_id)
            return res[0] if res else None
        return await self._run(_get)

    async def create_workflow(self, workflow_data: Dict[str, Any]) -> Union[int, str]:
        return await self._run(self.workflows.insert, workflow_data)

    async def get_all_workflows(self, organization_id: Optional[str] = None, role: Optional[str] = None) -> List[Dict[str, Any]]:
        def _get():
            all_wfs = self.workflows.all()
            
            # Root View: See EVERYTHING if filtering by system/root
            if role == "ROOT":
                 return all_wfs

            # Tenant View
            filtered = []
            for wf in all_wfs:
                wf_org = wf.get('organization_id')
                is_system = (wf_org is None or wf_org == "system")
                is_public = wf.get('is_public', False)
                
                # 1. Own Org Workflows
                if organization_id and wf_org == organization_id:
                    filtered.append(wf)
                
                # 2. System Workflows (Public Only, unless Root handled above)
                elif is_system and is_public:
                    filtered.append(wf)
                    
            return filtered
            
        return await self._run(_get)

    async def update_workflow(self, workflow_id: str, updates: Dict[str, Any]):
        def _update():
             Q = Query()
             self.workflows.update(updates, Q.id == workflow_id)
        await self._run(_update)

    async def delete_workflow(self, workflow_id: str):
        def _delete():
             Q = Query()
             self.workflows.remove(Q.id == workflow_id)
        await self._run(_delete)

    # --- Executions ---
    async def create_execution(self, execution_data: Dict[str, Any]) -> Union[int, str]:
        return await self._run(self.executions.insert, execution_data)

    async def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        def _get():
            Q = Query()
            res = self.executions.search(Q.execution_id == str(execution_id))
            return res[0] if res else None
        return await self._run(_get)

    async def update_execution(self, execution_id: str, updates: Dict[str, Any]):
        def _update():
            Q = Query()
            self.executions.update(updates, Q.execution_id == str(execution_id))
        await self._run(_update)

    async def get_all_executions(self, organization_id: Optional[str] = None, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        def _get():
            all_execs = self.executions.all()
            
            # 1. Tenant Filter
            if organization_id:
                all_execs = [e for e in all_execs if e.get('organization_id') == organization_id]
            
            # 2. User Filter (Member Role)
            if user_id:
                all_execs = [e for e in all_execs if e.get('user_id') == user_id]
                
            return all_execs
        return await self._run(_get)

    # --- Config ---
    async def get_model_registry(self) -> Optional[Dict[str, Any]]:
        def _get():
            Q = Query()
            res = self.system_config.search(Q.type == 'model_registry')
            return res[0] if res else None
        return await self._run(_get)

    async def get_banned_phrases(self) -> List[Dict[str, Any]]:
        return await self._run(self.banned_phrases.all)

    async def add_banned_phrase(self, phrase: str, **kwargs):
        def _add():
            existing = self.banned_phrases.search(Query().phrase == phrase)
            if not existing:
                data = {"phrase": phrase}
                data.update(kwargs)
                return self.banned_phrases.insert(data)
        await self._run(_add)

    async def remove_banned_phrase(self, phrase: str):
        def _remove():
            self.banned_phrases.remove(Query().phrase == phrase)
        await self._run(_remove)

    # --- Knowledge Base ---
    async def get_knowledge_base_items(self) -> List[Dict[str, Any]]:
        return await self._run(self.knowledge_base.all)

    async def add_knowledge_base_item(self, item_data: Dict[str, Any]):
        await self._run(self.knowledge_base.insert, item_data)
        
    async def clear_knowledge_base(self):
        await self._run(self.knowledge_base.truncate)

    # --- Organization Management ---
    async def create_organization(self, org_data: Dict[str, Any]) -> str:
        # For simplicity, we assume org_data already has 'id' or we let TinyDB trigger one.
        # But our ABC expects a string return ID.
        result = await self._run(self.organizations.insert, org_data)
        return str(result)

    async def get_organization(self, org_id: str) -> Optional[Dict[str, Any]]:
        def _get():
            Q = Query()
            res = self.organizations.search(Q.id == org_id)
            return res[0] if res else None
        return await self._run(_get)

    async def update_organization(self, org_id: str, updates: Dict[str, Any]):
        def _update():
            Q = Query()
            self.organizations.update(updates, Q.id == org_id)
        await self._run(_update)

    async def list_organizations(self) -> List[Dict[str, Any]]:
        return await self._run(self.organizations.all)

    async def delete_organization(self, org_id: str):
        def _delete():
            Q = Query()
            self.organizations.remove(Q.id == org_id)
        await self._run(_delete)

    async def delete_org_data(self, org_id: str):
        """
        Cascading delete for organization data (Workflows, Executions).
        """
        def _delete_data():
            # 1. Delete Workflows
            self.workflows.remove(Query().organization_id == org_id)
            # 2. Delete Executions
            self.executions.remove(Query().organization_id == org_id)
        await self._run(_delete_data)

# Backward compatibility alias
WorkflowRepository = TinyDBRepository

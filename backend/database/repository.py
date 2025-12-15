from typing import List, Optional, Dict, Any
from backend.database.wrapper import AbstractDatabase
from tinydb import Query

class WorkflowRepository:
    def __init__(self, db_client: AbstractDatabase):
        self.db = db_client
        self.components = self.db.table('components')
        self.steps = self.db.table('steps')
        self.workflows = self.db.table('workflows')
        self.executions = self.db.table('executions')
        self.banned_phrases = self.db.table('banned_phrases')
        self.system_config = self.db.table('system_config')

    # --- Components ---
    def get_component_by_id(self, component_id: str) -> Optional[Dict[str, Any]]:
        Q = Query()
        res = self.components.search(Q.id == component_id)
        return res[0] if res else None

    def get_component_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        Q = Query()
        res = self.components.search(Q.name == name)
        return res[0] if res else None
    
    def register_component(self, component_data: Dict[str, Any]):
        self.components.insert(component_data)

    def update_component_metadata(self, name: str, module: str, component_class: str):
        Q = Query()
        self.components.update({
             "module": module,
             "class": component_class
        }, Q.name == name)
    
    def get_all_components(self) -> List[Dict[str, Any]]:
        return self.components.all()

    # --- Steps ---
    def get_step_by_id(self, step_id: str) -> Optional[Dict[str, Any]]:
        Q = Query()
        res = self.steps.search(Q.id == step_id)
        return res[0] if res else None

    def get_all_steps(self) -> List[Dict[str, Any]]:
        return self.steps.all()

    # --- Workflows ---
    def get_workflow_by_id(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        Q = Query()
        res = self.workflows.search(Q.id == workflow_id)
        return res[0] if res else None

    def create_workflow(self, workflow_data: Dict[str, Any]) -> int:
        return self.workflows.insert(workflow_data)

    def get_all_workflows(self) -> List[Dict[str, Any]]:
        return self.workflows.all()

    # --- Executions ---
    def create_execution(self, execution_data: Dict[str, Any]) -> int:
        return self.executions.insert(execution_data)
        
    def get_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        Q = Query()
        res = self.executions.search(Q.execution_id == str(execution_id))
        return res[0] if res else None

    def update_execution(self, execution_id: str, updates: Dict[str, Any]):
        Q = Query()
        self.executions.update(updates, Q.execution_id == str(execution_id))

    def get_all_executions(self) -> List[Dict[str, Any]]:
        return self.executions.all()

    # --- Config ---
    def get_model_registry(self) -> Optional[Dict[str, Any]]:
        Q = Query()
        res = self.system_config.search(Q.type == 'model_registry')
        return res[0] if res else None
    
    def get_banned_phrases(self) -> List[Dict[str, Any]]:
        return self.banned_phrases.all()

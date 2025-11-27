from typing import Dict, Any
from src.database.client import DatabaseClient
from src.engine.executor import Executor
from tinydb import Query

class Orchestrator:
    def __init__(self):
        self.db_client = DatabaseClient()
        self.executor = Executor()

    def run_workflow(self, workflow_id: str, initial_inputs: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[ORCHESTRATOR] Starting Workflow: {workflow_id}")
        
        workflows_table = self.db_client.get_table('workflows')
        workflow = workflows_table.get(Query().id == workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found.")

        context = initial_inputs.copy()
        
        for step_id in workflow['sequence']:
            print(f"[ORCHESTRATOR] Step: {step_id}")
            # Determine model override if any
            model_override = workflow.get('default_model_mapping', {}).get(step_id)
            
            step_output = self.executor.execute_step(step_id, context, model_override)
            
            # Update context
            context.update(step_output)

        print("[ORCHESTRATOR] Workflow Completed.")
        return context

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from tinydb import TinyDB, Query

from backend.state import WorkflowState, InputData
from backend.agents.guard import GuardAgent
from backend.agents.analyst import AnalystAgent
from backend.agents.logician import LogicianAgent
from backend.agents.critics import (
    LogicalFalsifierAgent, 
    FactualOverseerAgent, 
    CausalAnalystAgent, 
    PerformativityDetectorAgent
)
from backend.agents.judge import JudgeAgent
from backend.agents.xai import XAIReporterAgent

class WorkflowEngine:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.db = TinyDB(db_path, encoding='utf-8')
        
        # Initialize Tables
        self.components_table = self.db.table('components')
        self.steps_table = self.db.table('steps')
        self.workflows_table = self.db.table('workflows')
        self.executions_table = self.db.table('executions')
        
        # Initialize Agents (The Pipeline)
        # In a fully dynamic system, these would be loaded based on the 'steps' config.
        # For now, we hardcode the V2 pipeline for robustness.
        self.agents_map = {
            "GuardAgent": GuardAgent(),
            "AnalystAgent": AnalystAgent(),
            "LogicianAgent": LogicianAgent(),
            "LogicalFalsifierAgent": LogicalFalsifierAgent(),
            "FactualOverseerAgent": FactualOverseerAgent(),
            "CausalAnalystAgent": CausalAnalystAgent(),
            "PerformativityDetectorAgent": PerformativityDetectorAgent(),
            "JudgeAgent": JudgeAgent(),
            "XAIReporterAgent": XAIReporterAgent()
        }
        
        # Ordered pipeline for the default flow
        self.pipeline = [
            self.agents_map["GuardAgent"],
            self.agents_map["AnalystAgent"],
            self.agents_map["LogicianAgent"],
            self.agents_map["LogicalFalsifierAgent"],
            self.agents_map["FactualOverseerAgent"],
            self.agents_map["CausalAnalystAgent"],
            self.agents_map["PerformativityDetectorAgent"],
            self.agents_map["JudgeAgent"],
            self.agents_map["XAIReporterAgent"]
        ]

    # --- LEGACY / MANAGEMENT METHODS (Required by main.py) ---

    def register_component(self, name: str, type: str, class_name: str):
        """
        Registers a component in the DB.
        """
        Component = Query()
        if not self.components_table.search(Component.name == name):
            self.components_table.insert({
                "name": name,
                "type": type,
                "class_name": class_name,
                "registered_at": datetime.now().isoformat()
            })

    def create_workflow(self, name: str, steps: List[Dict[str, Any]]) -> int:
        """
        Creates a new workflow definition.
        """
        workflow_id = self.workflows_table.insert({
            "name": name,
            "steps": steps,
            "created_at": datetime.now().isoformat()
        })
        return workflow_id

    def create_execution(self, workflow_id: Any, inputs: Dict[str, Any]) -> str:
        """
        Creates a new execution record.
        """
        execution_id = str(uuid.uuid4())
        self.executions_table.insert({
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "status": "pending",
            "start_time": datetime.now().isoformat(),
            "inputs": inputs, # Save inputs for debugging/restart
            "logs": []
        })
        return execution_id

    def get_execution_status(self, execution_id: Any) -> Optional[Dict[str, Any]]:
        """
        Retrieves execution status.
        """
        # Handle both int and str IDs (legacy vs new)
        Execution = Query()
        result = self.executions_table.search(Execution.execution_id == str(execution_id))
        if result:
            return result[0]
        return None

    def preview_step_prompt(self, step_id: str) -> Dict[str, Any]:
        # Placeholder for legacy UI compatibility
        return {"preview": "Prompt preview not available in V2 Engine yet.", "error": None}

    def preview_full_chain_prompts(self, workflow_id: str) -> str:
        # Placeholder for legacy UI compatibility
        return "Full chain preview not available in V2 Engine yet."

    # --- CORE EXECUTION LOGIC (V2) ---

    def run_execution(self, execution_id: str, raw_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs the full workflow using the new State-based architecture.
        """
        print(f"[WorkflowEngine] Starting execution {execution_id}")
        
        # Update status to running
        Execution = Query()
        self.executions_table.update({'status': 'running'}, Execution.execution_id == execution_id)
        
        # 1. Initialize State
        try:
            input_data = InputData(
                history_text=raw_inputs.get('history_text', ''),
                product_text=raw_inputs.get('product_text', ''),
                reflection_text=raw_inputs.get('reflection_text', ''),
                bibliography_context=raw_inputs.get('bibliography_context', [])
            )
            
            current_state = WorkflowState(
                execution_id=execution_id,
                inputs=input_data
            )
        except Exception as e:
            print(f"[WorkflowEngine] Failed to initialize state: {e}")
            self.executions_table.update({'status': 'failed', 'error': str(e)}, Execution.execution_id == execution_id)
            raise e

        # 2. Execute Pipeline
        try:
            for agent in self.pipeline:
                agent_name = agent.__class__.__name__
                current_state.current_step_name = agent_name
                print(f"[WorkflowEngine] Running step: {agent_name}")
                
                # Execute agent (updates state internally)
                current_state = agent.execute(current_state)
                
                # Update DB with progress
                self.executions_table.update({
                    'current_step': agent_name,
                    'last_updated': datetime.now().isoformat()
                    # We could save the partial state here too
                }, Execution.execution_id == execution_id)

            # 3. Success
            print(f"[WorkflowEngine] Execution {execution_id} completed successfully.")
            self.executions_table.update({
                'status': 'completed',
                'end_time': datetime.now().isoformat(),
                'result': current_state.model_dump(mode='json') # Save full state as result
            }, Execution.execution_id == execution_id)
            
            return current_state.model_dump(mode='json')

        except Exception as e:
            print(f"[WorkflowEngine] Pipeline crashed at {current_state.current_step_name}: {e}")
            self.executions_table.update({
                'status': 'failed',
                'error': str(e),
                'failed_step': current_state.current_step_name
            }, Execution.execution_id == execution_id)
            raise e

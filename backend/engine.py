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
        self.banned_phrases_table = self.db.table('banned_phrases')
        
        from backend.config import INITIAL_MODEL
        
        # Initialize Agents (The Pipeline)
        # In a fully dynamic system, these would be loaded based on the 'steps' config.
        # For now, we hardcode the V2 pipeline for robustness.
        self.agents_map = {
            "GuardAgent": GuardAgent(model=INITIAL_MODEL),
            "AnalystAgent": AnalystAgent(model=INITIAL_MODEL),
            "LogicianAgent": LogicianAgent(model=INITIAL_MODEL),
            "LogicalFalsifierAgent": LogicalFalsifierAgent(model=INITIAL_MODEL),
            "FactualOverseerAgent": FactualOverseerAgent(model=INITIAL_MODEL),
            "CausalAnalystAgent": CausalAnalystAgent(model=INITIAL_MODEL),
            "PerformativityDetectorAgent": PerformativityDetectorAgent(model=INITIAL_MODEL),
            "JudgeAgent": JudgeAgent(model=INITIAL_MODEL),
            "XAIReporterAgent": XAIReporterAgent(model=INITIAL_MODEL)
        }
        
        #     "XAIReporterAgent": XAIReporterAgent(model=INITIAL_MODEL)
        # }
        
        # Hardcoded pipeline list removed. We purely rely on DB "steps".

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

    def _construct_prompt_for_step(self, step_id: str) -> str:
        """
        Fetches the step configuration and constructs the full system prompt
        by concatenating the content of all referenced prompt components.
        Also inspects for placeholders like {{BANNED_PHRASES}}.
        """
        try:
            Step = Query()
            step_record = self.steps_table.search(Step.id == step_id)
            if not step_record:
                return ""
            
            step_data = step_record[0]
            exec_config = step_data.get('execution_config', {})
            prompt_ids = exec_config.get('llm_prompts', [])
            
            full_prompt_parts = []
            Component = Query()
            
            # Pre-fetch banned phrases if needed
            banned_phrases_list = []
            
            for pid in prompt_ids:
                comp = self.components_table.search(Component.id == pid)
                if comp:
                    content = comp[0].get('content', '')
                    if content:
                        # Check/Replace BANNED_PHRASES
                        if "{{BANNED_PHRASES}}" in content:
                            if not banned_phrases_list:
                                banned_phrases_list = [p['phrase'] for p in self.banned_phrases_table.all()]
                            
                            phrases_str = ", ".join([f'"{p}"' for p in banned_phrases_list]) if banned_phrases_list else "NONE"
                            content = content.replace("{{BANNED_PHRASES}}", phrases_str)
                            
                        full_prompt_parts.append(content)
            
            return "\n\n".join(full_prompt_parts)
        except Exception as e:
            print(f"[WorkflowEngine] Error constructing prompt for step {step_id}: {e}")
            return ""

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
            # Fetch Workflow Definition
            # We assume the execution_id allows us to look up the workflow, 
            # but currently create_execution stores workflow_id.
            
            # Fetch execution record to get workflow_id
            Execution = Query()
            exec_record = self.executions_table.search(Execution.execution_id == execution_id)
            if not exec_record:
                 raise ValueError(f"Execution {execution_id} not found")
            
            workflow_id = exec_record[0]['workflow_id']
            
            # Fetch Workflow Steps
            Workflow = Query()
            wf_record = self.workflows_table.search(Workflow.id == workflow_id)
            
            pipeline_steps = []
            if wf_record:
                step_ids = wf_record[0]['steps']
                # Create a list of (Agent, step_id) to execute
                # We need step_id to fetch the prompt
                Step = Query()
                for sid in step_ids:
                    s_doc = self.steps_table.search(Step.id == sid)
                    if s_doc:
                        agent_name = s_doc[0].get('component')
                        if agent_name in self.agents_map:
                            pipeline_steps.append((self.agents_map[agent_name], s_doc[0]))
            
            # Fallback to hardcoded pipeline if no dynamic workflow found (e.g. for testing)
            if not pipeline_steps:
                print(f"[WorkflowEngine] Error: No workflow steps found for Workflow ID {workflow_id}")
                raise ValueError(f"No steps defined for workflow {workflow_id}. Ensure the workflow is correctly seeded.")


            for agent, step_doc in pipeline_steps:
                step_id = step_doc['id']
                agent_name = agent.__class__.__name__
                current_state.current_step_name = agent_name
                print(f"[WorkflowEngine] Running step: {agent_name} (Step ID: {step_id})")
                
                # Construct data-driven prompt if step_id exists
                system_instruction = self._construct_prompt_for_step(step_id) if step_id else None
                
                # --- EXECUTE PRE-HOOKS ---
                config = step_doc.get('execution_config') or {}
                pre_hooks = config.get('pre_hooks') or []
                for hook_name in pre_hooks:
                    current_state = self._execute_hook(hook_name, agent, current_state)

                # Execute agent (updates state internally)
                current_state = agent.execute(current_state, system_instruction=system_instruction)

                # --- EXECUTE POST-HOOKS ---
                post_hooks = config.get('post_hooks') or []
                for hook_name in post_hooks:
                    current_state = self._execute_hook(hook_name, agent, current_state)

                # Update DB with progress
                self.executions_table.update({
                    'current_step': agent_name,
                    'last_updated': datetime.now().isoformat()
                }, Execution.execution_id == execution_id)

            # 3. Success
            print(f"[WorkflowEngine] Execution {execution_id} completed successfully.")
            
            # Prepare result with flattened fields
            final_result = current_state.model_dump(mode='json')
            
            # Flatten/Hoist XAI Report fields for easier client access
            if final_result.get('step_9_reporter'):
                report = final_result['step_9_reporter']
                final_result['executive_summary'] = report.get('executive_summary')
                final_result['final_verdict'] = report.get('final_verdict')
                final_result['confidence_score'] = report.get('confidence_score')
                # We also hoist the detailed analysis for direct access
                final_result['detailed_analysis'] = report.get('detailed_analysis')

            self.executions_table.update({
                'status': 'completed',
                'end_time': datetime.now().isoformat(),
                'result': final_result
            }, Execution.execution_id == execution_id)
            
            return final_result

        except Exception as e:
            print(f"[WorkflowEngine] Pipeline crashed at {current_state.current_step_name}: {e}")
            self.executions_table.update({
                'status': 'failed',
                'error': str(e),
                'failed_step': current_state.current_step_name
            }, Execution.execution_id == execution_id)
            raise e

    def _execute_hook(self, hook_name: str, agent: Any, state: WorkflowState) -> WorkflowState:
        """
        Executes a hook (Agent-method ONLY).
        
        Strict Policy:
        1. Only execute methods defined on the Agent class.
        2. Do NOT execute global hooks that might replace internal logic (e.g. parsers).
        """
        # 1. Agent Method Check
        if hasattr(agent, hook_name):
            print(f"[WorkflowEngine] Executing Hook: {agent.__class__.__name__}.{hook_name}")
            try:
                hook_method = getattr(agent, hook_name)
                return hook_method(state)
            except Exception as e:
                print(f"[WorkflowEngine] Hook {hook_name} failed: {e}")
                return state
        
        # 2. Strict Rejection
        else:
            # We explicitly ignore 'parse_' hooks as they are internal to _update_state
            if hook_name.startswith('parse_'):
                pass # Silent ignore for redundant legacy hooks
            else:
                print(f"[WorkflowEngine] Warning: Hook '{hook_name}' not found on Agent {agent.__class__.__name__}. Skipping.")
            return state

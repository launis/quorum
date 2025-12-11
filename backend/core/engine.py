import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from tinydb import TinyDB, Query
import pkgutil
import importlib
import inspect
import backend.agents

from backend.models.state import WorkflowState, InputData
from backend.config import INITIAL_MODEL
from backend.agents.base import BaseAgent

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
        
        # Initialize Agents (The Pipeline) - Fully Dynamic
        self.agents_map = {}
        
        # 1. Dynamically discover and register Agent classes from backend.agents package
        print(f"[WorkflowEngine] Scanning for agents in {backend.agents.__name__}...")
        
        # Iterate over modules in the backend.agents package
        for module_info in pkgutil.iter_modules(backend.agents.__path__):
            module_name = f"backend.agents.{module_info.name}"
            try:
                module = importlib.import_module(module_name)
                
                # Scan for classes in the module
                for name, obj in inspect.getmembers(module):
                    if (inspect.isclass(obj) and 
                        issubclass(obj, BaseAgent) and 
                        obj is not BaseAgent):
                        
                        try:
                            self.agents_map[name] = obj(model=INITIAL_MODEL)
                            print(f"[WorkflowEngine] Registered agent: {name} (from {module_name})")
                        except Exception as e:
                            print(f"[WorkflowEngine] Failed to initialize {name}: {e}")
                            
            except Exception as e:
                print(f"[WorkflowEngine] Failed to import module {module_name}: {e}")

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
        try:
            # 1. Fetch Step Record
            Step = Query()
            step_record = self.steps_table.search(Step.id == step_id)
            if not step_record:
                return {"error": f"Step {step_id} not found", "preview": "Not Found"}
            
            step_data = step_record[0]
            agent_class = step_data.get('component', 'UnknownAgent')
            
            # 2. Construct Prompt
            prompt = self._construct_prompt_for_step(step_id)
            if not prompt:
                return {"error": f"Could not generate prompt for step {step_id}"}
            
            # 3. Return Structured Data for UI
            preview_data = {
                "agent_class": agent_class,
                "system_instruction": prompt,
                "user_prompt": "Template Logic Not Available" 
            }

            # Try to get the User Prompt Template from the Agent Class
            if agent_class in self.agents_map:
                agent_instance = self.agents_map[agent_class]
                try:
                    preview_data["user_prompt"] = agent_instance.get_user_prompt_template()
                except Exception as e:
                    preview_data["user_prompt"] = f"Error retrieving template: {e}"
            
            return preview_data
        except Exception as e:
            return {"error": str(e)}

    def preview_full_chain_prompts(self, workflow_id: str) -> str:
        try:
            Workflow = Query()
            wf_record = self.workflows_table.search(Workflow.id == workflow_id)
            if not wf_record:
                return f"Error: Workflow {workflow_id} not found."
            
            steps_ids = wf_record[0].get('steps', [])
            full_chain = []
            
            full_chain.append(f"# Workflow: {wf_record[0].get('name', 'Untitled')}")
            full_chain.append(f"ID: {workflow_id}\n")
            
            for i, step_id in enumerate(steps_ids):
                prompt = self._construct_prompt_for_step(step_id)
                
                # Fetch step name/component for header
                Step = Query()
                s_rec = self.steps_table.search(Step.id == step_id)
                step_name = s_rec[0].get('id', step_id) if s_rec else step_id
                component = s_rec[0].get('component', 'Unknown') if s_rec else 'Unknown'
                
                full_chain.append(f"## Step {i+1}: {step_name} ({component})")
                full_chain.append("-" * 40)
                full_chain.append(prompt if prompt else "(No Prompt Configured)")
                full_chain.append("\n" + "="*40 + "\n")
                
            return "\n".join(full_chain)

        except Exception as e:
            return f"Error generating chain preview: {str(e)}"

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
                            
                        # Check/Replace CURRENT_DATE
                        if "{{CURRENT_DATE}}" in content:
                            from datetime import datetime
                            now_str = datetime.now().strftime("%d.%m.%Y")
                            content = content.replace("{{CURRENT_DATE}}", now_str)
                            
                        full_prompt_parts.append(content)
            
            return "\n\n".join(full_prompt_parts)
        except Exception as e:
            print(f"[WorkflowEngine] Error constructing prompt for step {step_id}: {e}")
            return ""

    # --- CORE EXECUTION LOGIC (V2) ---

    async def run_execution(self, execution_id: str, raw_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs the full workflow using the new State-based architecture (Async).
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
                Step = Query()
                for sid in step_ids:
                    s_doc = self.steps_table.search(Step.id == sid)
                    if s_doc:
                        agent_name = s_doc[0].get('component')
                        if agent_name in self.agents_map:
                            pipeline_steps.append((self.agents_map[agent_name], s_doc[0]))
            
            if not pipeline_steps:
                print(f"[WorkflowEngine] Error: No workflow steps found for Workflow ID {workflow_id}")
                raise ValueError(f"No steps defined for workflow {workflow_id}. Ensure the workflow is correctly seeded.")


            for agent, step_doc in pipeline_steps:
                step_id = step_doc['id']
                agent_name = agent.__class__.__name__
                current_state.current_step_name = agent_name
                print(f"[WorkflowEngine] Running step: {agent_name} (Step ID: {step_id})")
                
                # Construct data-driven prompt
                system_instruction = self._construct_prompt_for_step(step_id) if step_id else None
                
                # --- EXECUTE PRE-HOOKS ---
                config = step_doc.get('execution_config') or {}
                pre_hooks = config.get('pre_hooks') or []
                for hook_name in pre_hooks:
                    current_state = self._execute_hook(hook_name, agent, current_state)

                # Execute agent (ASYNC AWAIT)
                current_state = await agent.execute(current_state, system_instruction=system_instruction)

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
            
            # Capture full state for debugging (could be saved to a separate 'trace' field if needed)
            full_state = current_state.model_dump(mode='json')
            
            # Initialize strictly filtered public result
            public_result = {}
            
            # Dynamic Result Projection (Strict Filtering)
            # We iterate through the steps that were executed and project specific fields
            # based on their configured output components.
            for agent, step_doc in pipeline_steps:
                state_key = step_doc.get('state_key')
                hoist_fields = step_doc.get('hoist_fields', [])
                
                # Check for component-based configuration (Level A)
                output_config_id = step_doc.get('output_config_component')
                if output_config_id:
                    Component = Query()
                    comp_record = self.components_table.search(Component.id == output_config_id)
                    if comp_record:
                        # Merge or override fields from component
                        hoist_fields = comp_record[0].get('content', [])
                
                # Perform Projection
                if state_key and hoist_fields and full_state.get(state_key):
                    source_data = full_state[state_key]
                    print(f"[WorkflowEngine] Projecting {len(hoist_fields)} fields from {state_key}")
                    
                    for field in hoist_fields:
                        # Support dot notation for nested source fields
                        if '.' in field:
                            parts = field.split('.')
                            val = source_data
                            for part in parts:
                                if isinstance(val, dict):
                                    val = val.get(part)
                                else:
                                    val = None
                                    break
                            
                            # Naming Convention: Use the leaf name as the public key
                            # e.g. 'pisteet.analyysi' -> 'analyysi'
                            target_key = parts[-1]
                        else:
                            val = source_data.get(field)
                            target_key = field

                        # Add to public result keys
                        public_result[target_key] = val

            # Update DB with strict result
            self.executions_table.update({
                'status': 'completed',
                'end_time': datetime.now().isoformat(),
                'result': public_result,
                # Save full trace for detailed audit/debugging
                'trace': full_state 
            }, Execution.execution_id == execution_id)
            
            return public_result

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

import importlib
import os
import traceback
from typing import List, Dict, Any, Union
from datetime import datetime
from tinydb import TinyDB, Query
from pydantic import BaseModel
import backend.hooks as hooks

class WorkflowStep(BaseModel):
    component: str
    inputs: Dict[str, Any] = {}

class WorkflowDefinition(BaseModel):
    name: str
    steps: List[WorkflowStep]

class WorkflowEngine:
    """
    Orchestrates the execution of workflows.
    """
    
    def __init__(self, db_path: str):
        self.db = TinyDB(db_path, encoding='utf-8')
        self.components_table = self.db.table('components')
        self.workflows_table = self.db.table('workflows')
        self.executions_table = self.db.table('executions')
        self.steps_table = self.db.table('steps')
        self.rules_table = self.db.table('rules')
        self.prompts_table = self.db.table('prompts')

    def register_component(self, name: str, module_path: str, class_name: str):
        """
        Registers a component in the database.
        """
        self.components_table.upsert(
            {'name': name, 'module': module_path, 'class': class_name},
            Query().name == name
        )

    def create_workflow(self, name: str, steps: List[Dict[str, Any]]) -> int:
        """
        Creates a new workflow definition.
        """
        return self.workflows_table.insert({'name': name, 'steps': steps})

    def _load_component_class(self, component_name: str):
        """
        Dynamically loads the component class based on the registry.
        """
        component_record = self.components_table.get(Query().name == component_name)
        if not component_record:
            raise ValueError(f"Component '{component_name}' not found in registry.")
        
        module = importlib.import_module(component_record['module'])
        return getattr(module, component_record['class'])

    def create_execution(self, workflow_id: str, inputs: Dict[str, Any]) -> int:
        """Creates an execution record and returns its ID."""
        execution_id = self.executions_table.insert({
            'workflow_id': workflow_id,
            'status': 'PENDING',
            'start_time': datetime.now().isoformat(),
            'inputs': inputs,
            'step_results': []
        })
        return execution_id

    def run_execution(self, execution_id: int):
        """Runs the workflow for a given execution ID."""
        try:
            # 1. Fetch execution record
            execution = self.executions_table.get(doc_id=execution_id)
            if not execution:
                raise ValueError(f"Execution {execution_id} not found")
            
            workflow_id = execution['workflow_id']
            inputs = execution['inputs']
            
            # Update status to RUNNING
            self.executions_table.update({'status': 'RUNNING'}, doc_ids=[execution_id])
            
            # 2. Fetch Workflow Definition
            if isinstance(workflow_id, int):
                workflow = self.workflows_table.get(doc_id=workflow_id)
            else:
                workflow = self.workflows_table.get(Query().id == workflow_id)
                
            if not workflow:
                raise ValueError(f"Workflow {workflow_id} not found")

            # 3. Execute Steps
            context = inputs.copy()
            step_results = []
            
            # Robustly get steps
            steps = workflow.get('sequence', [])
            if not steps:
                steps = workflow.get('steps', [])

            for step_id in steps:
                print(f"--- Executing Step: {step_id} ---")
                
                # Update current step in DB for UI tracking
                self.executions_table.update({'current_step': step_id}, doc_ids=[execution_id])
                
                # Get Step Definition
                step_def = self.steps_table.get(Query().id == step_id)
                if not step_def:
                    print(f"Error: Step {step_id} not found")
                    continue

                # Prepare Inputs
                current_inputs = context.copy()
                
                # Get Component Class
                component_map = {
                    "STEP_1_GUARD": "GuardAgent",
                    "STEP_2_ANALYST": "AnalystAgent",
                    "STEP_3_LOGICIAN": "LogicianAgent",
                    "STEP_4_FALSIFIER": "LogicalFalsifierAgent",
                    "STEP_5_CAUSAL": "CausalAnalystAgent",
                    "STEP_6_PERFORMATIVITY": "PerformativityDetectorAgent",
                    "STEP_7_FACT_CHECKER": "FactualOverseerAgent",
                    "STEP_8_JUDGE": "JudgeAgent",
                    "STEP_9_XAI": "XAIReporterAgent",
                    "STEP_CRITICS_PANEL": "PanelAgent",
                }
                
                component_class_name = component_map.get(step_id) or step_def.get('component')
                
                if not component_class_name:
                    print(f"Error: Could not determine component for step {step_id}")
                    continue
                execution_config = step_def.get('execution_config', {})
                
                # Assemble System Instruction
                prompt_ids = execution_config.get('llm_prompts', [])
                system_instruction = ""
                for p_id in prompt_ids:
                    prompt = self.components_table.get(Query().id == p_id)
                    if prompt:
                        content = prompt['content']
                        # Resolve Schema References
                        import re
                        import json
                        import backend.schemas as schemas
                        
                        def replace_schema(match):
                            model_name = match.group(1)
                            if hasattr(schemas, model_name):
                                model_class = getattr(schemas, model_name)
                                schema = model_class.model_json_schema()
                                return json.dumps(schema, indent=2, ensure_ascii=False)
                            else:
                                return f"[SCHEMA ERROR: Model {model_name} not found]"

                        def replace_example(match):
                            model_name = match.group(1)
                            if hasattr(schemas, model_name):
                                model_class = getattr(schemas, model_name)
                                # Pydantic V2: examples are in json_schema_extra
                                config = model_class.model_config
                                extra = config.get('json_schema_extra', {})
                                examples = extra.get('examples', [])
                                if examples:
                                    return json.dumps(examples[0], indent=2, ensure_ascii=False)
                                return f"[EXAMPLE ERROR: No examples found for {model_name}]"
                            else:
                                return f"[EXAMPLE ERROR: Model {model_name} not found]"

                        content = re.sub(r'\[Ks\. schemas\.py / (\w+)\]', replace_schema, content)
                        content = re.sub(r'\[Ks\. schemas\.py / (\w+) / EXAMPLE\]', replace_example, content)
                        system_instruction += f"\n\n{content}"
                
                system_instruction = system_instruction.strip()

                # Instantiate Component
                comp_record = self.components_table.get(Query()['class'] == component_class_name)
                if comp_record:
                    try:
                        ComponentClass = self._load_component_class(comp_record['name'])
                    except Exception as e:
                         print(f"Error loading component {comp_record['name']}: {e}")
                         continue
                else:
                    # Fallback: try to find in agents modules
                    try:
                        if "Guard" in component_class_name: module_name = "backend.agents.guard"
                        elif "Analyst" in component_class_name: module_name = "backend.agents.analyst"
                        elif "Logician" in component_class_name: module_name = "backend.agents.logician"
                        elif "Falsifier" in component_class_name: module_name = "backend.agents.critics"
                        elif "Causal" in component_class_name: module_name = "backend.agents.critics"
                        elif "Performativity" in component_class_name: module_name = "backend.agents.critics"
                        elif "Overseer" in component_class_name: module_name = "backend.agents.critics"
                        elif "Judge" in component_class_name: module_name = "backend.agents.judge"
                        elif "XAI" in component_class_name: module_name = "backend.agents.judge"
                        elif "Panel" in component_class_name: module_name = "backend.agents.panel"
                        else: module_name = "backend.agents.base"
                        
                        module = importlib.import_module(module_name)
                        ComponentClass = getattr(module, component_class_name)
                    except ImportError:
                        print(f"Error: Could not load class {component_class_name}")
                        continue

                # Determine model for this step
                model_mapping = workflow.get('default_model_mapping')
                if model_mapping is None:
                    model_mapping = {}
                
                model_name = model_mapping.get(step_id)
                
                if model_name:
                    print(f"DEBUG: Using model {model_name} for step {step_id}")
                    component_instance = ComponentClass(model=model_name)
                else:
                    print(f"DEBUG: No model mapped for {step_id}, using default.")
                    component_instance = ComponentClass()
                
                print(f"Executing component: {component_class_name}")
                
                # Pass system_instruction to execute/process
                output = component_instance.execute(system_instruction=system_instruction, **current_inputs)
                
                # 4. Execute Post-Hooks
                for hook_name in execution_config.get('post_hooks', []):
                    if hasattr(hooks, hook_name):
                        hook_func = getattr(hooks, hook_name)
                        output = hook_func(current_inputs, output)
                    else:
                        print(f"Warning: Post-hook {hook_name} not found.")

                step_results.append({
                    'step_id': step_id,
                    'output': output
                })

                # Update context with output if it's a dictionary
                if isinstance(output, dict):
                    print(f"DEBUG: Step {step_id} output keys: {list(output.keys())}")
                    context.update(output)
                    print(f"DEBUG: Context keys after update: {list(context.keys())}")
            
            # Update status to completed
            self.executions_table.update(
                {'status': 'COMPLETED', 'result': context, 'step_results': step_results},
                doc_ids=[execution_id]
            )

        except Exception as e:
            print(f"Workflow execution failed: {e}")
            traceback.print_exc()
            self.executions_table.update(
                {'status': 'FAILED', 'error': str(e), 'step_results': []}, 
                doc_ids=[execution_id]
            )
            raise e

    def execute_workflow(self, workflow_id: str, inputs: Dict[str, Any]) -> int:
        """
        Synchronous wrapper for backward compatibility.
        """
        execution_id = self.create_execution(workflow_id, inputs)
        self.run_execution(execution_id)
        return execution_id

    def get_execution_status(self, execution_id: int):
        return self.executions_table.get(doc_id=execution_id)

    def preview_step_prompt(self, step_id: str) -> Dict[str, Any]:
        print(f"DEBUG: preview_step_prompt called for {step_id}", flush=True)
        step_def = self.steps_table.get(Query().id == step_id)
        if not step_def:
            print(f"DEBUG: Step {step_id} not found", flush=True)
            raise ValueError(f"Step {step_id} not found in DB.")

        # 1. Determine Component Class
        component_map = {
            "STEP_1_GUARD": "GuardAgent",
            "STEP_2_ANALYST": "AnalystAgent",
            "STEP_3_LOGICIAN": "LogicianAgent",
            "STEP_4_FALSIFIER": "LogicalFalsifierAgent",
            "STEP_5_CAUSAL": "CausalAnalystAgent",
            "STEP_6_PERFORMATIVITY": "PerformativityDetectorAgent",
            "STEP_7_FACT_CHECKER": "FactualOverseerAgent",
            "STEP_8_JUDGE": "JudgeAgent",
            "STEP_9_XAI": "XAIReporterAgent",
            "STEP_CRITICS_PANEL": "PanelAgent",
        }
        
        component_class_name = component_map.get(step_id) or step_def.get('component')
        print(f"DEBUG: Component class: {component_class_name}", flush=True)
        if not component_class_name:
             # Try to infer from ID if possible, or fail
             if "PANEL" in step_id: component_class_name = "PanelAgent"
             else: return {"error": f"No component mapping for {step_id}"}

        # 2. Get Step Definition
        execution_config = step_def.get('execution_config', {})
        
        # 3. Resolve System Instruction
        prompt_ids = execution_config.get('llm_prompts', [])
        print(f"DEBUG: Prompt IDs: {prompt_ids}", flush=True)
        system_instruction = ""
        for p_id in prompt_ids:
            prompt = self.components_table.get(Query().id == p_id)
            if prompt:
                content = prompt['content']
                # Resolve Schema References
                import re
                import json
                import backend.schemas as schemas
                
                def replace_schema(match):
                    model_name = match.group(1)
                    if hasattr(schemas, model_name):
                        model_class = getattr(schemas, model_name)
                        schema = model_class.model_json_schema()
                        return json.dumps(schema, indent=2, ensure_ascii=False)
                    else:
                        return f"[SCHEMA ERROR: Model {model_name} not found]"

                def replace_example(match):
                    model_name = match.group(1)
                    if hasattr(schemas, model_name):
                        model_class = getattr(schemas, model_name)
                        config = model_class.model_config
                        extra = config.get('json_schema_extra', {})
                        examples = extra.get('examples', [])
                        if examples:
                            return json.dumps(examples[0], indent=2, ensure_ascii=False)
                        return f"[EXAMPLE ERROR: No examples found for {model_name}]"
                    else:
                        return f"[EXAMPLE ERROR: Model {model_name} not found]"

                content = re.sub(r'\[Ks\. schemas\.py / (\w+)\]', replace_schema, content)
                content = re.sub(r'\[Ks\. schemas\.py / (\w+) / EXAMPLE\]', replace_example, content)
                system_instruction += f"\n\n{content}"
        
        # 4. Generate User Prompt (Template)
        mock_inputs = {
            "history_text": "[PLACEHOLDER: CHAT HISTORY]",
            "product_text": "[PLACEHOLDER: PRODUCT TEXT]",
            "reflection_text": "[PLACEHOLDER: REFLECTION TEXT]",
            "tainted_data": {"data": "...", "metadata": "..."},
            "todistuskartta": {"hypoteesit": [], "rag_todisteet": []},
            "argumentaatioanalyysi": {"toulmin_analyysi": []},
        }
        
        try:
            # Explicit mapping to avoid substring matching errors
            class_to_module = {
                "GuardAgent": "backend.agents.guard",
                "AnalystAgent": "backend.agents.analyst",
                "LogicianAgent": "backend.agents.logician",
                "LogicalFalsifierAgent": "backend.agents.critics",
                "CausalAnalystAgent": "backend.agents.critics",
                "PerformativityDetectorAgent": "backend.agents.critics",
                "FactualOverseerAgent": "backend.agents.critics",
                "JudgeAgent": "backend.agents.judge",
                "XAIReporterAgent": "backend.agents.judge",
                "PanelAgent": "backend.agents.panel"
            }
            
            module_name = class_to_module.get(component_class_name, "backend.agents.base")
            
            module = importlib.import_module(module_name)
            ComponentClass = getattr(module, component_class_name)
            agent_instance = ComponentClass()
            
            # Prepare inputs based on agent requirements to avoid potential crashes with unused complex types
            if "Guard" in component_class_name:
                # GuardAgent only needs strings
                agent_inputs = {k: v for k, v in mock_inputs.items() if isinstance(v, str)}
            else:
                agent_inputs = mock_inputs

            if hasattr(agent_instance, 'construct_user_prompt'):
                user_prompt = agent_instance.construct_user_prompt(**agent_inputs)
            else:
                user_prompt = "[ERROR: Agent does not support prompt preview (missing construct_user_prompt)]"
                
        except Exception as e:
            print(f"DEBUG: Exception in preview: {e}", flush=True)
            traceback.print_exc()
            user_prompt = f"[ERROR generating user prompt: {str(e)}]"

        return {
            "step_id": step_id,
            "agent_class": component_class_name,
            "system_instruction": system_instruction.strip(),
            "user_prompt": user_prompt
        }

    def preview_full_chain_prompts(self, workflow_id: str) -> str:
        """
        Generates a concatenated string of all prompts in the workflow.
        """
        # Get workflow
        if isinstance(workflow_id, int):
             # This might happen if passed as int, but usually string ID in DB
             # Let's assume we search by 'id' string first
             workflow = self.workflows_table.get(Query().id == str(workflow_id))
        else:
             workflow = self.workflows_table.get(Query().id == workflow_id)
             
        if not workflow:
             # Try searching by doc_id if it's an int-like string?
             # Or just return error
             return f"Error: Workflow {workflow_id} not found."

        # Workflow structure uses 'sequence' which is a list of step IDs
        step_ids = workflow.get('sequence', [])
        if not step_ids and 'steps' in workflow:
            # Fallback if structure changes
            step_ids = [s['id'] for s in workflow['steps']]
        
        full_chain_text = f"=== FULL CHAIN PROMPT PREVIEW FOR WORKFLOW: {workflow.get('name', workflow_id)} ===\n\n"
        
        for step_id in step_ids:
            preview = self.preview_step_prompt(step_id)
            
            full_chain_text += f"################################################################################\n"
            full_chain_text += f"### STEP: {step_id} ({preview.get('agent_class', 'Unknown Agent')})\n"
            full_chain_text += f"################################################################################\n\n"
            
            full_chain_text += f"--- SYSTEM INSTRUCTION ---\n"
            full_chain_text += f"{preview.get('system_instruction', '')}\n\n"
            
            full_chain_text += f"--- USER PROMPT (TEMPLATE) ---\n"
            full_chain_text += f"{preview.get('user_prompt', '')}\n\n"
            
            full_chain_text += f"\n\n"
            
        return full_chain_text

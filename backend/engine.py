import importlib
from typing import List, Dict, Any, Union
from tinydb import TinyDB, Query
from pydantic import BaseModel

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
        self.db = TinyDB(db_path)
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

    def _resolve_references(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolves references to Rules and Prompts in the inputs.
        Keys ending in '_ref' or '_refs' are resolved.
        """
        resolved = inputs.copy()
        
        for key, value in inputs.items():
            # Resolve Rule References (List)
            if key.endswith('_refs') and isinstance(value, list):
                resolved_rules = []
                for rule_id in value:
                    rule = self.rules_table.get(Query().id == rule_id)
                    if rule:
                        resolved_rules.append(rule['content'])
                    else:
                        print(f"Warning: Rule ID {rule_id} not found.")
                
                # Replace 'rule_refs' with 'rules' (or whatever the prefix is)
                new_key = key.replace('_refs', 's') # e.g., rule_refs -> rules
                resolved[new_key] = resolved_rules
            
            # Resolve Prompt Reference (Single)
            elif key.endswith('_ref') and isinstance(value, str):
                prompt = self.prompts_table.get(Query().id == value)
                if prompt:
                    # Replace 'prompt_ref' with 'system_instruction' or similar
                    # For now, let's map prompt_ref -> system_instruction if it's a system prompt
                    # or just resolve the content.
                    new_key = key.replace('_ref', '') # e.g., prompt_ref -> prompt
                    resolved[new_key] = prompt['content']
                else:
                    print(f"Warning: Prompt ID {value} not found.")

        return resolved

    def execute_workflow(self, workflow_id: Union[int, str], initial_inputs: Dict[str, Any] = {}) -> int:
        """
        Executes a workflow by ID (string) or doc_id (int).
        """
        if isinstance(workflow_id, int):
            workflow = self.workflows_table.get(doc_id=workflow_id)
        else:
            workflow = self.workflows_table.get(Query().id == workflow_id)
            
        if not workflow:
            raise ValueError(f"Workflow ID {workflow_id} not found.")

        execution_id = self.executions_table.insert({
            'workflow_id': workflow_id,
            'status': 'running',
            'step_results': [],
            'initial_inputs': initial_inputs
        })

        context = initial_inputs.copy()
        step_results = []

        try:
            step_ids = workflow.get('sequence', [])
            if not step_ids and 'steps' in workflow:
                 # Legacy support or if create_workflow was used
                 step_ids = [s['id'] for s in workflow['steps']]

            for step_id in step_ids:
                step_def = self.steps_table.get(Query().id == step_id)
                if not step_def:
                    raise ValueError(f"Step {step_id} not found in DB.")
                
                # Determine component class based on step ID or description?
                # In seed_data, steps don't explicitly say "component class".
                # But the ID usually implies it (STEP_1_GUARD -> GuardAgent).
                # We need a mapping or convention.
                # Let's assume a mapping exists or we infer it.
                # For now, let's map manually or use a registry lookup if possible.
                # The current engine uses 'component' field in step.
                # Let's add 'component' to the step definition in DB or infer it.
                # In seed_data.json, steps have 'id', 'description', 'execution_config'.
                # They DO NOT have 'component'.
                # However, the workflow has 'default_model_mapping'.
                # We need to map Step ID to Component Class.
                # Let's infer from ID: STEP_1_GUARD -> GuardAgent.
                
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
                    "STEP_ALL_CRITICS": "CriticGroup" # Special case
                }
                
                component_class_name = component_map.get(step_id)
                if not component_class_name:
                     print(f"Warning: No component mapping for {step_id}")
                     continue

                execution_config = step_def.get('execution_config', {})

                # 1. Assemble System Instruction (Prompts)
                prompt_ids = execution_config.get('llm_prompts', [])
                system_instruction = ""
                for p_id in prompt_ids:
                    prompt = self.components_table.get(Query().id == p_id)
                    if prompt:
                        content = prompt['content']
                        # Resolve Schema References
                        # Pattern: [Ks. schemas.py / ModelName]
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

                        content = re.sub(r'\[Ks\. schemas\.py / (\w+)\]', replace_schema, content)
                        system_instruction += f"\n\n{content}"
                
                # 2. Execute Pre-Hooks
                import backend.hooks as hooks
                current_inputs = context.copy()
                for hook_name in execution_config.get('pre_hooks', []):
                    if hasattr(hooks, hook_name):
                        hook_func = getattr(hooks, hook_name)
                        current_inputs = hook_func(current_inputs)
                    else:
                        print(f"Warning: Pre-hook {hook_name} not found.")

                # 3. Load and Execute Component
                # We need to find the module for the class.
                # Assuming standard location backend.agents.*
                # We can try to find it in the registry or guess.
                # The registry has 'name', 'module', 'class'.
                # Let's try to find by class name in registry.
                comp_record = self.components_table.get(Query()['class'] == component_class_name)
                if comp_record:
                    ComponentClass = self._load_component_class(comp_record['name'])
                else:
                    # Fallback: try to find in agents modules
                    # This is a bit hacky, but robust for now.
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
                        else: module_name = "backend.agents.base"
                        
                        module = importlib.import_module(module_name)
                        ComponentClass = getattr(module, component_class_name)
                    except ImportError:
                        print(f"Error: Could not load class {component_class_name}")
                        continue

                component_instance = ComponentClass()
                
                print(f"Executing component: {component_class_name}")
                
                # Pass system_instruction to execute/process
                # We pass it as a kwarg.
                output = component_instance.execute(system_instruction=system_instruction, **current_inputs)
                
                # 4. Execute Post-Hooks
                for hook_name in execution_config.get('post_hooks', []):
                    if hasattr(hooks, hook_name):
                        hook_func = getattr(hooks, hook_name)
                        # Post-hooks might take inputs AND output
                        output = hook_func(current_inputs, output)
                    else:
                        print(f"Warning: Post-hook {hook_name} not found.")

                step_results.append({
                    'step_id': step_id,
                    'output': output
                })

                # Update context with output if it's a dictionary
                if isinstance(output, dict):
                    context.update(output)
            
        except Exception as e:
            print(f"Workflow execution failed: {e}")
            self.executions_table.update(
                {'status': 'failed', 'error': str(e), 'step_results': step_results},
                doc_ids=[execution_id]
            )
            raise e

        return execution_id

    def get_execution_status(self, execution_id: int):
        return self.executions_table.get(doc_id=execution_id)

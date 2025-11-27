import importlib
from typing import List, Dict, Any
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

    def execute_workflow(self, workflow_id: int, initial_inputs: Dict[str, Any] = {}) -> int:
        """
        Executes a workflow by ID.
        """
        workflow = self.workflows_table.get(doc_id=workflow_id)
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
            for step in workflow['steps']:
                component_name = step['component']
                step_inputs = step.get('inputs', {})
                
                # 1. Variable Substitution
                substituted_inputs = {}
                for k, v in step_inputs.items():
                    if isinstance(v, str) and v.startswith('$'):
                        var_name = v[1:]
                        if var_name in context:
                            substituted_inputs[k] = context[var_name]
                        else:
                            substituted_inputs[k] = None 
                    else:
                        substituted_inputs[k] = v
                
                # 2. Reference Resolution (Rules/Prompts)
                final_inputs = self._resolve_references(substituted_inputs)
                
                ComponentClass = self._load_component_class(component_name)
                component_instance = ComponentClass()
                
                print(f"Executing component: {component_name}")
                output = component_instance.execute(**final_inputs)
                
                step_result = {
                    'component': component_name,
                    'inputs': final_inputs,
                    'output': output
                }
                step_results.append(step_result)
                
                # Update context with outputs
                if isinstance(output, dict):
                    context.update(output)

            self.executions_table.update(
                {'status': 'completed', 'step_results': step_results, 'final_context': context},
                doc_ids=[execution_id]
            )
            
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

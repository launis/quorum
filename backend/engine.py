import importlib
import os
import traceback
from typing import List, Dict, Any, Union
from datetime import datetime
from tinydb import TinyDB, Query
from pydantic import BaseModel
import backend.hooks as hooks
import json
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

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
    
    def __init__(self, db_path: str = None):
        from backend.config import DB_PATH
        
        if db_path:
            self.db_path = db_path
        else:
            self.db_path = DB_PATH

        print(f"[WorkflowEngine] Using Database at: {self.db_path}")

        self.db = TinyDB(self.db_path, encoding='utf-8')
        self.components_table = self.db.table('components')
        self.workflows_table = self.db.table('workflows')
        self.executions_table = self.db.table('executions')
        self.steps_table = self.db.table('steps')
        self.rules_table = self.db.table('rules')
        self.prompts_table = self.db.table('prompts')
        self.banned_phrases_table = self.db.table('banned_phrases')

    def simplify_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simplifies a JSON Schema for LLM consumption by removing Pydantic-specific metadata
        and flattening structures where possible.
        """
        if not isinstance(schema, dict):
            return schema
            
        # Remove metadata keys that add noise
        keys_to_remove = ['title', 'description', 'default', 'examples'] 
        # Note: We keep 'description' if it's meaningful, but Pydantic often adds redundant titles.
        # Let's keep description for fields but remove title.
        
        new_schema = {}
        for k, v in schema.items():
            if k == 'title':
                continue
            if k == '$defs':
                # Recursively simplify definitions
                new_schema[k] = {dk: self.simplify_schema(dv) for dk, dv in v.items()}
                continue
            if isinstance(v, dict):
                new_schema[k] = self.simplify_schema(v)
            elif isinstance(v, list):
                new_schema[k] = [self.simplify_schema(i) if isinstance(i, dict) else i for i in v]
            else:
                new_schema[k] = v
                
        return new_schema

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
            collected_citations = set() # Track unique citations
            
            # Robustly get steps
            steps = workflow.get('sequence') or workflow.get('steps') or []

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
                
                # Get Component Class Name
                component_class_name = step_def.get('component')
                
                if not component_class_name:
                    print(f"Error: Could not determine component for step {step_id}")
                    continue
                execution_config = step_def.get('execution_config') or {}
                
                # Assemble System Instruction
                prompt_ids = execution_config.get('llm_prompts') or []
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
                        
                        # Inject Citation if present
                        if prompt.get('citation'):
                            citation_text = prompt.get('citation')
                            content += f"\n[Lähde: {citation_text}]"
                            
                            # Use full citation for bibliography if available, else short
                            bib_entry = prompt.get('citation_full') or citation_text
                            collected_citations.add(bib_entry)
                            
                        system_instruction += f"\n\n{content}"
                
                system_instruction = system_instruction.strip()

                # Inject Custom Instruction (Ad-Hoc)
                if execution_config.get('custom_instruction'):
                    custom_instr = execution_config.get('custom_instruction')
                    system_instruction += f"\n\n[MUKAUTETTU OHJEISTUS]:\n{custom_instr}"

                # Inject Step-Level Citation (Ad-Hoc)
                if execution_config.get('citation'):
                    citation_text = execution_config.get('citation')
                    system_instruction += f"\n\n[Lähde: {citation_text}]"
                    
                    bib_entry = execution_config.get('citation_full') or citation_text
                    collected_citations.add(bib_entry)

                # Instantiate Component
                # 1. Try to find by class name in components table (preferred)
                comp_record = self.components_table.get(Query()['class'] == component_class_name)
                
                # 2. If not found by class, try by name (fallback for older configs)
                if not comp_record:
                     comp_record = self.components_table.get(Query()['name'] == component_class_name)

                if comp_record and 'module' in comp_record and 'class' in comp_record:
                    try:
                        module = importlib.import_module(comp_record['module'])
                        ComponentClass = getattr(module, comp_record['class'])
                    except Exception as e:
                         print(f"Error loading component {comp_record['name']} from {comp_record['module']}: {e}")
                         continue
                else:
                    print(f"Error: Component definition not found for class '{component_class_name}'. Ensure it is registered in 'components' table with 'module' and 'class'.")
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
                
                # Special handling for XAI Reporter: Pass bibliography
                if "XAI" in component_class_name or "Reporter" in component_class_name:
                    current_inputs['bibliography_context'] = list(collected_citations)

                # Resolve Output Schema Class dynamically
                output_schema_name = step_def.get('output_schema')
                validation_schema_class = None

                if output_schema_name:
                    import backend.schemas as schemas
                    # Check if the schema exists in your Pydantic definitions
                    if hasattr(schemas, output_schema_name):
                        validation_schema_class = getattr(schemas, output_schema_name)
                    else:
                        print(f"Warning: Output schema '{output_schema_name}' defined in step but not found in backend.schemas.")

                # --- SCHEMA INJECTION ---
                # If an output schema is defined, explicitly inject its definition into the System Instruction.
                # This ensures the LLM knows exactly what structure to produce, regardless of prompt placeholders.
                if validation_schema_class:
                    try:
                        raw_schema = validation_schema_class.model_json_schema()
                        simplified_schema = self.simplify_schema(raw_schema)
                        schema_json = json.dumps(simplified_schema, indent=2, ensure_ascii=False)
                        
                        schema_instruction = (
                            f"\n\n*** REQUIRED OUTPUT SCHEMA ({output_schema_name}) ***\n"
                            f"You MUST output a valid JSON object that strictly adheres to the following schema:\n"
                            f"```json\n{schema_json}\n```\n"
                        )
                        
                        # Inject Example if available in ConfigDict
                        config = validation_schema_class.model_config
                        extra = config.get('json_schema_extra', {})
                        examples = extra.get('examples', [])
                        if examples:
                            example_json = json.dumps(examples[0], indent=2, ensure_ascii=False)
                            schema_instruction += (
                                f"\n*** EXAMPLE OUTPUT ***\n"
                                f"```json\n{example_json}\n```\n"
                            )
                        
                        schema_instruction += "Do not include any other text."
                        
                        system_instruction += schema_instruction
                        print(f"   [Engine] Injected schema definition for: {output_schema_name}")
                    except Exception as e:
                        print(f"   [Engine] Error injecting schema definition: {e}")
                # ------------------------
                # ------------------------
                
                # --- Static Inputs Injection ---
                static_input_ids = execution_config.get('static_inputs') or []
                for s_id in static_input_ids:
                    comp = self.components_table.get(Query().id == s_id)
                    if comp:
                        # Inject into current_inputs
                        # Use lowercase ID as key: "DISCLAIMER_TEXT" -> "disclaimer_text"
                        key = s_id.lower()
                        current_inputs[key] = comp.get('content', '')
                        print(f"   [Engine] Injected static input: {key}")
                # -------------------------------

                # Execute Pre-Hooks
                for hook_name in (execution_config.get('pre_hooks') or []):
                    if hasattr(hooks, hook_name):
                        print(f"Executing pre-hook: {hook_name}")
                        hook_func = getattr(hooks, hook_name)
                        current_inputs = hook_func(current_inputs)
                    else:
                        print(f"Warning: Pre-hook {hook_name} not found.")

                # --- DEBUG LOGGING ---
                # Preview the prompt for debugging purposes
                try:
                    debug_prompt = component_instance.construct_user_prompt(**current_inputs)
                    print(f"\n--- [DEBUG] STEP: {step_id} ---")
                    print(f"--- [DEBUG] SYSTEM INSTRUCTION (First 500 chars) ---\n{system_instruction[:500]}...\n--- [DEBUG] END SYSTEM INSTRUCTION ---")
                    print(f"--- [DEBUG] USER PROMPT (Last 500 chars) ---\n...{debug_prompt[-500:]}\n--- [DEBUG] END USER PROMPT ---")
                except Exception as e:
                    print(f"--- [DEBUG] Could not preview prompt: {e}")
                # ---------------------

                output = component_instance.execute(
                    system_instruction=system_instruction, 
                    validation_schema=validation_schema_class,
                    **current_inputs
                )
                
                print(f"--- [DEBUG] RAW RESULT (First 500 chars) ---\n{str(output)[:500]}...\n--- [DEBUG] END RAW RESULT ---")
                
                # 4. Execute Post-Hooks
                # Automatic Parsing Hook: Check if a parser exists for this component/step
                # Convention: parse_{component_snake_case}_output
                # e.g. parse_analyst_agent_output or parse_analyst_output
                
                # Try to map component class to hook name
                # GuardAgent -> parse_guard_output (if exists)
                # AnalystAgent -> parse_analyst_output
                
                # Helper to convert CamelCase to snake_case
                import re
                s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', component_class_name)
                snake_name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
                # Remove _agent suffix if present
                if snake_name.endswith('_agent'):
                    snake_name = snake_name[:-6]
                    
                parser_hook_name = f"parse_{snake_name}_output"
                
                if hasattr(hooks, parser_hook_name):
                    print(f"Executing implicit parser hook: {parser_hook_name}")
                    hook_func = getattr(hooks, parser_hook_name)
                    output = hook_func(current_inputs, output)

                # Explicit Post-Hooks from Config
                for hook_name in (execution_config.get('post_hooks') or []):
                    if hasattr(hooks, hook_name):
                        print(f"Executing post-hook: {hook_name}")
                        hook_func = getattr(hooks, hook_name)
                        output = hook_func(current_inputs, output)
                    else:
                        print(f"Warning: Post-hook {hook_name} not found.")

                step_results.append({
                    'step_id': step_id,
                    'output': output
                })

                # Update context with output
                # NEW LOGIC: Use output_filename from step definition if available
                output_filename = step_def.get('output_filename')
                
                if output_filename:
                    print(f"[DEBUG] Saving step output to context as '{output_filename}'")
                    # If output is a dict (JSON), save it directly
                    if isinstance(output, dict):
                        print(f"   [DEBUG] Output is dict with keys: {list(output.keys())}")
                        context[output_filename] = output
                    # If output is a Pydantic model (from structured output), dump to dict
                    elif hasattr(output, 'model_dump'):
                        print(f"   [DEBUG] Output is Pydantic model, dumping to dict.")
                        context[output_filename] = output.model_dump()
                    else:
                        # Fallback for strings or other types
                        print(f"   [DEBUG] Output is raw type: {type(output)}")
                        context[output_filename] = output
                    
                    # Verify save
                    if output_filename in context:
                        print(f"   [DEBUG] SUCCESS: '{output_filename}' exists in context.")
                    else:
                        print(f"   [DEBUG] ERROR: Failed to save '{output_filename}' to context!")
                
                # Legacy support: Update context with output keys if it's a dictionary
                # This ensures backward compatibility for steps relying on direct key access
                if isinstance(output, dict):
                    print(f"[DEBUG] Merging output keys to global context (Legacy): {list(output.keys())}")
                    context.update(output)
                
                print(f"[DEBUG] Current Context Keys: {list(context.keys())}")
            
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
        @retry(stop=stop_after_attempt(5), wait=wait_fixed(0.2), retry=retry_if_exception_type(json.JSONDecodeError))
        def _get_safe():
            # Force reload of table data to ensure freshness and handle race conditions
            self.executions_table.clear_cache() 
            return self.executions_table.get(doc_id=execution_id)
            
        try:
            return _get_safe()
        except Exception as e:
            print(f"[WorkflowEngine] Error reading execution status after retries: {e}")
            return None

    def preview_step_prompt(self, step_id: str) -> Dict[str, Any]:
        print(f"DEBUG: preview_step_prompt called for {step_id}", flush=True)
        step_def = self.steps_table.get(Query().id == step_id)
        if not step_def:
            print(f"DEBUG: Step {step_id} not found", flush=True)
            raise ValueError(f"Step {step_id} not found in DB.")

        # 1. Determine Component Class
        component_class_name = step_def.get('component')
        print(f"DEBUG: Component class: {component_class_name}", flush=True)
        
        if not component_class_name:
             return {"error": f"No component class defined for step {step_id}"}

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
                
                # Inject Citation if present
                if prompt.get('citation'):
                    content += f"\n[Lähde: {prompt.get('citation')}]"
                    
                system_instruction += f"\n\n{content}"
        
        user_prompt = ""
        try:
            # Instantiate Component Dynamically
            comp_record = self.components_table.get(Query()['class'] == component_class_name)
            
            # Fallback: try by name if class lookup fails
            if not comp_record:
                 comp_record = self.components_table.get(Query()['name'] == component_class_name)

            if comp_record and 'module' in comp_record and 'class' in comp_record:
                module = importlib.import_module(comp_record['module'])
                ComponentClass = getattr(module, comp_record['class'])
                agent_instance = ComponentClass()
            else:
                # Fallback to base agent if not found (or raise error)
                print(f"Warning: Component class {component_class_name} not found in DB. Using BaseAgent for preview.")
                from backend.agents.base import BaseAgent
                agent_instance = BaseAgent()
            
            # Define mock inputs for preview
            mock_inputs = {
                "history_text": "[PLACEHOLDER: Chat History]",
                "product_text": "[PLACEHOLDER: Final Product]",
                "reflection_text": "[PLACEHOLDER: Reflection Document]",
                "tainted_data": {},
                "evidence_map": {},
                "argument_analysis": {},
                "logical_errors": {},
                "causal_analysis": {},
                "performativity_analysis": {},
                "fact_check_report": {},
                "bibliography_context": []
            }
            
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

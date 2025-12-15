import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from datetime import datetime
from typing import Dict, Any, List, Optional
import pkgutil
import importlib
import inspect
import backend.agents

from backend.models.state import WorkflowState, InputData
from backend.config import INITIAL_MODEL
from backend.agents.base import BaseAgent
from backend.services.agent_registry import AgentRegistry
from backend.services.prompt_builder import PromptBuilder
import logging

from datetime import datetime
import logging
from backend.services.agent_registry import AgentRegistry
from backend.services.prompt_builder import PromptBuilder
from backend.models.state import WorkflowState
from backend.database.repository import WorkflowRepository
from backend.exceptions import (
    WorkflowNotFoundError, 
    ExecutionNotFoundError, 
    AgentExecutionError, 
    StepNotFoundError,
    AppException
)
from backend.context import set_execution_context, clear_execution_context

logger = logging.getLogger(__name__)

class WorkflowEngine:
    def __init__(
        self, 
        db_path: str, 
        repository: Optional[Any] = None, 
        registry: Optional[AgentRegistry] = None,
        prompt_builder: Optional[PromptBuilder] = None,
        db_client: Optional[Any] = None
    ):
        self.db_path = db_path
        
        # Repository Injection (Preferred)
        if repository:
            self.repository = repository
        else:
             from backend.database.wrapper import get_db_client
             from backend.database.repository import WorkflowRepository
             client = db_client if db_client else get_db_client()
             self.repository = WorkflowRepository(client)
        
        # Service Injection
        if registry:
            self.registry = registry
        else:
            # Fallback for manual instantiation
            self.registry = AgentRegistry(self.repository)
            self.registry.discover_and_register_agents()

        if prompt_builder:
            self.prompt_builder = prompt_builder
        else:
            self.prompt_builder = PromptBuilder(self.repository, self.registry)
        
        # Agents Map is now in Registry
        # self.agents_map = {} # Removed
        
        # 1. Dynamically discover and register Agent classes from backend.agents package
        
        # 1. Dynamically discover and register Agent classes is now handled by AgentRegistry
        if not registry: 
             # Only if we created the registry ourselves (fallback), ensuring it's scanned
             # But AgentRegistry(repo) already did call discover_and_register_agents() above?
             # Yes: see lines 60-61.
             pass
             
        logger.info(f"[WorkflowEngine] initialized with DB at {db_path}")

    # --- DELEGATED METHODS (Services) ---
    def resolve_model_name(self, model_identifier: str) -> str:
        return self.registry.resolve_model_name(model_identifier)





    def create_workflow(self, name: str, steps: List[Dict[str, Any]]) -> int:
        """
        Creates a new workflow definition.
        """
        workflow_id = self.repository.create_workflow({
            "name": name,
            "steps": steps,
            "created_at": datetime.now().isoformat()
        })
        return workflow_id

    async def create_execution(self, workflow_id: Any, inputs: Dict[str, Any], files: Optional[Dict[str, tuple]] = None) -> str:
        """
        Creates a new execution record.
        Supports optional file attachments (Multipart/Form-Data source).
        files: Dict[key, (filename, bytes)]
        """
        execution_id = str(uuid.uuid4())
        
        # Merge basic inputs
        final_inputs = inputs.copy()

        # Handle Files (Extract & Archive)
        if files:
            file_updates = await self._ingest_files(execution_id, files)
            final_inputs.update(file_updates)

        self.repository.create_execution({
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "status": "pending",
            "start_time": datetime.now().isoformat(),
            "inputs": final_inputs,
            "logs": []
        })
        return execution_id

    async def _ingest_files(self, execution_id: str, files: Dict[str, tuple]) -> Dict[str, str]:
        """
        Archives files to storage (if enabled) and extracts text.
        Returns dictionary of {input_key: extracted_text}
        files format: { "input_key": ("filename.ext", b"file_bytes") }
        """
        import os
        from backend.services.document_processor import DocumentProcessor
        from backend.services.storage import get_storage_client
        from fastapi.concurrency import run_in_threadpool
        
        extracted_data = {}
        storage_client = get_storage_client()
        
        for input_key, (filename, file_bytes) in files.items():
            try:
                # 1. Extract Text (Offload to Threadpool for CPU-bound tasks)
                lower_name = filename.lower()
                text = ""
                if lower_name.endswith(".pdf"):
                    # Use run_in_threadpool but handle potential errors
                    try:
                        text = await run_in_threadpool(DocumentProcessor.extract_text_from_pdf, file_bytes)
                    except Exception as e:
                         # Fallback or re-raise? Logging is enough for ingestion partial failure
                         logger.error(f"PDF extraction failed for {filename}: {e}")
                         text = f"[Error extracting PDF: {e}]"

                elif lower_name.endswith(".docx"):
                    try:
                        text = await run_in_threadpool(DocumentProcessor.extract_text_from_docx, file_bytes)
                    except Exception as e:
                         logger.error(f"DOCX extraction failed for {filename}: {e}")
                         text = f"[Error extracting DOCX: {e}]"
                else:
                    # Treat as text file (fast enough)
                    text = file_bytes.decode('utf-8', errors='ignore')

                extracted_data[input_key] = text
                
                # 2. Save to Storage (Offload to Threadpool for I/O-bound tasks)
                # LocalStorage expects path relative to its base (backend/files/executions)
                relative_path = f"{execution_id}/{filename}"
                saved_path = await run_in_threadpool(storage_client.save, relative_path, file_bytes)
                
                logger.info(f"[WorkflowEngine] File {filename} processed. Extracted {len(text)} chars. Storage: {saved_path}")
                
            except Exception as e:
                logger.error(f"[WorkflowEngine] Failed to ingest file {filename} ({input_key}): {e}")
                extracted_data[input_key] = f"Error processing file: {str(e)}"
                
        return extracted_data

    def get_execution_status(self, execution_id: Any) -> Optional[Dict[str, Any]]:
        """
        Retrieves execution status.
        """
        exec_data = self.repository.get_execution(str(execution_id))
        if not exec_data:
            raise ExecutionNotFoundError(str(execution_id))
        return exec_data

    def preview_step_prompt(self, step_id: str) -> Dict[str, Any]:
        try:
            # 1. Fetch Step Record
            step_data = self.repository.get_step_by_id(step_id)
            if not step_data:
                return {"error": f"Step {step_id} not found", "preview": "Not Found"}
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
            wf_record = self.repository.get_workflow_by_id(workflow_id)
            if not wf_record:
                return f"Error: Workflow {workflow_id} not found."
            
            steps_ids = wf_record.get('steps', [])
            full_chain = []
            
            full_chain.append(f"# Workflow: {wf_record.get('name', 'Untitled')}")
            full_chain.append(f"ID: {workflow_id}\n")
            
            for i, step_id in enumerate(steps_ids):
                prompt = self._construct_prompt_for_step(step_id)
                
                # Fetch step name/component for header
                # Fetch step name/component for header
                s_rec = self.repository.get_step_by_id(step_id)
                step_name = s_rec.get('id', step_id) if s_rec else step_id
                component = s_rec.get('component', 'Unknown') if s_rec else 'Unknown'
                
                full_chain.append(f"## Step {i+1}: {step_name} ({component})")
                full_chain.append("-" * 40)
                full_chain.append(prompt if prompt else "(No Prompt Configured)")
                full_chain.append("\n" + "="*40 + "\n")
                
            return "\n".join(full_chain)

        except Exception as e:
            return f"Error generating chain preview: {str(e)}"

    def _construct_prompt_for_step(self, step_id: str, current_state: Optional[WorkflowState] = None) -> str:
        """
        Fetches the step configuration and constructs the full system prompt
        by concatenating the content of all referenced prompt components.
        Also inspects for placeholders like {{BANNED_PHRASES}} and state variables.
        """
    def preview_step_prompt(self, step_id: str) -> Dict[str, Any]:
        return self.prompt_builder.preview_step_prompt(step_id)

    def preview_full_chain_prompts(self, workflow_id: str) -> str:
        return self.prompt_builder.preview_full_chain_prompts(workflow_id)

    def _construct_prompt_for_step(self, step_id: str, current_state: Optional[WorkflowState] = None) -> str:
        return self.prompt_builder.construct_prompt(step_id, current_state)

    # --- CORE EXECUTION LOGIC (V2) ---

    async def run_execution(self, execution_id: str, raw_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs the full workflow using the new State-based architecture (Async).
        """
        set_execution_context(execution_id)
        
        logger.info(f"[WorkflowEngine] Starting execution {execution_id}")
        
        # Update status to running
        self.repository.update_execution(execution_id, {'status': 'running'})
        
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
            logger.debug(f"[WorkflowEngine] State initialized with inputs: {raw_inputs.keys()}")
        except Exception as e:
            logger.error(f"[WorkflowEngine] Failed to initialize state: {e}")
            self.repository.update_execution(execution_id, {'status': 'failed', 'error': str(e)})
            clear_execution_context()
            raise e

        # 2. Execute Pipeline
        try:
            # Fetch Workflow Definition
            exec_record = self.repository.get_execution(execution_id)
            if not exec_record:
                 raise ExecutionNotFoundError(execution_id)
            
            workflow_id = exec_record['workflow_id']
            
            # Fetch Workflow Steps
            wf_record = self.repository.get_workflow_by_id(workflow_id)
            
            pipeline_steps = []
            if wf_record:
                step_ids = wf_record['steps']
                for sid in step_ids:
                    s_doc = self.repository.get_step_by_id(sid)
                    if s_doc:
                        agent_name = s_doc.get('component')
                        if agent_name:
                             agent_instance = self.registry.get_agent(agent_name)
                             if agent_instance:
                                 pipeline_steps.append((agent_instance, s_doc))
            
            if not pipeline_steps:
                logger.error(f"[WorkflowEngine] Error: No workflow steps found for Workflow ID {workflow_id}")
                raise ValueError(f"No steps defined for workflow {workflow_id}. Ensure the workflow is correctly seeded.")


            for agent, step_doc in pipeline_steps:
                step_id = step_doc['id']
                agent_name = agent.__class__.__name__
                current_state.current_step_name = agent_name
                logger.info(f"[WorkflowEngine] Running step: {agent_name} (Step ID: {step_id})")
                
                # --- EXECUTE PRE-HOOKS ---
                config = step_doc.get('execution_config') or {}
                pre_hooks = config.get('pre_hooks') or []
                for hook_name in pre_hooks:
                    current_state = self._execute_hook(hook_name, agent, current_state)

                # --- DYNAMIC MODEL SWITCHING (Refactor) ---
                # 1. Get mapping from Workflow Definition
                # (Ideally passed from run_execution inputs or fetched from DB record)
                # Here we fetch it from the workflow definition record we already loaded (wf_record)
                workflow_model_mapping = {}
                if wf_record:
                    workflow_model_mapping = wf_record.get('default_model_mapping', {})

                # 2. Determine Model for this Step
                # Default to 'fast' if not specified (safe fallback)
                step_model_key = workflow_model_mapping.get(step_id, "fast")
                
                # 3. Resolve Strategy to Actual Model Name
                resolved_model_name = self.registry.resolve_model_name(step_model_key)
                
                # 4. Update Agent
                if hasattr(agent, 'set_model'):
                    agent.set_model(resolved_model_name)
                    logger.debug(f"[WorkflowEngine] Method 'set_model' called on {agent_name} -> {resolved_model_name} (Key: {step_model_key})")
                
                # Construct data-driven prompt WITH STATE INJECTION
                # MOVED AFTER PRE-HOOKS to ensure sanitization (e.g. PDF extraction) happens first
                system_instruction = self.prompt_builder.construct_prompt(step_id, current_state) if step_id else None

                # Execute agent (ASYNC AWAIT)
                try:
                    current_state = await agent.execute(current_state, system_instruction=system_instruction)
                except Exception as e:
                    # Wrap Agent Failure
                    raise AgentExecutionError(agent_name, step_id, e)

                # --- EXECUTE POST-HOOKS ---
                post_hooks = config.get('post_hooks') or []
                for hook_name in post_hooks:
                    current_state = self._execute_hook(hook_name, agent, current_state)

                # --- VALIDATION (Dynamic Output Schema) ---
                output_config_id = step_doc.get('output_config_component')
                if output_config_id:
                    comp_record = self.repository.get_component_by_id(output_config_id)
                    if comp_record:
                        required_fields = comp_record.get('content', [])
                        if isinstance(required_fields, list):
                            # Get output from state
                            state_key = step_doc.get('state_key')
                            if state_key and hasattr(current_state, state_key):
                                output_obj = getattr(current_state, state_key)
                                if output_obj:
                                    # Safe dump (BaseJSON allows extra)
                                    output_data = output_obj.model_dump(mode='json')
                                    missing_fields = []
                                    for field in required_fields:
                                        # Handle dot notation for nested fields? 
                                        # Assuming standard top-level or handled by Pydantic alias, 
                                        # but simplistic check:
                                        if "." not in field:
                                            if field not in output_data:
                                                missing_fields.append(field)
                                        # (Optional) Deep check for nested fields could go here
                                    
                                    if missing_fields:
                                        error_msg = f"Validation Failed: Missing required fields in {agent_name} output: {missing_fields}"
                                        logger.error(f"[WorkflowEngine] {error_msg}")
                                        # Strict Mode: Raise Error
                                        raise AgentExecutionError(agent_name, step_id, ValueError(error_msg))
                
                # Update DB with progress
                self.repository.update_execution(execution_id, {
                    'current_step': agent_name,
                    'last_updated': datetime.now().isoformat()
                })

                # --- KILL SWITCH (Security Gate) ---
                # Check data, not agent name (Robustness Fix)
                if current_state.step_guard and current_state.step_guard.security_check.uhka_havaittu:
                    msg = f"[WorkflowEngine] SECURITY INTERVENTION: Threat detected by GuardAgent. Aborting execution {execution_id}."
                    logger.critical(msg)
                    
                    # 1. Update DB as Rejected/Failed
                    rejection_details = {
                        "security_alert": "Execution aborted due to security violation.",
                        "risk_level": current_state.step_guard.security_check.riski_taso,
                        "analysis": current_state.step_guard.security_check.adversariaalinen_simulaatio_tulos,
                        "guard_data": current_state.step_guard.model_dump()
                    }
                    
                    self.repository.update_execution(execution_id, {
                        'status': 'rejected',
                        'error': f"Security Threat Detected: {current_state.step_guard.security_check.riski_taso}",
                        'end_time': datetime.now().isoformat(),
                        'result': rejection_details
                    })

                    # 2. Halt Pipeline
                    return {"security_alert": "Execution aborted due to security violation."}


            # 3. Success
            logger.info(f"[WorkflowEngine] Execution {execution_id} completed successfully.")
            
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
                    comp_record = self.repository.get_component_by_id(output_config_id)
                    if comp_record:
                        # Merge or override fields from component
                        hoist_fields = comp_record.get('content', [])
                
                # Perform Projection
                if state_key and hoist_fields and full_state.get(state_key):
                    source_data = full_state[state_key]
                    logger.debug(f"[WorkflowEngine] Projecting {len(hoist_fields)} fields from {state_key}")
                    
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
            # Update DB with strict result
            self.repository.update_execution(execution_id, {
                'status': 'completed',
                'end_time': datetime.now().isoformat(),
                'result': public_result,
                # Save full trace for detailed audit/debugging
                'trace': full_state 
            })
            
            return public_result

        except AgentExecutionError as ae:
            # Specific handling for Agent failures
            logger.error(f"[WorkflowEngine] Agent Execution Error: {ae.message}")
            self.repository.update_execution(execution_id, {
                'status': 'failed',
                'error': ae.message,
                'end_time': datetime.now().isoformat()
            })

        except Exception as e:
            logger.error(f"[WorkflowEngine] Critical Failure: {e}", exc_info=True)
            self.repository.update_execution(execution_id, {
                'status': 'failed',
                'error': str(e),
                'end_time': datetime.now().isoformat()
            })
        finally:
            clear_execution_context()

    def _execute_hook(self, hook_name: str, agent: Any, state: WorkflowState) -> WorkflowState:
        """
        Executes a hook (Agent-method ONLY).
        
        Strict Policy:
        1. Only execute methods defined on the Agent class.
        2. Do NOT execute global hooks that might replace internal logic (e.g. parsers).
        """
        # 1. Agent Method Check
        if hasattr(agent, hook_name):
            logger.debug(f"[WorkflowEngine] Executing Hook: {agent.__class__.__name__}.{hook_name}")
            try:
                hook_method = getattr(agent, hook_name)
                return hook_method(state)
            except Exception as e:
                logger.error(f"[WorkflowEngine] Hook {hook_name} failed: {e}")
                return state
        
        # 2. Strict Rejection
        else:
            # We explicitly ignore 'parse_' hooks as they are internal to _update_state
            if hook_name.startswith('parse_'):
                pass # Silent ignore for redundant legacy hooks
            else:
                logger.warning(f"[WorkflowEngine] Warning: Hook '{hook_name}' not found on Agent {agent.__class__.__name__}. Skipping.")
            return state

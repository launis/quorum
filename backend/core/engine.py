import uuid
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
from backend.database.repository import AbstractWorkflowRepository
from backend.context import set_execution_context, clear_execution_context

logger = logging.getLogger(__name__)

class WorkflowEngine:
    def __init__(
        self, 
        db_path: str, 
        repository: Optional[AbstractWorkflowRepository] = None, 
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
             from backend.database.repository import TinyDBRepository
             client = db_client if db_client else get_db_client()
             self.repository = TinyDBRepository(client)
        
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
        return self.prompt_builder.preview_step_prompt(step_id)

    def preview_full_chain_prompts(self, workflow_id: str) -> str:
        return self.prompt_builder.preview_full_chain_prompts(workflow_id)

    def _construct_prompt_for_step(self, step_id: str, current_state: Optional[WorkflowState] = None) -> str:
        return self.prompt_builder.construct_prompt(step_id, current_state)

    # --- CORE EXECUTION LOGIC (V2) ---

    async def run_execution(self, execution_id: str, raw_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Runs the full workflow using the new State-based architecture (Async).
        Refactored into modular helper methods for clarity and maintenance.
        """
        set_execution_context(execution_id)
        logger.info(f"[WorkflowEngine] Starting execution {execution_id}")
        self.repository.update_execution(execution_id, {'status': 'running'})
        
        try:
            # 1. Initialize State
            current_state = await self._initialize_execution(execution_id, raw_inputs)
            
            # 2. Execute Pipeline Steps
            # Fetch workflow definition and calculate steps
            exec_record = self.repository.get_execution(execution_id)
            if not exec_record:
                raise ExecutionNotFoundError(execution_id)
            
            workflow_id = exec_record['workflow_id']
            pipeline_steps = self._resolve_pipeline_steps(workflow_id)

            # Execute Steps Serially
            for agent, step_doc in pipeline_steps:
                current_state = await self._execute_step(current_state, agent, step_doc, execution_id)
                # Check for Early Exit (Security)
                if isinstance(current_state, dict) and "security_alert" in current_state:
                     return current_state

            # 3. Success & Result Projection
            logger.info(f"[WorkflowEngine] Execution {execution_id} completed successfully.")
            return self._project_final_result(execution_id, current_state, pipeline_steps)

        except AgentExecutionError as ae:
            self._handle_execution_error(execution_id, ae)
        except Exception as e:
            self._handle_execution_error(execution_id, e)
        finally:
            clear_execution_context()

    # --- HELPER METHODS (Refactoring) ---

    async def _initialize_execution(self, execution_id: str, raw_inputs: Dict[str, Any]) -> WorkflowState:
        """Helper to create initial WorkflowState from Inputs."""
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
            return current_state
        except Exception as e:
            logger.error(f"[WorkflowEngine] Failed to initialize state: {e}")
            self.repository.update_execution(execution_id, {'status': 'failed', 'error': str(e)})
            raise e

    def _resolve_pipeline_steps(self, workflow_id: str) -> List[Any]:
        """Helper to fetch steps and resolve Agent instances."""
        wf_record = self.repository.get_workflow_by_id(workflow_id)
        if not wf_record:
             raise WorkflowNotFoundError(workflow_id)
        
        pipeline_steps = []
        step_ids = wf_record.get('steps', [])
        
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
            raise ValueError(f"No steps defined for workflow {workflow_id}. Ensure seeding is correct.")
            
        return pipeline_steps

    async def _execute_step(self, current_state: WorkflowState, agent: Any, step_doc: Dict[str, Any], execution_id: str) -> Any:
        """Helper to execute a single step (Pre-hooks -> Model -> Agent -> Post-hooks -> Validation -> DB Update)."""
        step_id = step_doc['id']
        agent_name = agent.__class__.__name__
        current_state.current_step_name = agent_name
        logger.info(f"[WorkflowEngine] Running step: {agent_name} (Step ID: {step_id})")

        # 1. Pre-Hooks
        config = step_doc.get('execution_config') or {}
        for hook in config.get('pre_hooks') or []:
            current_state = self._execute_hook(hook, agent, current_state)

        # 2. Dynamic Model Selection
        self._configure_agent_model(agent, step_id, execution_id)

        # 3. Prompt Construction
        system_instruction = self.prompt_builder.construct_prompt(step_id, current_state) if step_id else None

        # 4. Agent Execution (Async)
        try:
            current_state = await agent.execute(current_state, system_instruction=system_instruction)
        except Exception as e:
            raise AgentExecutionError(agent_name, step_id, e)

        # 5. Post-Hooks
        for hook in config.get('post_hooks') or []:
            current_state = self._execute_hook(hook, agent, current_state)

        # 6. Validation
        self._validate_step_output(agent_name, step_id, current_state, step_doc)

        # 7. Update DB
        self.repository.update_execution(execution_id, {
            'current_step': agent_name,
            'last_updated': datetime.now().isoformat()
        })

        # 8. Security Check
        if current_state.step_guard and current_state.step_guard.security_check.uhka_havaittu:
            return self._handle_security_intervention(execution_id, current_state)
            
        return current_state

    def _configure_agent_model(self, agent: Any, step_id: str, execution_id: str):
        """Helper to resolve and set the specific model for an agent."""
        # 1. Get mapping from Workflow Definition via execution -> workflow logic
        # For simplicity, invalidating complex fetches here, defaulting to safe 'fast' if not found easily
        # In a perfect world, we pass wf_record down.
        # Fallback: Default to 'fast'
        step_model_key = "fast" 
        
        # Try to fetch actual mapping from execution record or re-fetch workflow?
        # Re-fetching workflow record for EVERY step is expensive. 
        # Ideally _resolve_pipeline_steps returns (agent, step_doc, model_key).
        # For this refactor, let's keep it simple: 
        # We can re-fetch workflow ID from execution to be safe or pass it down.
        # Let's assume 'fast' for now to keep refactor safe or fetch it if needed.
        # Re-fetching IS safer for correctness.
        try:
             exec_rec = self.repository.get_execution(execution_id)
             if exec_rec:
                 wf_rec = self.repository.get_workflow_by_id(exec_rec['workflow_id'])
                 if wf_rec:
                     mapping = wf_rec.get('default_model_mapping', {})
                     step_model_key = mapping.get(step_id, "fast")
        except:
             pass

        resolved_model_name = self.registry.resolve_model_name(step_model_key)
        if hasattr(agent, 'set_model'):
            agent.set_model(resolved_model_name)
            logger.debug(f"[WorkflowEngine] Configured {agent.__class__.__name__} with {resolved_model_name}")

    def _validate_step_output(self, agent_name: str, step_id: str, state: WorkflowState, step_doc: Dict[str, Any]):
        """Helper to validate output against component schemas."""
        output_config_id = step_doc.get('output_config_component')
        if output_config_id:
            comp_record = self.repository.get_component_by_id(output_config_id)
            if comp_record:
                required_fields = comp_record.get('content', [])
                if isinstance(required_fields, list):
                    state_key = step_doc.get('state_key')
                    if state_key and hasattr(state, state_key):
                        output_obj = getattr(state, state_key)
                        if output_obj:
                            output_data = output_obj.model_dump(mode='json')
                            missing = [f for f in required_fields if "." not in f and f not in output_data]
                            if missing:
                                error_msg = f"Validation Failed: Missing fields {missing} in {agent_name}"
                                logger.error(f"[WorkflowEngine] {error_msg}")
                                raise AgentExecutionError(agent_name, step_id, ValueError(error_msg))

    def _handle_security_intervention(self, execution_id: str, state: WorkflowState) -> Dict[str, Any]:
        """Helper to handle security check failures."""
        msg = f"[WorkflowEngine] SECURITY INTERVENTION: Threat detected."
        logger.critical(msg)
        
        rejection_details = {
            "security_alert": "Execution aborted due to security violation.",
            "risk_level": state.step_guard.security_check.riski_taso,
            "analysis": state.step_guard.security_check.adversariaalinen_simulaatio_tulos,
            "guard_data": state.step_guard.model_dump()
        }
        
        self.repository.update_execution(execution_id, {
            'status': 'rejected',
            'error': f"Security Threat Detected: {state.step_guard.security_check.riski_taso}",
            'end_time': datetime.now().isoformat(),
            'result': rejection_details
        })
        return rejection_details

    def _project_final_result(self, execution_id: str, state: WorkflowState, pipeline_steps: List[Any]) -> Dict[str, Any]:
        """Helper to create the public result dictionary from the final state."""
        full_state = state.model_dump(mode='json')
        public_result = {}
        
        for agent, step_doc in pipeline_steps:
            state_key = step_doc.get('state_key')
            hoist_fields = step_doc.get('hoist_fields', [])
            
            output_config_id = step_doc.get('output_config_component')
            if output_config_id:
                comp_record = self.repository.get_component_by_id(output_config_id)
                if comp_record:
                    hoist_fields = comp_record.get('content', [])
            
            if state_key and hoist_fields and full_state.get(state_key):
                source_data = full_state[state_key]
                for field in hoist_fields:
                    if '.' in field:
                        parts = field.split('.')
                        val = source_data
                        for part in parts:
                            if isinstance(val, dict): val = val.get(part)
                            else: val = None; break
                        target_key = parts[-1]
                    else:
                        val = source_data.get(field)
                        target_key = field
                    public_result[target_key] = val

        self.repository.update_execution(execution_id, {
            'status': 'completed',
            'end_time': datetime.now().isoformat(),
            'result': public_result,
            'trace': full_state 
        })
        return public_result

    def _handle_execution_error(self, execution_id: str, error: Exception):
        """Helper to log and update DB on failure."""
        if isinstance(error, AgentExecutionError):
            logger.error(f"[WorkflowEngine] Agent Error: {error.message}")
            msg = error.message
        else:
            logger.error(f"[WorkflowEngine] Critical Failure: {error}", exc_info=True)
            msg = str(error)

        self.repository.update_execution(execution_id, {
            'status': 'failed',
            'error': msg,
            'end_time': datetime.now().isoformat()
        })

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

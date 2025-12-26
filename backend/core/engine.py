import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
import pkgutil
import importlib
import inspect
import backend.agents

from backend.models.state import WorkflowState, InputData
# from backend.config import INITIAL_MODEL # Removed
from backend.agents.base import BaseAgent
from backend.services.agent_registry import AgentRegistry
from backend.services.prompt_builder import PromptBuilder
import logging
from backend.database.repository import AbstractWorkflowRepository
from backend.context import set_execution_context, clear_execution_context
from backend.exceptions import ExecutionNotFoundError, WorkflowNotFoundError, AgentExecutionError, FatalInterruption
from backend.models.domain import TaintedData # Type checking import
from backend.core.runner import PipelineRunner

logger = logging.getLogger(__name__)

class WorkflowEngine:
    def __init__(
        self, 
        db_path: str, 
        repository: Optional[AbstractWorkflowRepository] = None, 
        registry: Optional[AgentRegistry] = None,
        prompt_builder: Optional[PromptBuilder] = None,
        db_client: Optional[Any] = None,
        storage_client: Optional[Any] = None,
        document_service: Optional[Any] = None
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

        if storage_client:
             self.storage_client = storage_client
        else:
             from backend.services.storage import get_storage_client
             self.storage_client = get_storage_client()
             
        if document_service:
            self.document_service = document_service
        else:
            from backend.services.document_service import DocumentService
            self.document_service = DocumentService(self.storage_client)
        
        # Initialize Runner
        self.runner = PipelineRunner(self.repository, self.registry, self.prompt_builder)
        
        # Agents Map is now in Registry
        # self.agents_map = {} # Removed
        
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

        # Handle Files (Extract & Archive) via Service
        if files:
            file_updates = await self.document_service.process_evidence_files(execution_id, files)
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

    # _ingest_files REMOVED (Moved to FileIngestionService)

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
        Delegates execution logic to PipelineRunner.
        """
        set_execution_context(execution_id)
        logger.info(f"[WorkflowEngine] Starting execution {execution_id}")
        
        try:
            # 1. Initialize State via Runner
            current_state = await self.runner.initialize_state(execution_id, raw_inputs)
            
            # 2. Get Pipeline Steps
            exec_record = self.repository.get_execution(execution_id)
            if not exec_record:
                raise ExecutionNotFoundError(execution_id)
            
            pipeline_steps = self._resolve_pipeline_steps(exec_record['workflow_id'])

            # 3. Execute Loop via Runner
            from backend.services.progress import DatabaseProgressTracker
            tracker = DatabaseProgressTracker(self.repository, execution_id)
            tracker.start() 

            print(f"DEBUG: Engine calling runner.execute_loop. Runner type: {type(self.runner)}", flush=True)
            final_state = await self.runner.execute_loop(current_state, pipeline_steps, tracker, execution_id)
            
            # 4. Check for Halt/Early Exit
            if isinstance(final_state, dict) and "security_alert" in final_state:
                 return final_state

            # 5. Success
            logger.info(f"[WorkflowEngine] Execution {execution_id} completed successfully.")
            result = self._project_final_result(execution_id, final_state, pipeline_steps)
            tracker.complete(result)
            return result

        except FatalInterruption as fi:
            return self._create_halt_response(execution_id, fi.step_name, fi, current_state)
        except AgentExecutionError as ae:
            self._handle_execution_error(execution_id, ae, current_state)
        except Exception as e:
            self._handle_execution_error(execution_id, e, current_state)
        finally:
            clear_execution_context()

    async def resume_execution(self, execution_id: str) -> Dict[str, Any]:
        """
        Resumes a failed or interrupted execution from the last successful state.
        Delegates execution logic to PipelineRunner.
        """
        set_execution_context(execution_id)
        logger.info(f"[WorkflowEngine] RESUMING execution {execution_id}")

        try:
            # 1. Load Execution Record & Trace
            exec_record = self.repository.get_execution(execution_id)
            if not exec_record:
                raise ExecutionNotFoundError(execution_id)
            
            trace_data = exec_record.get('trace')
            if not trace_data:
                logger.warning(f"[WorkflowEngine] No trace found for {execution_id}. Restarting from scratch.")
                return await self.run_execution(execution_id, exec_record['inputs'])

            # 2. Reconstruct State
            current_state = WorkflowState.model_validate(trace_data)
            
            # 3. Determine Resume Point
            pipeline_steps = self._resolve_pipeline_steps(exec_record['workflow_id'])
            
            steps_to_run = []
            resume_index = 0
            
            for i, (agent, step_doc) in enumerate(pipeline_steps):
                state_key = step_doc.get('state_key')
                
                is_done = False
                if state_key and hasattr(current_state, state_key):
                    val = getattr(current_state, state_key)
                    if val is not None:
                         is_done = True
                
                if not is_done:
                    steps_to_run.append((agent, step_doc))
                    if resume_index == 0: resume_index = i # Mark start index
            
            if not steps_to_run:
                logger.info("[WorkflowEngine] Execution appears already complete. Returning result.")
                return self._project_final_result(execution_id, current_state, pipeline_steps)

            logger.info(f"[WorkflowEngine] Resuming from step {resume_index + 1}/{len(pipeline_steps)} ({steps_to_run[0][0].__class__.__name__})")

            # 4. Update Status to Running
            self.repository.update_execution(execution_id, {
                'status': 'running',
                'error': None # Clear error
            })
            
            # 5. Execute Remaining Steps via Runner
            from backend.services.progress import DatabaseProgressTracker
            tracker = DatabaseProgressTracker(self.repository, execution_id)
            tracker.start() 

            final_state = await self.runner.execute_loop(
                current_state, 
                steps_to_run, 
                tracker, 
                execution_id, 
                start_index=resume_index,
                total_steps_count=len(pipeline_steps)
            )

            # 6. Check for Halt/Early Exit
            if isinstance(final_state, dict) and "security_alert" in final_state:
                 return final_state

            # 7. Success
            logger.info(f"[WorkflowEngine] Execution {execution_id} completed successfully (RESUMED).")
            result = self._project_final_result(execution_id, final_state, pipeline_steps)
            tracker.complete(result)
            return result

        except Exception as e:
            c_state = locals().get('current_state', None)
            self._handle_execution_error(execution_id, e, c_state)
            raise e
        finally:
            clear_execution_context()

    async def recover_interrupted_jobs(self):
        """
        Scans for jobs marked 'running' that are structurally dead (e.g. after server restart).
        Resumes them automatically.
        """
        logger.info("[WorkflowEngine] Scanning for interrupted jobs...")
        try:
            all_executions = self.repository.get_all_executions()
            running_jobs = [j for j in all_executions if j.get('status') == 'running']
            
            for job in running_jobs:
                eid = job['execution_id']
                logger.warning(f"[WorkflowEngine] Found stale running job {eid}. Auto-resuming...")
                try:
                    if not job.get('trace'):
                        logger.warning(f"[WorkflowEngine] Cannot resume {eid}: No trace data. Marking as failed.")
                        self.repository.update_execution(eid, {'status': 'failed', 'error': 'System Restart: No trace to resume.'})
                        continue

                    import asyncio
                    asyncio.create_task(self.resume_execution(eid))
                    
                except Exception as e:
                    logger.error(f"[WorkflowEngine] Failed to recovery job {eid}: {e}")
                    
        except Exception as e:
            logger.error(f"[WorkflowEngine] Recovery scan failed: {e}")

    def _create_halt_response(self, execution_id: str, step_name: str, error: FatalInterruption, state: Optional[WorkflowState] = None) -> Dict[str, Any]:
        """Helper to create a structured HALT response."""
        msg = f"[WorkflowEngine] FATAL INTERRUPTION at {step_name}: {error.reason}"
        logger.error(msg)
        
        halt_result = error.details
        
        halt_result.update({
             "status": "failed",
             "halted_at": step_name,
             "timestamp": datetime.now().isoformat(),
             "reason": error.reason
        })

        update_data = {
            'status': 'failed',
            'error': error.reason,
            'end_time': datetime.now().isoformat(),
            'result': halt_result
        }
        if state:
            update_data['trace'] = state.model_dump(mode='json')

        self.repository.update_execution(execution_id, update_data)
        return halt_result

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

    def _project_final_result(self, execution_id: str, state: WorkflowState, pipeline_steps: List[Any]) -> Dict[str, Any]:
        """Helper to create the public result dictionary from the final state."""
        # 1. Start with the architecturally mandated V2 structure (Scores, Reports, etc.)
        public_result = state.to_flat_dict()
        full_state = state.model_dump(mode='json')

        # 2. Augment with dynamic steps that might not be in to_flat_dict explicit logic
        # and apply specific valid hoisting configurations.
        for agent, step_doc in pipeline_steps:
            state_key = step_doc.get('state_key')
            hoist_fields = step_doc.get('hoist_fields', [])
            
            output_config_id = step_doc.get('output_config_component')
            if output_config_id:
                comp_record = self.repository.get_component_by_id(output_config_id)
                if comp_record:
                    hoist_fields = comp_record.get('content', [])
            
            if state_key and full_state.get(state_key):
                source_data = full_state[state_key]
                


                if hoist_fields:
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
                        # Overwrite/Add specific hoisted fields
                        public_result[target_key] = val

        # 3. Generate Consolidated Bibliography (ReferenceManager)
        # Scan the FINAL public_result for all used citations
        try:
            from backend.services.reference_manager import ReferenceManager
            
            # Load KB items for resolution
            kb_items = self.repository.get_knowledge_base_items()
            # Transform to expected structure for ReferenceManager
            # (Similar to CoachAgent prepare_context logic, maybe unify later?)
            kb_struct = {"references": []}
            for item in kb_items:
                if item.get('type') == 'reference':
                    kb_struct["references"].append({
                        "citation": item.get('definition'),
                        "short_citation": item.get('term'),
                        "doi": item.get('doi_link')
                    })
            
            ref_manager = ReferenceManager(kb_struct)
            
            # Scan everything!
            bibliography = ref_manager.scan_and_collect_references(public_result)
            
            if bibliography:
                # Add to Report section or Root?
                # User asked for "yksi lähdeluettelo" (one bibliography)
                # Let's put it in public_result["lahdeluettelo"] (Root level)
                public_result["lahdeluettelo"] = bibliography
                
                # Also ensure it's in Report if Report exists
                if "Report" in public_result:
                    public_result["Report"]["lahdeluettelo"] = bibliography
                    
        except Exception as e:
            logger.error(f"[WorkflowEngine] Reference consolidation failed: {e}")

        self.repository.update_execution(execution_id, {
            'status': 'completed',
            'end_time': datetime.now().isoformat(),
            'result': public_result,
            'trace': full_state 
        })
        return public_result

    def _handle_execution_error(self, execution_id: str, error: Exception, state: Optional[WorkflowState] = None):
        """Helper to log and update DB on failure."""
        if isinstance(error, AgentExecutionError):
            logger.error(f"[WorkflowEngine] Agent Error: {error.message}")
            msg = error.message
        else:
            logger.error(f"[WorkflowEngine] Critical Failure: {str(error)}", exc_info=True)
            msg = str(error)

        update_data = {
            'status': 'failed',
            'error': msg,
            'end_time': datetime.now().isoformat()
        }
        
        # Save trace if available so we can resume later
        if state:
            try:
                # Assuming state is partial but valid Pydantic object
                update_data['trace'] = state.model_dump(mode='json')
                logger.info(f"[WorkflowEngine] Saved crash state (Trace) for {execution_id}")
            except Exception as e:
                logger.error(f"[WorkflowEngine] Failed to save crash state: {e}")

        self.repository.update_execution(execution_id, update_data)

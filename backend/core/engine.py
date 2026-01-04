import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.context import clear_execution_context, set_execution_context
from backend.core.runner import PipelineRunner
from backend.database.repository import AbstractWorkflowRepository
from backend.exceptions import AgentExecutionError, ExecutionNotFoundError, FatalInterruption, WorkflowNotFoundError
from backend.models.state import WorkflowState
from backend.services.agent_registry import AgentRegistry
from backend.services.prompt_builder import PromptBuilder

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
        document_service: Optional[Any] = None,
    ):
        """
        Initializes the Workflow Engine with necessary dependencies.

        Args:
            db_path (str): Path to the database file.
            repository (Optional[AbstractWorkflowRepository]): Data access layer.
            registry (Optional[AgentRegistry]): Agent management service.
            prompt_builder (Optional[PromptBuilder]): Prompt generation service.
            db_client (Optional[Any]): DB connection instance.
            storage_client (Optional[Any]): Storage connection instance.
            document_service (Optional[Any]): Document processing service.
        """
        self.db_path = db_path

        # Repository Injection (Preferred)
        if repository:
            self.repository = repository
        else:
            # AUTO-WIRING:
            # If no repo is provided, we create one using the new Async-First Dependency.
            from backend.dependencies import get_async_repository, get_db_client_dep

            self.repository = get_async_repository(get_db_client_dep())

        # Service Injection
        if registry:
            self.registry = registry
        else:
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

        if not registry:
            pass

        logger.info(f"[WorkflowEngine] initialized with DB at {db_path}")

    # --- DELEGATED METHODS (Services) ---
    # --- DELEGATED METHODS (Services) ---
    async def resolve_model_name(self, model_identifier: str) -> str:
        """
        Resolves a high-level model strategy to a concrete model name.
        """
        return await self.registry.resolve_model_name(model_identifier)

    async def create_workflow(self, name: str, steps: List[Dict[str, Any]]) -> int:
        """
        Creates a new workflow definition in the repository.
        """
        workflow_id = await self.repository.create_workflow(
            {"name": name, "steps": steps, "created_at": datetime.now().isoformat()}
        )
        return workflow_id

    async def create_execution(
        self,
        workflow_id: Any,
        inputs: Dict[str, Any],
        files: Optional[Dict[str, tuple]] = None,
        organization_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> str:
        """
        Initializes a new execution record with processed inputs and files.
        """
        execution_id = str(uuid.uuid4())

        # Merge basic inputs
        final_inputs = inputs.copy()

        # Handle Files (Extract & Archive) via Service
        if files:
            file_updates = await self.document_service.process_evidence_files(execution_id, files)
            final_inputs.update(file_updates)

            final_inputs.update(file_updates)

        await self.repository.create_execution(
            {
                "execution_id": execution_id,
                "workflow_id": workflow_id,
                "status": "pending",
                "start_time": datetime.now().isoformat(),
                "inputs": final_inputs,
                "logs": [],
                "organization_id": organization_id,
                "user_id": user_id,
            }
        )
        return execution_id

    async def get_execution_status(self, execution_id: Any) -> Optional[Dict[str, Any]]:
        """
        Retrieves the current status and data for a given execution.
        """
        exec_data = await self.repository.get_execution(str(execution_id))
        if not exec_data:
            raise ExecutionNotFoundError(str(execution_id))
        return exec_data

    async def preview_step_prompt(self, step_id: str) -> Dict[str, Any]:
        """
        Previews the prompt for a specific step.
        """
        return await self.prompt_builder.preview_step_prompt(step_id)

    async def preview_full_chain_prompts(self, workflow_id: str) -> str:
        """
        Generates a full textual preview of all prompts in the validation chain.
        """
        return await self.prompt_builder.preview_full_chain_prompts(workflow_id)

    async def _construct_prompt_for_step(self, step_id: str, current_state: Optional[WorkflowState] = None) -> str:
        """
        Helper to construct a prompt for a single step with current state.
        """
        return await self.prompt_builder.construct_prompt(step_id, current_state)

    # --- CORE EXECUTION LOGIC (V2) ---

    async def run_execution(self, execution_id: str, raw_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes a workflow state-machine asynchronously.

        Args:
            execution_id (str): The Execution UUID.
            raw_inputs (Dict[str, Any]): Initial input data.

        Returns:
            Dict[str, Any]: The final results object.
        """
        set_execution_context(execution_id)
        logger.info(f"[WorkflowEngine] Starting execution {execution_id}")

        try:
            # 1. Get Execution Record first to identify Workflow
            exec_record = await self.repository.get_execution(execution_id)
            if not exec_record:
                raise ExecutionNotFoundError(execution_id)

            wf_id = exec_record["workflow_id"]
            wf_record = await self.repository.get_workflow_by_id(wf_id)
            wf_name = wf_record["name"] if wf_record else "Unknown"

            # 2. Initialize State via Runner
            current_state = await self.runner.initialize_state(
                execution_id,
                raw_inputs,
                wf_id,
                wf_name,
                organization_id=exec_record.get("organization_id"),
                user_id=exec_record.get("user_id"),
            )

            pipeline_steps = await self._resolve_pipeline_steps(wf_id)

            # 3. Execute Loop via Runner
            from backend.services.progress import DatabaseProgressTracker

            tracker = DatabaseProgressTracker(self.repository, execution_id)
            await tracker.start()

            print(f"DEBUG: Engine calling runner.execute_loop. Runner type: {type(self.runner)}", flush=True)
            final_state = await self.runner.execute_loop(current_state, pipeline_steps, tracker, execution_id)

            # 4. Check for Halt/Early Exit
            if isinstance(final_state, dict) and "security_alert" in final_state:
                return final_state

            # 5. Success
            logger.info(f"[WorkflowEngine] Execution {execution_id} completed successfully.")
            result = await self._project_final_result(execution_id, final_state, pipeline_steps)
            await tracker.complete(result)
            return result

        except FatalInterruption as fi:
            return await self._create_halt_response(execution_id, fi.step_name, fi, current_state)
        except AgentExecutionError as ae:
            await self._handle_execution_error(execution_id, ae, current_state)
        except Exception as e:
            await self._handle_execution_error(execution_id, e, current_state)
        finally:
            clear_execution_context()

    async def resume_execution(self, execution_id: str) -> Dict[str, Any]:
        """
        Resumes a failed or interrupted execution from its last known trace state.

        Args:
            execution_id (str): The Execution UUID.

        Returns:
            Dict[str, Any]: The final results object.
        """
        set_execution_context(execution_id)
        logger.info(f"[WorkflowEngine] RESUMING execution {execution_id}")

        try:
            # 1. Load Execution Record & Trace
            exec_record = await self.repository.get_execution(execution_id)
            if not exec_record:
                raise ExecutionNotFoundError(execution_id)

            trace_data = exec_record.get("trace")
            if not trace_data:
                logger.warning(f"[WorkflowEngine] No trace found for {execution_id}. Restarting from scratch.")
                return await self.run_execution(execution_id, exec_record["inputs"])

            # 2. Reconstruct State
            current_state = WorkflowState.model_validate(trace_data)

            # Identity Injection (Resume Logic)
            if not current_state.organization_id:
                current_state.organization_id = exec_record.get("organization_id")
            if not current_state.user_id:
                current_state.user_id = exec_record.get("user_id")

            # 3. Determine Resume Point
            pipeline_steps = await self._resolve_pipeline_steps(exec_record["workflow_id"])

            steps_to_run = []
            resume_index = 0

            for i, (agent, step_doc) in enumerate(pipeline_steps):
                state_key = step_doc.get("state_key")

                is_done = False
                if state_key and hasattr(current_state, state_key):
                    val = getattr(current_state, state_key)
                    if val is not None:
                        is_done = True

                if not is_done:
                    steps_to_run.append((agent, step_doc))
                    if resume_index == 0:
                        resume_index = i  # Mark start index

            if not steps_to_run:
                logger.info("[WorkflowEngine] Execution appears already complete. Returning result.")
                return await self._project_final_result(execution_id, current_state, pipeline_steps)

            logger.info(
                f"[WorkflowEngine] Resuming from step {resume_index + 1}/{len(pipeline_steps)} ({steps_to_run[0][0].__class__.__name__})"
            )

            # 4. Update Status to Running
            await self.repository.update_execution(execution_id, {"status": "running", "error": None})

            # 5. Execute Remaining Steps via Runner
            from backend.services.progress import DatabaseProgressTracker

            tracker = DatabaseProgressTracker(self.repository, execution_id)
            await tracker.start()

            final_state = await self.runner.execute_loop(
                current_state,
                steps_to_run,
                tracker,
                execution_id,
                start_index=resume_index,
                total_steps_count=len(pipeline_steps),
            )

            # 6. Check for Halt/Early Exit
            if isinstance(final_state, dict) and "security_alert" in final_state:
                return final_state

            # 7. Success
            logger.info(f"[WorkflowEngine] Execution {execution_id} completed successfully (RESUMED).")
            result = await self._project_final_result(execution_id, final_state, pipeline_steps)
            await tracker.complete(result)
            return result

        except Exception as e:
            c_state = locals().get("current_state", None)
            await self._handle_execution_error(execution_id, e, c_state)
            raise e
        finally:
            clear_execution_context()

    async def recover_interrupted_jobs(self):
        """
        Scans for and resumes jobs that were interrupted (e.g. by server restart).
        """
        logger.info("[WorkflowEngine] Scanning for interrupted jobs...")
        try:
            all_executions = await self.repository.get_all_executions()
            running_jobs = [j for j in all_executions if j.get("status") == "running"]

            for job in running_jobs:
                eid = job["execution_id"]
                logger.warning(f"[WorkflowEngine] Found stale running job {eid}. Auto-resuming...")
                try:
                    if not job.get("trace"):
                        logger.warning(f"[WorkflowEngine] Cannot resume {eid}: No trace data. Marking as failed.")
                        await self.repository.update_execution(
                            eid, {"status": "failed", "error": "System Restart: No trace to resume."}
                        )
                        continue

                    import asyncio

                    asyncio.create_task(self.resume_execution(eid))

                except Exception as e:
                    logger.error(f"[WorkflowEngine] Failed to recovery job {eid}: {e}")

        except Exception as e:
            logger.error(f"[WorkflowEngine] Recovery scan failed: {e}")

    async def _create_halt_response(
        self, execution_id: str, step_name: str, error: FatalInterruption, state: Optional[WorkflowState] = None
    ) -> Dict[str, Any]:
        """
        Helper to construct a structured response when execution is fatally halted.

        Args:
            execution_id (str): Execution ID.
            step_name (str): Step where interruption occurred.
            error (FatalInterruption): The exception object.
            state (Optional[WorkflowState]): Current state object.

        Returns:
            Dict[str, Any]: The structured halt result.
        """
        msg = f"[WorkflowEngine] FATAL INTERRUPTION at {step_name}: {error.reason}"
        logger.error(msg)

        halt_result = error.details

        halt_result.update(
            {
                "status": "failed",
                "halted_at": step_name,
                "timestamp": datetime.now().isoformat(),
                "reason": error.reason,
            }
        )

        update_data = {
            "status": "failed",
            "error": error.reason,
            "end_time": datetime.now().isoformat(),
            "result": halt_result,
        }
        if state:
            update_data["trace"] = state.model_dump(mode="json")

        await self.repository.update_execution(execution_id, update_data)
        return halt_result

    async def _resolve_pipeline_steps(self, workflow_id: str) -> List[Any]:
        """
        Resolves the sequential list of execution steps for a workflow.

        Args:
            workflow_id (str): Workflow ID.

        Returns:
            List[Any]: List of (AgentInstance, StepDocument) tuples.
        """
        wf_record = await self.repository.get_workflow_by_id(workflow_id)
        if not wf_record:
            raise WorkflowNotFoundError(workflow_id)

        pipeline_steps = []
        step_ids = wf_record.get("steps", [])

        for sid in step_ids:
            s_doc = await self.repository.get_step_by_id(sid)
            if s_doc:
                agent_name = s_doc.get("component")
                if agent_name:
                    agent_instance = self.registry.get_agent(agent_name)
                    if agent_instance:
                        pipeline_steps.append((agent_instance, s_doc))

        if not pipeline_steps:
            logger.error(f"[WorkflowEngine] Error: No workflow steps found for Workflow ID {workflow_id}")
            raise ValueError(f"No steps defined for workflow {workflow_id}. Ensure seeding is correct.")

        # VALIDATION: Enforce Maximum 2 BARS Matrices per Workflow
        # This ensures the Stereoscopic Audit does not become a 'cacophony'.
        matrix_count = sum(
            1 for _, doc in pipeline_steps if doc.get("component") == "JudgeAgent" or doc.get("matrix_id")
        )
        if matrix_count > 2:
            logger.error(
                f"[WorkflowEngine] Configuration Error: Workflow {workflow_id} has {matrix_count} matrices "
                "(Max 2 allowed)."
            )
            raise ValueError(
                f"Workflow '{workflow_id}' violates constraint: "
                f"Maximum of 2 BARS Matrices allowed (found {matrix_count})."
            )

        return pipeline_steps

    async def _project_final_result(
        self, execution_id: str, state: WorkflowState, pipeline_steps: List[Any]
    ) -> Dict[str, Any]:
        """
        Transforms the final internal state into the public result dictionary.
        Applies logic for field hoisting and Reference Manager scanning.

        Args:
            execution_id (str): Execution ID.
            state (WorkflowState): Final state object.
            pipeline_steps (List[Any]): List of executed steps info.

        Returns:
            Dict[str, Any]: The public facing result object.
        """
        # 1. Start with the architecturally mandated V2 structure (Scores, Reports, etc.)
        public_result = state.to_flat_dict()
        full_state = state.model_dump(mode="json")

        # 2. Augment with dynamic steps that might not be in to_flat_dict explicit logic
        for agent, step_doc in pipeline_steps:
            state_key = step_doc.get("state_key")
            hoist_fields = step_doc.get("hoist_fields", [])

            output_config_id = step_doc.get("output_config_component")
            if output_config_id:
                comp_record = await self.repository.get_component_by_id(output_config_id)
                if comp_record:
                    hoist_fields = comp_record.get("content", [])

            if state_key and full_state.get(state_key):
                source_data = full_state[state_key]

                if hoist_fields:
                    for field in hoist_fields:
                        if "." in field:
                            parts = field.split(".")
                            val = source_data
                            for part in parts:
                                if isinstance(val, dict):
                                    val = val.get(part)
                                else:
                                    val = None
                                    break
                            target_key = parts[-1]
                        else:
                            val = source_data.get(field)
                            target_key = field
                        # Overwrite/Add specific hoisted fields
                        public_result[target_key] = val

        # 3. Generate Consolidated Bibliography (ReferenceManager)
        try:
            from backend.services.reference_manager import ReferenceManager

            kb_items = await self.repository.get_knowledge_base_items()
            kb_struct = {"references": []}
            for item in kb_items:
                if item.get("type") == "reference":
                    kb_struct["references"].append(
                        {
                            "citation": item.get("definition"),
                            "short_citation": item.get("term"),
                            "doi": item.get("doi_link"),
                        }
                    )

            ref_manager = ReferenceManager(kb_struct)

            # Scan everything!
            bibliography = ref_manager.scan_and_collect_references(public_result)

            if bibliography:
                # Add to Root
                public_result["lahdeluettelo"] = bibliography

                # Add to Report if exists
                if "Report" in public_result:
                    public_result["Report"]["lahdeluettelo"] = bibliography

        except Exception as e:
            logger.error(f"[WorkflowEngine] Reference consolidation failed: {e}")

        # 4. Inject Matrix Metadata for UI (Stereoscopic Vision Support)
        # This allows the Frontend to decide whether to show 'Combined Verdict' (Dual) or standard view.
        matrix_count = sum(
            1 for _, doc in pipeline_steps if doc.get("component") == "JudgeAgent" or doc.get("matrix_id")
        )
        public_result["_meta"] = {
            "matrix_count": matrix_count,
            "matrix_mode": "dual" if matrix_count == 2 else "single",
        }
        # Backward compatibility for direct access if needed
        public_result["matrix_count"] = matrix_count
        public_result["matrix_mode"] = "dual" if matrix_count == 2 else "single"

        await self.repository.update_execution(
            execution_id,
            {
                "status": "completed",
                "end_time": datetime.now().isoformat(),
                "result": public_result,
                "trace": full_state,
            },
        )
        return public_result

    async def _handle_execution_error(self, execution_id: str, error: Exception, state: Optional[WorkflowState] = None):
        """
        Handles exception logging and state persistence during failure.

        Args:
            execution_id (str): Execution ID.
            error (Exception): The captured exception.
            state (Optional[WorkflowState]): The current state.
        """
        if isinstance(error, AgentExecutionError):
            logger.error(f"[WorkflowEngine] Agent Error: {error.message}")
            msg = error.message
        else:
            logger.error(f"[WorkflowEngine] Critical Failure: {str(error)}", exc_info=True)
            msg = str(error)

        update_data = {"status": "failed", "error": msg, "end_time": datetime.now().isoformat()}

        # Save trace if available so we can resume later
        if state:
            try:
                # Assuming state is partial but valid Pydantic object
                update_data["trace"] = state.model_dump(mode="json")
                logger.info(f"[WorkflowEngine] Saved crash state (Trace) for {execution_id}")
            except Exception as e:
                logger.error(f"[WorkflowEngine] Failed to save crash state: {e}")

        await self.repository.update_execution(execution_id, update_data)

import logging
import uuid
from datetime import datetime
from typing import Any

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
        repository: AbstractWorkflowRepository,
        registry: AgentRegistry,
        prompt_builder: PromptBuilder,
        storage_client: Any,
        document_service: Any,
    ):
        """Initializes the Workflow Engine with necessary dependencies.
        Strict Dependency Injection is enforced; no auto-wiring allowed.

        Args:
            db_path (str): Path to the database file (for logging purposes).
            repository (AbstractWorkflowRepository): Data access layer.
            registry (AgentRegistry): Agent management service.
            prompt_builder (PromptBuilder): Prompt generation service.
            storage_client (Any): Storage connection instance.
            document_service (Any): Document processing service.

        """
        self.db_path = db_path
        self.repository = repository
        self.registry = registry
        self.prompt_builder = prompt_builder
        self.storage_client = storage_client
        self.document_service = document_service

        # Initialize Runner
        self.runner = PipelineRunner(self.repository, self.registry, self.prompt_builder)

        logger.info(f"[WorkflowEngine] initialized with DB at {db_path} (Strict DI)")

    # --- DELEGATED METHODS (Services) ---
    async def resolve_model_name(self, model_identifier: str) -> str:
        """Resolves a high-level model strategy to a concrete model name.

        Args:
            model_identifier (str): The strategy key (e.g. 'fast').

        Returns:
            str: The resolved model name.
        """
        return await self.registry.resolve_model_name(model_identifier)

    async def create_workflow(self, name: str, steps: list[dict[str, Any]]) -> int:
        """Creates a new workflow definition in the repository.

        Args:
            name (str): Workflow name.
            steps (List[dict]): List of step definitions.

        Returns:
            int: The new Workflow ID.

        Side Effects:
            - **Database**: Inserts a new record into the `workflows` table.
        """
        workflow_id = await self.repository.create_workflow(
            {"name": name, "steps": steps, "created_at": datetime.now().isoformat()}
        )
        return workflow_id

    async def create_execution(
        self,
        workflow_id: Any,
        inputs: dict[str, Any],
        files: dict[str, tuple] | None = None,
        organization_id: str | None = None,
        user_id: str | None = None,
    ) -> str:
        """Initializes a new execution record with processed inputs and files.

        Args:
            workflow_id (Any): Workflow ID.
            inputs (dict): Raw input dictionary.
            files (Optional[dict]): File uploads.
            organization_id (Optional[str]): Org ID.
            user_id (Optional[str]): User ID.

        Returns:
            str: The new Execution UUID.

        Side Effects:
            - **Database**: Creates a new execution record with status 'pending'.
            - **DocumentService**: Ingests and archives provided files, updating inputs with file metadata.
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

    async def get_execution_status(self, execution_id: Any) -> dict[str, Any] | None:
        """Retrieves the current status and data for a given execution.

        Args:
            execution_id (Any): Execution UUID.

        Returns:
            Optional[dict]: Execution record if found.

        Raises:
            ExecutionNotFoundError: If not found.
        """
        exec_data = await self.repository.get_execution(str(execution_id))
        if not exec_data:
            raise ExecutionNotFoundError(str(execution_id))
        return exec_data

    async def preview_step_prompt(self, step_id: str) -> dict[str, Any]:
        """Previews the prompt for a specific step.

        Args:
            step_id (str): Step ID.

        Returns:
            dict: Preview data (prompt string).
        """
        return await self.prompt_builder.preview_step_prompt(step_id)

    async def preview_full_chain_prompts(self, workflow_id: str) -> str:
        """Generates a full textual preview of all prompts in the validation chain.

        Args:
            workflow_id (str): Workflow ID.

        Returns:
            str: Concatenated prompt preview.
        """
        return await self.prompt_builder.preview_full_chain_prompts(workflow_id)

    async def _construct_prompt_for_step(self, step_id: str, current_state: WorkflowState | None = None) -> str:
        """Helper to construct a prompt for a single step with current state.

        Args:
            step_id (str): Step ID.
            current_state (Optional[WorkflowState]): Current state.

        Returns:
            str: Prompt string.
        """
        return await self.prompt_builder.construct_prompt(step_id, current_state)

    # --- CORE EXECUTION LOGIC (V2) ---

    async def execute_workflow_task(
        self, execution_id: str, workflow_id: str, inputs: dict[str, Any]
    ) -> dict[str, Any]:
        """Core worker task: Executes the workflow state-machine logic.
        This method is designed to be called locally or via a task queue worker.

        Args:
            execution_id (str): The Execution UUID.
            workflow_id (str): The Workflow UUID.
            inputs (Dict[str, Any]): Input data.

        Returns:
            Dict[str, Any]: The final results.

        Side Effects:
            - **Context**: Sets thread-local execution context.
            - **Database**:
                - Updates execution status to 'completed' or 'failed'.
                - Persists full execution trace (WorkflowState).
            - **Progress Tracker**: Emits progress events to the database.

        Raises:
            ExecutionNotFoundError: If execution ID is invalid.
            FatalInterruption: If workflow is halted by logic or error.
        """
        set_execution_context(execution_id)
        logger.info(f"[WorkflowEngine] Worker started execution {execution_id}")

        try:
            # 1. Fetch Context Data
            # We fetch fresh records to ensure we have latest data (especially in distributed env)
            exec_record = await self.repository.get_execution(execution_id)
            if not exec_record:
                raise ExecutionNotFoundError(execution_id)

            wf_record = await self.repository.get_workflow_by_id(workflow_id)
            wf_name = wf_record["name"] if wf_record else "Unknown"

            # 2. Initialize State via Runner
            current_state = await self.runner.initialize_state(
                execution_id,
                inputs,
                workflow_id,
                wf_name,
                organization_id=exec_record.get("organization_id"),
                user_id=exec_record.get("user_id"),
            )

            pipeline_steps = await self._resolve_pipeline_steps(workflow_id)

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
            # We need to reconstruct state if possible for the halt response,
            # but current_state accessible in this scope?
            # We initialize current_state early, but python scope is function level?
            # Safer to initialize c_state var
            c_state = locals().get("current_state", None)
            return await self._create_halt_response(execution_id, fi.step_name, fi, c_state)
        except AgentExecutionError as ae:
            c_state = locals().get("current_state", None)
            await self._handle_execution_error(execution_id, ae, c_state)
            # We assume handle_execution_error updates DB. We return None or empty dict?
            # Better to re-raise or return a status?
            # The caller might expect a result dict.
            # Usually we return the partial result from DB or just None.
            return {"status": "failed", "error": ae.message}
        except Exception as e:
            c_state = locals().get("current_state", None)
            await self._handle_execution_error(execution_id, e, c_state)
            return {"status": "failed", "error": str(e)}
        finally:
            clear_execution_context()

    async def run_execution(
        self, execution_id: str, raw_inputs: dict[str, Any], arq_pool: Any | None = None
    ) -> dict[str, Any]:
        """Executes a workflow state-machine asynchronously.

        If 'arq_pool' is provided, the job is enqueued to Redis (Async/Distributed).
        Otherwise, it runs locally/inline (Blocking/Legacy).

        Args:
            execution_id (str): The Execution UUID.
            raw_inputs (Dict[str, Any]): Initial input data.
            arq_pool (Optional[Any]): Arq Redis pool for background tasks.

        Returns:
            Dict[str, Any]: The initial state (if queued) or final results.

        Side Effects:
            - **Redis**: Enqueues job if `arq_pool` is provided.
            - **Database**: Updates execution record during synchronous run.
        """
        set_execution_context(execution_id)
        logger.info(f"[WorkflowEngine] Submit execution {execution_id}")

        try:
            # 1. Get Execution Record first to identify Workflow
            exec_record = await self.repository.get_execution(execution_id)
            if not exec_record:
                raise ExecutionNotFoundError(execution_id)

            wf_id = exec_record["workflow_id"]
            wf_record = await self.repository.get_workflow_by_id(wf_id)
            wf_name = wf_record["name"] if wf_record else "Unknown"

            # 2. Distributed Execution (Preferred)
            if arq_pool:
                logger.info(f"[WorkflowEngine] Enqueuing execution {execution_id} to Arq/Redis.")

                # Enqueue the job defined in backend/worker.py
                await arq_pool.enqueue_job(
                    "execute_workflow_task", execution_id=execution_id, workflow_id=wf_id, inputs=raw_inputs
                )

                # Initialize state stub for immediate UI feedback
                current_state = await self.runner.initialize_state(
                    execution_id,
                    raw_inputs,
                    wf_id,
                    wf_name,
                    organization_id=exec_record.get("organization_id"),
                    user_id=exec_record.get("user_id"),
                )

                return current_state.model_dump()

            # 3. Local Execution (Fallback)
            logger.warning(f"[WorkflowEngine] No Arq pool provided. Running execution {execution_id} LOCALLY (Inline).")
            return await self.execute_workflow_task(execution_id, wf_id, raw_inputs)

        except Exception as e:
            # If submission fails, we log it and re-raise or handle.
            logger.error(f"[WorkflowEngine] Submission failed: {e}")
            raise e
        finally:
            clear_execution_context()

    async def resume_execution(self, execution_id: str) -> dict[str, Any]:
        """Resumes a failed or interrupted execution from its last known trace state.

        Args:
            execution_id (str): The Execution UUID.

        Returns:
            Dict[str, Any]: The final results object.

        Side Effects:
            - **Database**: Re-hydrates state from trace and updates status to 'running'.
            - **Progress Tracker**: Resumes progress tracking from last checkpoint.
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
        """Scans for and resumes jobs that were interrupted (e.g. by server restart).
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
        self, execution_id: str, step_name: str, error: FatalInterruption, state: WorkflowState | None = None
    ) -> dict[str, Any]:
        """Helper to construct a structured response when execution is fatally halted.

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

    async def _resolve_pipeline_steps(self, workflow_id: str) -> list[Any]:
        """Resolves the sequential list of execution steps for a workflow.

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

        return pipeline_steps

    async def _project_final_result(
        self, execution_id: str, state: WorkflowState, pipeline_steps: list[Any]
    ) -> dict[str, Any]:
        """Transforms the final internal state into the public result dictionary.
        Applies logic for field hoisting and Reference Manager scanning.

        Args:
            execution_id (str): Execution ID.
            state (WorkflowState): Final state object.
            pipeline_steps (List[Any]): List of executed steps info.

        Returns:
            Dict[str, Any]: The public facing result object.

        """
        # 1. Start with the architecturally mandated V2 structure via StatePresenter
        from backend.services.state_presenter import StatePresenter

        # We start with the flattened representation
        public_result = StatePresenter.flatten_state(state)
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

    async def _handle_execution_error(self, execution_id: str, error: Exception, state: WorkflowState | None = None):
        """Handles exception logging and state persistence during failure.

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

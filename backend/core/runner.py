"""Workflow Runner (Orchestrator)."""

import inspect
import logging
from datetime import datetime
from typing import Any

from backend.exceptions import AgentExecutionError, FatalInterruption
from backend.models.state import InputData, WorkflowState
from backend.services.usage_service import UsageService

logger = logging.getLogger(__name__)


class PipelineRunner:
    """Responsible for executing the sequential agent loop and individual steps.

    Managed by the WorkflowEngine.
    """

    def __init__(self, repository, registry, prompt_builder):
        """Initializes the PipelineRunner.

        Args:
            repository: Data access layer for executions/workflows.
            registry: Service for agent discovery and configuration.
            prompt_builder: Service for dynamic prompt construction.

        """
        self.repository = repository
        self.registry = registry
        self.prompt_builder = prompt_builder
        # Inject UsageService for cost tracking
        self.usage_service = UsageService(repository)

    async def initialize_state(
        self,
        execution_id: str,
        raw_inputs: dict[str, Any],
        workflow_id: str | None = None,
        workflow_name: str | None = None,
        organization_id: str | None = None,
        user_id: str | None = None,
    ) -> WorkflowState:
        """Constructs the initial WorkflowState object from raw input dictionary.

        Args:
            execution_id (str): The unique ID of the execution.
            raw_inputs (Dict[str, Any]): Inputs provided by the user/API.
            workflow_id (Optional[str]): The workflow ID.
            workflow_name (Optional[str]): The workflow Name.
            organization_id (Optional[str]): The Organization ID.
            user_id (Optional[str]): The User ID.

        Returns:
            WorkflowState: The initialized state object.

        Raises:
            FatalInterruption: If state cannot be initialized.

        """
        try:
            input_data = InputData(
                history_text=raw_inputs.get("history_text", ""),
                product_text=raw_inputs.get("product_text", ""),
                reflection_text=raw_inputs.get("reflection_text", ""),
                bibliography_context=raw_inputs.get("bibliography_context", []),
            )

            current_state = WorkflowState(
                execution_id=execution_id,
                workflow_id=workflow_id,
                workflow_name=workflow_name,
                organization_id=organization_id,  # Populated from Exec Record
                user_id=user_id,  # Populated from Exec Record
                inputs=input_data,
                start_time=datetime.now(),
                audit_results={},
                reasoning_context={},
                last_reasoning_trace=None,
                aux_data={},
            )

            # Inject Global Configuration
            try:
                banned_raw = await self.repository.get_banned_phrases()
                current_state.aux_data["banned_phrases"] = (
                    [r["phrase"].lower() for r in banned_raw] if banned_raw else []
                )
            except Exception as e:
                logger.error(f"[PipelineRunner] Failed to load banned phrases: {e}")
                current_state.aux_data["banned_phrases"] = []

            logger.debug(f"[PipelineRunner] State initialized with inputs: {raw_inputs.keys()}")
            return current_state
        except Exception as e:
            logger.error(f"[PipelineRunner] Failed to initialize state: {e}")
            raise FatalInterruption("StateInitialization", f"Failed to initialize state: {e}", {"error": str(e)}) from e

    async def execute_loop(
        self,
        state: WorkflowState,
        pipeline_steps: list[Any],
        tracker: Any,
        execution_id: str,
        start_index: int = 0,
        total_steps_count: int = 0,
    ) -> Any:
        """Runs the sequential agent loop.

        Args:
            state (WorkflowState): The current workflow state.
            pipeline_steps (List[Any]): List of (AgentInstance, StepDocument) tuples.
            tracker (Any): Progress tracking service instance.
            execution_id (str): The Execution ID.
            start_index (int, optional): Index to start from (resuming). Defaults to 0.
            total_steps_count (int, optional): Total count override. Defaults to 0.

        Returns:
            Any: The final WorkflowState or a dict (if early exit).

        Side Effects:
            - **Database**: Persists state trace via `tracker` at each step.
            - **Logging**: Logs step transitions and progress.
            - **State Mutation**: `current_state` is updated by each step's execution.
        """
        print(f"DEBUG: PipelineRunner.execute_loop START. Steps: {len(pipeline_steps)}", flush=True)
        total_steps = total_steps_count or len(pipeline_steps)
        current_state = state

        for index, (agent, step_doc) in enumerate(pipeline_steps):
            # Absolute step number logic
            current_abs_index = start_index + index
            step_num = current_abs_index + 1

            percent = int((step_num / total_steps) * 100)
            # Fix: Use stable Step ID for UI matching (e.g. 'step_guard')
            stage_name = step_doc.get("id", f"step_{step_num}")
            description = f"Step {step_num}/{total_steps}: {agent.__class__.__name__}"

            # Assign Step ID to state for UI sync
            current_state.current_step_name = stage_name

            # Checkpoint: Save current state to DB (trace)
            trace_dump = current_state.model_dump(mode="json")
            await tracker.update(
                stage=stage_name, percent=percent, details={"trace": trace_dump, "description": description}
            )

            current_state = await self._execute_step(current_state, agent, step_doc, execution_id)

            # Checkpoint: Save state AFTER execution (Capture Usage/Outputs immediately)
            trace_dump = current_state.model_dump(mode="json")
            await tracker.update(
                stage=stage_name,
                percent=percent,
                details={"trace": trace_dump, "description": f"{description} (Completed)"},
            )

            # Check for Early Exit (Security)
            if isinstance(current_state, dict) and "security_alert" in current_state:
                return current_state

        return current_state

    async def _execute_step(
        self, current_state: WorkflowState, agent: Any, step_doc: dict[str, Any], execution_id: str
    ) -> Any:
        """Executes a singe pipeline step: Hooks -> Model Config -> Prompt -> Agent -> Hooks -> Validation.

        Args:
            current_state (WorkflowState): Current state.
            agent (Any): The Agent instance.
            step_doc (Dict[str, Any]): The Step configuration document.
            execution_id (str): Execution ID.

        """
        step_id = step_doc["id"]
        agent_name = agent.__class__.__name__
        # current_state.current_step_name = agent_name  <-- REMOVED (Handled in execute_loop with step_id)
        logger.info(f"[PipelineRunner] Running step: {agent_name} (Step ID: {step_id})")

        # 1. Pre-Hooks
        config = step_doc.get("execution_config") or {}
        print(f"DEBUG: Step {agent_name} Config Hooks: {config.get('pre_hooks')}", flush=True)
        for hook in config.get("pre_hooks") or []:
            print(f"DEBUG: Executing Pre-Hook {hook}", flush=True)
            current_state = await self._execute_hook(hook, agent, current_state)

        # 2. Dynamic Model Selection
        # Pass organization_id from state to ensure correct cost tracking
        model_config = await self._configure_agent_model(
            agent, step_id, execution_id, organization_id=current_state.organization_id
        )

        # 3. Prompt Construction
        system_instruction = await self.prompt_builder.construct_prompt(step_id, current_state) if step_id else None

        # 4. Agent Execution (Async)
        try:
            # Inject repository based on DDD refactoring
            # Pass model configuration (max_tokens, temperature) as kwargs
            exec_kwargs = {
                "system_instruction": system_instruction,
                "repository": self.repository,
                "output_key": step_doc.get("state_key"),  # Pass destination override
                "usage_key": step_id,  # ENSURE GRANULAR COST TRACKING
                "execution_config": config,
                "step_id": step_id,
            }
            if exec_kwargs["output_key"]:
                print(f"DEBUG: EXEC_STEP {step_id} Output Key -> {exec_kwargs['output_key']}", flush=True)

            if model_config:
                if "max_tokens" in model_config:
                    exec_kwargs["max_tokens"] = model_config["max_tokens"]
                if "temperature" in model_config:
                    exec_kwargs["temperature"] = model_config["temperature"]

            current_state = await agent.execute(current_state, **exec_kwargs)

        except Exception as e:
            raise AgentExecutionError(
                detail="AGENT_EXECUTION_FAILED",
                original_error=e,
                agent_name=agent_name,
                step_id=step_id,
            ) from e

        # 5. Post-Hooks
        for hook in config.get("post_hooks") or []:
            current_state = await self._execute_hook(hook, agent, current_state)

        # 6. Validation
        await self._validate_step_output(agent_name, step_id, current_state, step_doc)

        # 7. Update DB - HANDLED BY TRACKER UPSTREAM

        # 8. Security Check
        if current_state.step_guard and current_state.step_guard.security_check.uhka_havaittu:
            return await self._handle_security_intervention(execution_id, current_state)

        # DEBUG TRACE

        return current_state

    async def _execute_hook(self, hook_name: str, agent: Any, state: WorkflowState) -> WorkflowState:
        """Executes a named hook method on the agent instance.

        Args:
            hook_name (str): Name of the method.
            agent (Any): Agent instance.
            state (WorkflowState): Current state.

        Returns:
            WorkflowState: Updated state.

        """
        if hasattr(agent, hook_name):
            logger.debug(f"[PipelineRunner] Executing Hook: {agent.__class__.__name__}.{hook_name}")
            try:
                hook_method = getattr(agent, hook_name)

                # Inspect signature
                sig = inspect.signature(hook_method)
                kwargs = {}

                if "repository" in sig.parameters:
                    kwargs["repository"] = self.repository

                # Check if hook_method is a coroutine function
                if inspect.iscoroutinefunction(hook_method):
                    if kwargs:
                        return await hook_method(state, **kwargs)
                    else:
                        return await hook_method(state)
                else:
                    # Run sync method
                    if kwargs:
                        return hook_method(state, **kwargs)
                    else:
                        return hook_method(state)
            except Exception as e:
                logger.error(f"[PipelineRunner] Hook {hook_name} failed: {e}")
                return state
        else:
            if not hook_name.startswith("parse_"):
                logger.warning(
                    f"[PipelineRunner] Warning: Hook '{hook_name}' not found on Agent "
                    f"{agent.__class__.__name__}. Skipping."
                )
            return state

    async def _configure_agent_model(
        self, agent: Any, step_id: str, execution_id: str, organization_id: str | None = None
    ) -> dict[str, Any]:
        """Resolves the appropriate model strategy for the step and configures the agent.

        Args:
            agent (Any): The Agent instance.
            step_id (str): Step ID.
            agent (Any): The Agent instance.
            step_id (str): Step ID.
            execution_id (str): Execution ID.
            organization_id (Optional[str]): Organization ID for tracking.

        Returns:
            Dict[str, Any]: The resolved model configuration.

        """
        step_model_key = None

        try:
            exec_rec = await self.repository.get_execution(execution_id)
            if exec_rec:
                wf_rec = await self.repository.get_workflow_by_id(exec_rec["workflow_id"])
                if wf_rec:
                    mapping = wf_rec.get("default_model_mapping", {})
                    step_model_key = mapping.get(step_id)
        except Exception as e:
            logger.error(f"[PipelineRunner] Model lookup failed: {e}")
            raise e

        # If still not found (e.g. mapping missing), we could check step_doc
        if not step_model_key:
            # Try getting step config directly again
            step_doc = await self.repository.get_step_by_id(step_id)
            if step_doc:
                config = step_doc.get("execution_config", {})
                step_model_key = config.get("model_strategy")

        if not step_model_key:
            # STRICT MODE: No implicit fallbacks
            msg = (
                f"[PipelineRunner] Critical: No model strategy/mapping found for step '{step_id}'. "
                "Explicit configuration required."
            )
            logger.error(msg)
            raise ValueError(msg)

        resolved_config = await self.registry.resolve_model_config(step_model_key)
        resolved_model_name = resolved_config.get("model_name")
        resolved_provider = resolved_config.get("provider")

        if resolved_model_name and hasattr(agent, "set_model"):
            agent.set_model(
                resolved_model_name,
                provider=resolved_provider,
                usage_service=self.usage_service,
                organization_id=organization_id,
            )
            logger.debug(
                f"[PipelineRunner] Configured {agent.__class__.__name__} with {resolved_model_name} "
                f"(Provider: {resolved_provider})"
            )

        return resolved_config

    async def _validate_step_output(
        self, agent_name: str, step_id: str, state: WorkflowState, step_doc: dict[str, Any]
    ):
        """Validates the step output against the defined component output schema.

        Args:
            agent_name (str): Name of the agent.
            step_id (str): Step ID.
            state (WorkflowState): Current state.
            step_doc (Dict[str, Any]): Step configuration.

        Raises:
            AgentExecutionError: If validation fails.

        """
        output_config_id = step_doc.get("output_config_component")
        if output_config_id:
            comp_record = await self.repository.get_component_by_id(output_config_id)
            if comp_record:
                required_fields = comp_record.get("content", [])
                if isinstance(required_fields, list):
                    state_key = step_doc.get("state_key")
                    if state_key and hasattr(state, state_key):
                        output_obj = getattr(state, state_key)
                        if output_obj:
                            output_data = output_obj.model_dump(mode="json")
                            missing = [f for f in required_fields if "." not in f and f not in output_data]
                            if missing:
                                error_msg = f"Validation Failed: Missing fields {missing} in {agent_name}"
                                logger.error(f"[PipelineRunner] {error_msg}")
                                raise AgentExecutionError(
                                    detail="OUTPUT_VALIDATION_FAILED",
                                    original_error=ValueError(error_msg),
                                    agent_name=agent_name,
                                    step_id=step_id,
                                )

    async def _handle_security_intervention(self, execution_id: str, state: WorkflowState) -> dict[str, Any]:
        """Handles a security check failure by creating a rejection result.

        Args:
            execution_id (str): Execution ID.
            state (WorkflowState): Current state (with audit warning).

        Returns:
            Dict[str, Any]: Rejection details object.

        """
        msg = "[PipelineRunner] SECURITY INTERVENTION: Threat detected."
        logger.critical(msg)

        if not state.step_guard:
            raise ValueError("Security intervention triggered loop, but guard state is missing.")

        rejection_details = {
            "security_alert": "Execution aborted due to security violation.",
            "risk_level": state.step_guard.security_check.riski_taso,
            "analysis": state.step_guard.security_check.adversariaalinen_simulaatio_tulos,
            "guard_data": state.step_guard.model_dump(),
        }

        await self.repository.update_execution(
            execution_id,
            {
                "status": "rejected",
                "error": f"Security Threat Detected: {state.step_guard.security_check.riski_taso}",
                "end_time": datetime.now().isoformat(),
                "result": rejection_details,
            },
        )
        return rejection_details

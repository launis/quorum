"""Profiler Agent implementation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.exceptions import AgentExecutionError, ErrorCodes
from backend.models.domain import ProfilerDTO, ProfilerInput, ProfilerOutput


logger = logging.getLogger(__name__)


class ProfilerAgent(BaseAgent[ProfilerInput, ProfilerOutput]):
    """Profiloija (Psychologist) Agent.

    Step 2.5: Analyzes the 'human' side of the input: intent, biases, tone.
    """

    state_field = "step_profiler"
    REQUIRES_KEYS = ["history_text", "product_text", "reflection_text"]
    PRODUCES_KEYS = ["step_profiler"]
    INPUT_SCHEMA = ProfilerInput
    DTO_SCHEMA = ProfilerDTO
    OUTPUT_SCHEMA = ProfilerOutput

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the expected output schema.

        Returns:
            Optional[Type[BaseModel]]: ProfilerAnalysis schema.

        """
        return ProfilerDTO

    async def execute(
        self,
        input_data: ProfilerInput,
        execution_context: dict[str, Any] | None = None,
        system_instruction: str | None = None,
        **kwargs: Any,
    ) -> ProfilerOutput:
        """Executes the psychological profiling analysis.

        Args:
            input_data (ProfilerInput): Inputs.
            execution_context (dict[str, Any] | None, optional): Context.
            system_instruction (str | None, optional): Prompt.
            **kwargs: Args.

        Returns:
            ProfilerOutput: The psychological profile.

        Raises:
            AgentExecutionError: If mandatory inputs are missing or validation fails.
        """
        # FAIL FAST: Output Control relies on valid input text.
        # Strict Input Validation already handled by BaseAgent (INPUT_SCHEMA).
        # Double check mandatory string content.
        if not input_data.history_text or not input_data.history_text.strip():
            error_msg = "Mandatory input 'history_text' is empty. Assessment aborted."
            logger.error(f"[ProfilerAgent] {error_msg}")
            raise AgentExecutionError(
                detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                original_error=ValueError(error_msg),
                agent_name="ProfilerAgent",
            )

        # 1. VALIDATION (Fail Fast)
        hook_metrics = None
        if input_data.profiler_metrics:
            hook_metrics_dict = input_data.profiler_metrics.model_dump() if hasattr(input_data.profiler_metrics, "model_dump") else input_data.profiler_metrics
            hook_metrics = input_data.profiler_metrics
            logger.info("[ProfilerAgent] Metrics found in input model.")

            # FAIL FAST: Output Control relies on 'control_ratio'
            if "control_ratio" not in hook_metrics_dict:
                logger.warning(
                    "[ProfilerAgent] 'control_ratio' missing in hook_metrics. Output Control may default to unsafe."
                )

            # Force clamp logic for dict
            if "control_ratio" in hook_metrics_dict:
                val = hook_metrics_dict["control_ratio"]
                if isinstance(val, (int, float)) and val > 1.0:
                    logger.warning(f"[ProfilerAgent] Anomaly detected: control_ratio {val} > 1.0. Clamping to 1.0.")

                # Update the pydantic model via model_copy
                if hasattr(hook_metrics, "model_copy"):
                    hook_metrics = hook_metrics.model_copy(update={"control_ratio": min(val, 1.0)})
                else:
                    hook_metrics["control_ratio"] = min(val, 1.0)

        # 2. EXECUTION (LLM)
        try:
            result = await super().execute(
                input_data=input_data,
                execution_context=execution_context,
                system_instruction=system_instruction,
                **kwargs,
            )
        except Exception as e:
            # Re-raise AppExceptions/AgentExecutionErrors as is
            from backend.exceptions import AppException

            if isinstance(e, AppException):
                raise e

            # Re-raise unexpected execution errors with context
            raise AgentExecutionError(
                detail=ErrorCodes.AGENT_EXECUTION_CRITICAL, original_error=e, agent_name="ProfilerAgent"
            ) from e

        # 3. MERGING
        try:
            # MERGE HOOK METRICS (Linguistic) with LLM METRICS (Psychometric)
            if hook_metrics:
                # Handle Pydantic Model (Frozen or not)
                # LLM output metrics (if any) and hook_metrics are now Pydantic models
                current_dict = result.metrics.model_dump() if result.metrics else {}
                hook_dict = hook_metrics.model_dump() if hasattr(hook_metrics, "model_dump") else hook_metrics

                merged_metrics = {**current_dict, **hook_dict}
                result = result.model_copy(update={"metrics": merged_metrics})

            return result

        except Exception as e:
            if isinstance(e, AgentExecutionError):
                raise e
            logger.critical(f"[ProfilerAgent] CRASHED during merging: {e}", exc_info=True)
            raise AgentExecutionError(
                detail=ErrorCodes.AGENT_EXECUTION_CRITICAL, original_error=e, agent_name="ProfilerAgent"
            ) from e

    # _update_state removed. Logic for metrics injection should be in a hook or pre-processing.
    # The 'profiler_metrics' are passed in input_data from the Engine if calculated.

    def post_process(self, response_data: Any) -> Any:
        """Post-process the response data.

        Args:
            response_data (Any): Raw response.

        Returns:
            Any: Processed response.
        """
        # If we need to inject metrics into the response structure before returning:
        # Check execution_context or input_data?
        # Typically the LLM response is returned as is.
        # If 'teksti_metriikka' is missing, it might be added here if we had access to input_data context.
        return response_data

    # NOTE: The analyze_text_metrics hook has been removed (Jan 2026).
    # Hooks are now executed via centralized HOOK_MAPPING in runner.py.
    # The 'calculate_text_metrics' hook is called directly from seed_data.json config.

    def get_user_prompt_template(self) -> str:
        """Returns the user prompt template.

        Returns:
            str: The template string.

        """
        # Override to show we use metrics
        return "Analyze the text. Metrics: {{profiler_metrics}}"

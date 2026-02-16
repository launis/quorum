"""Profiler Agent implementation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.exceptions import AgentExecutionError, ErrorCodes
from backend.models.domain import ProfilerAnalysis

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class ProfilerAgent(BaseAgent):
    """Profiloija (Psychologist) Agent.

    Step 2.5: Analyzes the 'human' side of the input: intent, biases, tone.
    """

    state_field = "step_profiler"
    REQUIRES_KEYS = ["history_text", "product_text", "reflection_text"]
    PRODUCES_KEYS = ["step_profiler"]

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the expected output schema.

        Returns:
            Optional[Type[BaseModel]]: ProfilerAnalysis schema.

        """
        return ProfilerAnalysis


    async def execute(
        self,
        input_data: dict[str, Any],
        execution_context: dict[str, Any] | None = None,
        system_instruction: str | None = None,
        **kwargs: Any,
    ) -> ProfilerAnalysis:
        """Executes the psychological profiling analysis.

        Args:
            input_data (dict[str, Any]): Inputs.
            execution_context (dict[str, Any] | None, optional): Context.
            system_instruction (str | None, optional): Prompt.
            **kwargs: Args.

        Returns:
            ProfilerAnalysis: The psychological profile.

        Raises:
            AgentExecutionError: If mandatory inputs are missing or validation fails.
        """
        # FAIL FAST: Output Control relies on valid input text.
        if not input_data.get("history_text"):
             error_msg = "Mandatory input 'history_text' missing. Assessment aborted."
             logger.error(f"[ProfilerAgent] {error_msg}")
             raise AgentExecutionError(
                 detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                 original_error=ValueError(error_msg),
                 agent_name="ProfilerAgent"
             )

        # 1. VALIDATION (Fail Fast)
        hook_metrics = None
        if "profiler_metrics" in input_data:
             logger.info(f"[ProfilerAgent] Input Context Keys: {list(input_data.keys())}")
             logger.info(f"[ProfilerAgent] Metrics found: {input_data['profiler_metrics']}")

             hook_metrics = input_data["profiler_metrics"]
             if not isinstance(hook_metrics, dict):
                 logger.error(f"[ProfilerAgent] Invalid profiler_metrics type: {type(hook_metrics)}")
                 # Fail Fast on Integration Type Error
                 raise AgentExecutionError(
                     detail=ErrorCodes.INVALID_JSON_PAYLOAD,
                     original_error=TypeError(f"ProfilerAgent received invalid metrics type: {type(hook_metrics)}"),
                     agent_name="ProfilerAgent"
                 )

             # FAIL FAST: Output Control relies on 'control_ratio'
             if "control_ratio" not in hook_metrics:
                  logger.warning("[ProfilerAgent] 'control_ratio' missing in hook_metrics. Output Control may default to unsafe.")

             # Force clamp logic for dict
             if "control_ratio" in hook_metrics:
                 val = hook_metrics["control_ratio"]
                 if isinstance(val, (int, float)) and val > 1.0:
                     logger.warning(f"[ProfilerAgent] Anomaly detected: control_ratio {val} > 1.0. Clamping to 1.0.")
                     hook_metrics["control_ratio"] = 1.0

        # 2. EXECUTION (LLM)
        try:
            result = await super().execute(
                input_data=input_data,
                execution_context=execution_context,
                system_instruction=system_instruction,
                **kwargs
            )
        except Exception as e:
            # Re-raise AppExceptions/AgentExecutionErrors as is
            from backend.exceptions import AppException
            if isinstance(e, AppException):
                raise e

            # Re-raise unexpected execution errors with context
            raise AgentExecutionError(
                detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                original_error=e,
                agent_name="ProfilerAgent"
            ) from e

        # 3. MERGING
        try:
             # MERGE HOOK METRICS (Linguistic) with LLM METRICS (Psychometric)
             if hook_metrics:
                 if isinstance(result, BaseModel):
                     # Handle Pydantic Model (Frozen or not)
                     # We use model_copy to safely update even if frozen
                     current_metrics = getattr(result, "metrics", {}) or {}
                     merged_metrics = {**current_metrics, **hook_metrics}
                     result = result.model_copy(update={"metrics": merged_metrics})
                 else:
                     # FAIL FAST: Strict Mode - Agent MUST return BaseModel
                     raise AgentExecutionError(
                         detail=ErrorCodes.INVALID_JSON_PAYLOAD,
                         original_error=TypeError(f"ProfilerAgent returned {type(result)} instead of ProfilerAnalysis."),
                         agent_name="ProfilerAgent"
                     )

             return result

        except Exception as e:
            if isinstance(e, AgentExecutionError):
                raise e
            logger.critical(f"[ProfilerAgent] CRASHED during merging: {e}", exc_info=True)
            raise AgentExecutionError(
                detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                original_error=e,
                agent_name="ProfilerAgent"
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

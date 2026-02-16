"""Logician Agent implementation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.exceptions import AgentExecutionError, ErrorCodes
from backend.models.domain import LogicianOutput

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class LogicianAgent(BaseAgent):
    """Loogikko-agentti (Logician Agent).

    Responsible for:
    1. Argument Construction (Argumentaation Rakentaminen)
    2. Applying Cognitive Assessment Matrix (Bloom/Toulmin)
    """

    state_field = "step_logician"
    PRODUCES_KEYS = ["step_logician"]

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the expected output schema.

        Returns:
            type[BaseModel] | None: LogicianOutput schema.
        """
        return LogicianOutput

    async def prepare_context(
        self,
        input_data: dict[str, Any],
        execution_context: dict[str, Any] | None,
        **kwargs: Any
    ) -> str | None:
        """Lifecycle Hook: Pre-Execution.

        Injects the Evidence Map (AnalystOutput) from the Analyst step.

        Args:
            input_data (dict[str, Any]): Inputs.
            execution_context (dict[str, Any] | None): Context.
            **kwargs: execution arguments.

        Returns:
            str | None: Formatted context string or None.

        Raises:
            ValueError: If mandatory inputs (Analyst Output or History Text) are missing.
        """
        # 1. Resolve Input (Prefer kwargs from wiring, then input_data)
        analyst_output = kwargs.get("step_analyst")
        if not analyst_output:
            analyst_output = input_data.get("step_analyst")

        if not analyst_output:
            # Check for direct text input as fallback (e.g. from single-step test)
            # But mandate at least ONE source of truth.
            raw_text = input_data.get("history_text") or input_data.get("input_text") or kwargs.get("history_text")

            if not raw_text:
                # FAIL FAST: Logician cannot construct arguments without ANY evidence.
                error_code = ErrorCodes.AGENT_EXECUTION_CRITICAL
                logger.error(f"[LogicianAgent] {error_code}: Missing 'step_analyst' AND 'history_text'.")
                # Raise AgentExecutionError for strictness matching other agents
                raise AgentExecutionError(
                    detail=error_code,
                    original_error=ValueError("LogicianAgent: Missing mandatory input 'step_analyst' (Evidence Map) or 'history_text'. Cannot construct arguments from nothing."),
                    agent_name="LogicianAgent"
                )

        # 2. Format Context
        if analyst_output:
            content = (
                analyst_output.model_dump_json(indent=2)
                if hasattr(analyst_output, "model_dump_json")
                else str(analyst_output)
            )
            return f"### TODISTUSKARTTA (EVIDENCE MAP):\n{content}"

        return None

    async def execute(
        self,
        input_data: dict[str, Any],
        execution_context: dict[str, Any] | None = None,
        system_instruction: str | None = None,
        **kwargs: Any,
    ) -> LogicianOutput:
        """Executes argument reconstruction and cognitive assessment.

        Args:
            input_data (dict[str, Any]): Inputs.
            execution_context (dict[str, Any] | None, optional): Context.
            system_instruction (str | None, optional): Prompt.
            **kwargs: Args.

        Returns:
            LogicianOutput: Argument structures.

        Raises:
            AgentExecutionError: On failure.
        """
        # Call BaseAgent.execute which handles LLM, JSON parsing, healing, and validation against OUTPUT_SCHEMA
        # BaseAgent.execute returns Any (dict or Model).
        # We must cast or validate if we want strict typing in code.
        result = await super().execute(input_data, execution_context, system_instruction, **kwargs)

        if isinstance(result, LogicianOutput):
            return result
        elif isinstance(result, dict):
            # Should have been validated by base, but double check
            return LogicianOutput(**result)
        else:
            raise AgentExecutionError(
                detail=ErrorCodes.INVALID_JSON_PAYLOAD,
                original_error=TypeError(f"LogicianAgent returned {type(result)} instead of LogicianOutput"),
                agent_name="LogicianAgent"
            )



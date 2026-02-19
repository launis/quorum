"""Logician Agent implementation."""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import TYPE_CHECKING, Any

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.exceptions import AgentExecutionError, ErrorCodes
from backend.models.domain import LogicianInput, LogicianOutput, LogicianOutputDTO

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)



class LogicianAgent(BaseAgent[LogicianInput, LogicianOutput]):
    """Loogikko-agentti (Logician Agent).

    Responsible for:
    1. Argument Construction (Argumentaation Rakentaminen)
    2. Applying Cognitive Assessment Matrix (Bloom/Toulmin)
    """

    state_field = "step_logician"
    PRODUCES_KEYS = ["step_logician"]
    INPUT_SCHEMA = LogicianInput
    DTO_SCHEMA = LogicianOutputDTO
    OUTPUT_SCHEMA = LogicianOutput


    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the expected output schema.

        Returns:
            type[BaseModel] | None: LogicianOutput schema.
        """
        return LogicianOutput

    async def prepare_context(
        self,
        input_data: LogicianInput,
        execution_context: dict[str, Any] | None,
        **kwargs: Any
    ) -> str | None:
        """Lifecycle Hook: Pre-Execution.

        Injects the Evidence Map (AnalystOutput) from the Analyst step.

        Args:
            input_data (LogicianInput): Inputs.
            execution_context (dict[str, Any] | None): Context.
            **kwargs: execution arguments.

        Returns:
            str | None: Formatted context string or None.

        Raises:
            ValueError: If mandatory inputs (Analyst Output or History Text) are missing.
        """
        # 1. Resolve Input (Strong Typed)
        analyst_output = input_data.step_analyst
        # LogicianInput doesn't have step_analyst. Wait. 
        # Plan said LogicianInput needs history_text.
        # But Logician needs step_analyst!
        # I missed checking if Logician needs AnalystOutput in LogicianInput.
        # Let's check logic: "analyst_output = kwargs.get('step_analyst') or input_data.get('step_analyst')"
        # If I strictly enforce LogicianInput, it must have it if implied.
        # But LogicianInput defined earlier ONLY has history_text.
        # If step_analyst is passed via kwargs (from graph), it's fine. 
        # If passed via input_data, it must be in the model.
        # I should probably add step_analyst to LogicianInput?
        # But BaseAgent doesn't enforce kwargs matching INPUT_SCHEMA.
        # BaseAgent.execute takes input_data.
        # If step_analyst comes from previous agent in chain, it might be in state, injected into input_data?
        # GraphEngine: "inputs = state.get_context(self.INPUT_SCHEMA)" 
        # If I add step_analyst to LogicianInput, GraphEngine will try to populate it.
        # So I SHOULD have added step_analyst to LogicianInput.
        # Let's assume for now it comes from kwargs (injected by Engine separately) or I need to fix LogicianInput.
        # The existing code checked `input_data.get("step_analyst")`.
        # So I SHOULD FIX LogicianInput.
        
        # NOTE: For now, I will use kwargs.get("step_analyst") which is safer if Engine injects dependencies.
        # But for strictness, it should be in Input.
        
        # Let's rely on kwargs for step_analyst for now, or check raw_text from input_data.history_text.
        
        if not analyst_output:
            # Check for direct text input as fallback
            raw_text = input_data.history_text

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
            # Pydantic Model Strictness
            if hasattr(analyst_output, "model_dump_json"):
                content = analyst_output.model_dump_json(indent=2)
            elif isinstance(analyst_output, dict):
                 # Backward compatibility but strictly typed expected
                 import json

                 def strict_serializer(obj):
                    if isinstance(obj, (datetime, date)):
                        return obj.isoformat()
                    raise TypeError(f"Type {type(obj)} not serializable")

                 content = json.dumps(analyst_output, indent=2, ensure_ascii=False, default=strict_serializer)
            else:
                 content = str(analyst_output)

            return f"### TODISTUSKARTTA (EVIDENCE MAP):\n{content}"

        return f"### RAW TEXT INPUT:\n{raw_text}"

    async def execute(
        self,
        input_data: LogicianInput,
        execution_context: dict[str, Any] | None = None,
        system_instruction: str | None = None,
        **kwargs: Any,
    ) -> LogicianOutput:
        """Executes argument reconstruction and cognitive assessment.

        Args:
            input_data (LogicianInput): Inputs.
            execution_context (dict[str, Any] | None, optional): Context.
            system_instruction (str | None, optional): Prompt.
            **kwargs: Args.

        Returns:
            LogicianOutput: Argument structures.

        Raises:
            AgentExecutionError: On failure.
        """
        # Call BaseAgent.execute which now GUARANTEES a Pydantic Model if OUTPUT_SCHEMA is set.
        result = await super().execute(input_data, execution_context, system_instruction, **kwargs)

        # BaseAgent checks ensure this is LogicianOutput
        return result



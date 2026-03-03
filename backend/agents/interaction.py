"""Interaction Analyst Agent implementation."""

from __future__ import annotations

import logging
from typing import Any

# 2. Third Party
from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.exceptions import AgentExecutionError, ErrorCodes
from backend.models.domain import InteractionAnalysis, InteractionAnalysisDTO, InteractionInput

logger = logging.getLogger(__name__)


class InteractionAnalystAgent(BaseAgent[InteractionInput, InteractionAnalysis]):
    """InteractionAnalystAgent (Vuorovaikutusanalysaattori).

    Analyses the 'history_text' to evaluate Prompt Engineering competence.
    Hybrid logic:
    - AI: Qualitative analysis (Strategies, Role Classification: Passenger/Navigator/Driver/Architect).
    - Python: Quantitative analysis (Input Control Ratio).
    """

    state_field = "step_interaction"
    REQUIRES_KEYS = ["history_text"]

    INPUT_SCHEMA = InteractionInput
    DTO_SCHEMA = InteractionAnalysisDTO
    OUTPUT_SCHEMA = InteractionAnalysis

    async def execute(
        self,
        input_data: InteractionInput,
        execution_context: dict[str, Any] | None = None,
        system_instruction: str | None = None,
        **kwargs: Any,
    ) -> InteractionAnalysis:
        """Executes interaction analysis (Driver/Passenger classification).

        Args:
            input_data (InteractionInput): Inputs including history_text.
            execution_context (dict): Context.
            system_instruction (str): Prompt.
            **kwargs: Args.

        Returns:
            InteractionAnalysis: InteractionAnalysis.

        Raises:
            AgentExecutionError: If mandatory input is missing or validation fails.
        """
        # FAIL FAST: Interaction Analysis requires conversation history.
        if not input_data.history_text:
            # This prevents analyzing empty context "hallucinations".
            error_msg = "InteractionAnalystAgent: Mandatory input 'history_text' missing."
            logger.error(f"[InteractionAnalystAgent] {ErrorCodes.AGENT_EXECUTION_CRITICAL}: {error_msg}")
            raise AgentExecutionError(
                detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                original_error=ValueError(error_msg),
                agent_name="InteractionAnalystAgent",
            )

        # Note: Control ratio is now calculated via centralized HOOK_MAPPING (pre_hooks in seed_data.json)
        result_obj = await super().execute(input_data, execution_context, system_instruction, **kwargs)

        if isinstance(result_obj, InteractionAnalysis):
            return result_obj
        else:
            raise AgentExecutionError(
                detail=ErrorCodes.INVALID_JSON_PAYLOAD,
                original_error=TypeError(
                    f"InteractionAnalystAgent returned {type(result_obj)} instead of InteractionAnalysis"
                ),
                agent_name="InteractionAnalystAgent",
            )

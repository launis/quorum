"""XAI Reporter Agent implementation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.models.domain import XAIReport

if TYPE_CHECKING:
    from backend.models.state import WorkflowState

logger = logging.getLogger(__name__)


class XAIReporterAgent(BaseAgent):
    """XAI-Raportoija-agentti (XAI Reporter Agent).

    Responsible for generating the final, explainable report.
    """

    state_field = "step_reporter"
    REQUIRES_KEYS = ["step_judge"]

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the expected output schema.

        Use the Domain Model directly to ensure strict validation.
        The dynamic generation was causing issues with Optional fields and Type mismatches.

        Returns:
            Optional[Type[BaseModel]]: XAIReport schema.

        """
        return XAIReport

    async def prepare_context(self, input_data: dict, execution_context: dict | None, **kwargs) -> str | None:
        """Lifecycle Hook: Pre-Execution.

        Prepares the context for the XAI Reporter by extracting and formatting
        the Judge's evaluation results from the new Standardized Schema.

        Args:
            input_data (dict): Inputs.
            execution_context (dict): Config.
            **kwargs: Args.

        Returns:
            str: Context string.
        """
        judge_result = input_data.get("step_judge")
        if not judge_result:
             logger.warning("[XAIReporterAgent] No 'step_judge' data found in inputs.")
             return None
        
        # If it's a Pydantic model, dump it; if dict, use as is.
        # The result should be EvaluationResult format (Unified Contract).
        if hasattr(judge_result, "model_dump"):
            data = judge_result.model_dump()
        else:
            data = judge_result

        # Format Context
        lines = ["### AUDIT RESULTS (EVALUATION):"]
        
        # 1. Total Score
        total_score = data.get("total_score", "N/A")
        lines.append(f"- **Total Score**: {total_score}")
        
        # 2. Dimensions (Replacing legacy 'pisteet' access)
        dimensions = data.get("dimensions", [])
        if dimensions:
            lines.append("\n#### Dimensions:")
            for dim in dimensions:
                d_id = dim.get("dimension_id", "uknown").capitalize()
                score = dim.get("score", "-")
                reason = dim.get("reasoning", "")
                lines.append(f"- **{d_id}**: {score}/5 - {reason}")
        else:
             # Fallback check for legacy 'pisteet' just in case normalization was skipped (Unlikely)
             pisteet = data.get("pisteet")
             if pisteet:
                 lines.append("\n#### Dimensions (Legacy):")
                 for key, val in pisteet.items():
                     if val:
                         lines.append(f"- **{key}**: {val.get('arvosana')}/5 - {val.get('perustelu')}")

        # 3. Critical Findings
        crit_findings = data.get("critical_findings", [])
        if crit_findings:
            lines.append("\n#### Critical Findings:")
            for item in crit_findings:
                lines.append(f"- {item}")
        
        return "\n".join(lines)

    async def execute(
        self,
        input_data: dict,
        execution_context: dict | None = None,
        system_instruction: str | None = None,
        **kwargs,
    ) -> dict:
        """Executes the XAI Reporter Agent logic.

        Args:
            input_data (dict): Inputs.
            execution_context (dict): Context.
            system_instruction (str): Prompt.
            **kwargs: Args.

        Returns:
            dict: The final report.
        """
        return await super().execute(input_data, execution_context, system_instruction, **kwargs)


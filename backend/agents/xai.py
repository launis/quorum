"""XAI Reporter Agent implementation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.models.domain import XAIReport, ScoreCardItem, DimensionResultItem

if TYPE_CHECKING:
    from backend.models.state import WorkflowState

logger = logging.getLogger(__name__)


class XAIReporterAgent(BaseAgent):
    """XAI-Raportoija-agentti (XAI Reporter Agent).

    Responsible for generating the final, explainable report.
    """

    state_field = "step_xai"
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
        judge_result = input_data.get("step_judge") or input_data.get("tuomio")
        if not judge_result:
             logger.warning("[XAIReporterAgent] No 'step_judge' or 'tuomio' data found in inputs.")
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
                max_val = data.get("scale_max", 5)
                lines.append(f"- **{d_id}**: {score}/{max_val} - {reason}")
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
        # 1. Generate the base report via LLM (super)
        result = await super().execute(input_data, execution_context, system_instruction, **kwargs)
        
        # 2. Aggregate Scores from any Judge Outputs found in input_data
        score_cards = []
        
        for key, value in input_data.items():
            if (key.startswith("step_judge") or key == "tuomio") and isinstance(value, (dict, BaseModel)):
                try:
                    # Normalize to dict
                    data = value.model_dump() if hasattr(value, "model_dump") else value
                    
                    # Extract Name
                    # Prefer matrix_id if available, otherwise format the step key
                    matrix_id = data.get("matrix_id")
                    if matrix_id:
                        agent_name = f"Judge ({matrix_id})"
                    else:
                        # "step_judge_cognitive" -> "Cognitive Judge"
                        parts = key.split("_")
                        if len(parts) > 2:
                            agent_name = f"{parts[2].capitalize()} Judge"
                        else:
                            agent_name = "Standard Judge"

                    # Extract Score Data
                    total_score = float(data.get("total_score", 0))
                    max_score = int(data.get("scale_max", 5))
                    
                    # Extract Dimensions
                    dimensions = []
                    raw_dims = data.get("dimensions", [])
                    
                    if raw_dims:
                        # V2: List of DimensionResultItems
                        for d in raw_dims:
                            # Handle both dict and object (if somehow mixed)
                            d_data = d if isinstance(d, dict) else d.__dict__
                            dimensions.append(
                                DimensionResultItem(
                                    dimension_id=d_data.get("dimension_id", "unknown"),
                                    score=d_data.get("score", 0),
                                    reasoning=d_data.get("reasoning", "")
                                )
                            )


                    # Extract Verdict
                    # V2: 'final_verdict' is not intrinsically on EvaluationResult, usually it's just scores.
                    # But if we have it, great. If not, summarise.
                    verdict = data.get("final_verdict")
                    if not verdict:
                        # Create a mini verdict
                        verdict = f"Score: {total_score}/{max_score}"

                    score_cards.append(
                        ScoreCardItem(
                            agent_name=agent_name,
                            total_score=total_score,
                            max_score=max_score,
                            verdict=verdict,
                            dimensions=dimensions
                        )
                    )
                    
                except Exception as e:
                    logger.warning(f"[XAIReporter] Failed to process scorecard for {key}: {e}")

        # 3. Inject into Result
        # Result is likely a dict from BaseAgent.execute logic processing the LLM response
        if isinstance(result, dict):
            # Check if 'score_cards' already exists (model might have predicted it empty)
            # We override/extend it with authoritative data ONLY if we found data.
            # This preserves MOCK data which might be present in the result when inputs are missing.
            if score_cards:
                result["score_cards"] = score_cards
        
        return result


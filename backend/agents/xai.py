"""XAI Reporter Agent implementation."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.models.domain import DimensionResultItem, ScoreCardItem, XAIReport

if TYPE_CHECKING:
    pass

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
        # Aggregate Judge Results from potentially multiple judges (Dual Chain)
        judge_results = []
        for key, value in input_data.items():
             if (key.startswith("step_judge") or key == "tuomio") and value:
                 # Normalize
                 data = value.model_dump() if hasattr(value, "model_dump") else value
                 
                 # Identify Judge Name
                 matrix_id = data.get("matrix_id")
                 if not matrix_id:
                     logger.error(f"[XAIReporterAgent] Strict Mode Violation: 'matrix_id' missing in {key}. Cannot identify judge.")
                     raise ValueError(f"Strict XAI: Judge output in '{key}' is missing 'matrix_id'. Agent must return matrix_id.")
                 
                 name = f"Judge ({matrix_id})"
                 
                 judge_results.append((name, data))

        if not judge_results:
             logger.warning("[XAIReporterAgent] No 'step_judge' or 'tuomio' data found in inputs.")
             return None

        # Format Context
        lines = ["### AUDIT RESULTS (EVALUATION):"]
        
        for name, data in judge_results:
            lines.append(f"\n#### EVALUATION FROM: {name}")

            # 1. Total Score
            total_score = data.get("total_score", "N/A")
            lines.append(f"- **Total Score**: {total_score}")

            # 2. Dimensions
            dimensions = data.get("dimensions", [])
            if dimensions:
                lines.append("  **Dimensions:**")
                for dim in dimensions:
                    # Handle dict vs object properties if necessary (usually dict here)
                    d_data = dim if isinstance(dim, dict) else dim.__dict__
                    
                    d_id = d_data.get("dimension_id", "unknown").capitalize()
                    score = d_data.get("score", "-")
                    reason = d_data.get("reasoning", "")
                    
                    max_val = data.get("scale_max", "UNKNOWN")
                    lines.append(f"  - **{d_id}**: {score}/{max_val} - {reason}")
            else:
                 # Fallback check for legacy 'pisteet'
                 pisteet = data.get("pisteet")
                 if pisteet:
                     lines.append("  **Dimensions (Legacy):**")
                     for key, val in pisteet.items():
                         if val:
                             lines.append(f"  - **{key}**: {val.get('arvosana')}/5 - {val.get('perustelu')}")

            # 3. Critical Findings
            crit_findings = data.get("critical_findings", [])
            if crit_findings:
                lines.append("  **Critical Findings:**")
                for item in crit_findings:
                    lines.append(f"  - {item}")
            
            lines.append("---") # Separator between judges

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
                    if not matrix_id:
                         raise ValueError(f"Strict XAI: Judge output in '{key}' is missing 'matrix_id'. Cannot build ScoreCard.")
                    
                    agent_name = f"Judge ({matrix_id})"

                    # Extract Score Data
                    total_score = float(data.get("total_score", 0))
                    max_val_raw = data.get("scale_max")
                    if max_val_raw is None:
                         raise ValueError(f"CRITICAL: Missing 'scale_max' in Judge Output for {key}. Cannot build ScoreCard.")
                    max_score = int(max_val_raw)

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
                                    dimension_label=d_data.get("dimension_label", ""),
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


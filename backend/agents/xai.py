from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.exceptions import AgentExecutionError, ErrorCodes
from backend.models.domain import DimensionResultItem, JudgeScoreCard, XAIOutput

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class XAIReporterAgent(BaseAgent):
    """XAI-Raportoija-agentti (XAI Reporter Agent).

    Responsible for generating the final, explainable report.
    """

    state_field = "step_xai"
    REQUIRES_KEYS = [] # Dynamic validation in execute() supports step_judge OR step_judge_cognitive

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the expected output schema.

        Use the Domain Model directly to ensure strict validation.
        The dynamic generation was causing issues with Optional fields and Type mismatches.

        Returns:
            type[BaseModel] | None: XAIOutput schema.
        """
        return XAIOutput

    async def prepare_context(
        self,
        input_data: dict[str, Any],
        execution_context: dict[str, Any] | None,
        **kwargs: Any
    ) -> str | None:
        """Lifecycle Hook: Pre-Execution.

        Prepares the context for the XAI Reporter by extracting and formatting
        the Judge's evaluation results from the new Standardized Schema.

        Args:
            input_data (dict[str, Any]): Inputs.
            execution_context (dict[str, Any] | None): Config.
            **kwargs: Args.

        Returns:
            str | None: Context string.

        Raises:
            ValueError: If Strict Mode violations occur in judge output.
        """
        # Aggregate Judge Results from potentially multiple judges (Dual Chain)
        judge_results = []
        for key, value in input_data.items():
             if key.startswith("step_judge") and value:
                 # Normalize
                 data = value.model_dump() if hasattr(value, "model_dump") else value

                 # Identify Judge Name
                 matrix_id = data.get("matrix_id")
                 if not matrix_id:
                     error_msg = f"Strict XAI: Judge output in '{key}' is missing 'matrix_id'. Agent must return matrix_id."
                     logger.error(f"[XAIReporterAgent] Strict Mode Violation: {error_msg}")
                     raise AgentExecutionError(
                         detail=ErrorCodes.INVALID_JSON_PAYLOAD,
                         original_error=ValueError(error_msg),
                         agent_name="XAIReporterAgent"
                     )

                 name = f"Judge ({matrix_id})"

                 judge_results.append((name, data))
                 logger.info(f"[XAIReporterAgent] Found Judge Output: {name}")

        if not judge_results:
             logger.warning("[XAIReporterAgent] No 'step_judge*' data found in inputs.")
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
                 # Strict Mode: No fallback for legacy 'pisteet'.
                 pass

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
        input_data: dict[str, Any],
        execution_context: dict[str, Any] | None = None,
        system_instruction: str | None = None,
        **kwargs: Any,
    ) -> XAIOutput:
        """Executes the XAI Reporter Agent logic.

        Args:
            input_data (dict[str, Any]): Inputs.
            execution_context (dict[str, Any] | None, optional): Context.
            system_instruction (str | None, optional): Prompt.
            **kwargs: Args.

        Returns:
            XAIOutput: The final report.

        Raises:
            AgentExecutionError: If mandatory inputs are missing or invalid.
        """
        # FAIL FAST: XAI requires Judge outputs
        has_judge_data = any(k.startswith("step_judge") for k in input_data.keys())
        if not has_judge_data:
             error_msg = "Mandatory input 'step_judge' or 'step_judge_cognitive' missing. Reporting aborted."
             logger.error(f"[XAIReporterAgent] {error_msg}")
             raise AgentExecutionError(
                 detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                 original_error=ValueError(error_msg),
                 agent_name="XAIReporterAgent"
             )

        # 1. Generate the base report via LLM (super)
        result = await super().execute(input_data, execution_context, system_instruction, **kwargs)

        # 2. Aggregate Scores from any Judge Outputs found in input_data
        score_cards = []

        for key, value in input_data.items():
            if key.startswith("step_judge") and isinstance(value, (dict, BaseModel)):
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
                        JudgeScoreCard(
                            agent_name=agent_name,
                            total_score=total_score,
                            max_score=max_score,
                            verdict=verdict,
                            dimensions=dimensions
                        )
                    )

                except Exception as e:
                    # FAIL FAST: Do not swallow errors in strict coding standards.
                    logger.error(f"[XAIReporter] Failed to process scorecard for {key}: {e}", exc_info=True)
                    raise AgentExecutionError(
                        detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                        original_error=e,
                        agent_name="XAIReporterAgent"
                    ) from e

        # 3. Inject into Result
        # STRICT MODE: Result must be a BaseModel (XAIOutput). Dictionaries are BANNED.
        if score_cards:
            if isinstance(result, BaseModel):
                # We expect the model to have 'score_cards' field.
                # We create a new instance with the updated field.
                # Note: This replaces any existing score_cards from the LLM (which is desired).
                result = result.model_copy(update={"score_cards": score_cards})
            else:
                 # If result is a dict (Violation of Mandate), we fail fast.
                 raise AgentExecutionError(
                     detail=ErrorCodes.INVALID_JSON_PAYLOAD,
                     original_error=TypeError(f"Agent returned {type(result)}, expected BaseModel."),
                     agent_name="XAIReporterAgent"
                 )

        return result


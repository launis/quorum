from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

# 2. Third Party
from pydantic import BaseModel

from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.exceptions import AgentExecutionError, ErrorCodes
from backend.models.domain import JudgeScoreCard, XAIOutput, XAIReporterInput

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class XAIReporterAgent(BaseAgent[XAIReporterInput, XAIOutput]):
    """XAI-Raportoija-agentti (XAI Reporter Agent).

    Responsible for generating the final, explainable report.
    """

    state_field = "step_xai"
    REQUIRES_KEYS = []  # Dynamic validation in execute() supports step_judge OR step_judge_cognitive

    INPUT_SCHEMA = XAIReporterInput
    OUTPUT_SCHEMA = XAIOutput

    def get_response_schema(self) -> type[BaseModel] | None:
        """Returns the expected output schema.

        Use the Domain Model directly to ensure strict validation.
        The dynamic generation was causing issues with Optional fields and Type mismatches.

        Returns:
            type[BaseModel] | None: XAIOutput schema.
        """
        return XAIOutput

    async def prepare_context(
        self, input_data: XAIReporterInput, execution_context: dict[str, Any] | None, **kwargs: Any
    ) -> str | None:
        """Lifecycle Hook: Pre-Execution.

        Prepares the context for the XAI Reporter by extracting and formatting
        the Judge's evaluation results from the new Standardized Schema.

        Args:
            input_data (XAIReporterInput): Inputs.
            execution_context (dict[str, Any] | None): Config.
            **kwargs: Args.

        Returns:
            str | None: Context string.

        Raises:
            ValueError: If Strict Mode violations occur in judge output.
        """
        # Aggregate Judge Results from potentially multiple judges (Dual Chain)
        judge_results = []

        # Convert Pydantic model to dict to iterate over dynamic fields (step_judge*)
        # XAIReporterInput uses extra="allow" to support these.
        input_dict = input_data.model_dump()

        for key, value in input_dict.items():
            if key.startswith("step_judge") and value:
                # Normalize (if it's a nested model, dump it too)
                data = value.model_dump() if hasattr(value, "model_dump") else value

                # If value is just a dict (from input_dict), it's already a dict.
                # But check if it was a model originally. input_data.model_dump() converts sub-models to dicts usually.

                # Identify Judge Name
                matrix_id = data.get("matrix_id")
                if not matrix_id:
                    error_msg = (
                        f"Strict XAI: Judge output in '{key}' is missing 'matrix_id'. Agent must return matrix_id."
                    )
                    logger.error(f"[XAIReporterAgent] Strict Mode Violation: {error_msg}")
                    raise AgentExecutionError(
                        detail=ErrorCodes.INVALID_JSON_PAYLOAD,
                        original_error=ValueError(error_msg),
                        agent_name="XAIReporterAgent",
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

            lines.append("---")  # Separator between judges

        return "\n".join(lines)

    async def execute(
        self,
        input_data: XAIReporterInput,
        execution_context: dict[str, Any] | None = None,
        system_instruction: str | None = None,
        **kwargs: Any,
    ) -> XAIOutput:
        """Executes the XAI Reporter Agent logic.

        Args:
            input_data (XAIReporterInput): Inputs.
            execution_context (dict[str, Any] | None, optional): Context.
            system_instruction (str | None, optional): Prompt.
            **kwargs: Args.

        Returns:
            XAIOutput: The final report.

        Raises:
            AgentExecutionError: If mandatory inputs are missing or invalid.
        """
        # Convert to dict for dynamic field access
        input_dict = input_data.model_dump()

        # FAIL FAST: XAI requires Judge outputs
        has_judge_data = any(k.startswith("step_judge") for k in input_dict.keys())
        if not has_judge_data:
            error_msg = "Mandatory input 'step_judge' or 'step_judge_cognitive' missing. Reporting aborted."
            logger.error(f"[XAIReporterAgent] {error_msg}")
            raise AgentExecutionError(
                detail=ErrorCodes.AGENT_EXECUTION_CRITICAL,
                original_error=ValueError(error_msg),
                agent_name="XAIReporterAgent",
            )

        # 1. Generate the base report via LLM (super)
        result = await super().execute(input_data, execution_context, system_instruction, **kwargs)

        # 2. Aggregate Scores from any Judge Outputs found in input_data
        score_cards = []

        for key, value in input_dict.items():
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
                        raise ValueError(
                            f"Strict XAI: Judge output in '{key}' is missing 'matrix_id'. Cannot build ScoreCard."
                        )

                    agent_name = f"Judge ({matrix_id})"

                    # Extract Score Data (Strict Phase 8 Standard)
                    score_card_data = data.get("score_card")
                    if not score_card_data:
                        # FAIL FAST: JudgeOutput MUST have score_card.
                        # This prevents default 0.0 scores or invalid data ingestion.
                        raise AgentExecutionError(
                            detail=ErrorCodes.INVALID_OUTPUT_SCHEMA,
                            original_error=ValueError(
                                f"Strict XAI: Judge output in '{key}' is missing 'score_card'. Legacy flat structure is forbidden."
                            ),
                            agent_name="XAIReporterAgent",
                        )

                    # Standard Extraction from ScoreCard
                    total_score = float(score_card_data.get("total_score", 0.0))
                    max_val_raw = score_card_data.get("scale_max") or score_card_data.get("max_score")

                    if max_val_raw is None:
                        # Fallback to root level scale_max if missing in card (data.get("scale_max"))
                        # But strictly, it should be in the card. Let's allow root fallback ONLY if missing in card for now.
                        max_val_raw = data.get("scale_max")

                    max_score = int(max_val_raw) if max_val_raw is not None else 5

                    verdict = score_card_data.get("verdict")
                    if not verdict:
                        verdict = "Verdict missing" # STRICT DTO: verdict is required and cannot be empty

                    dimensions = score_card_data.get("dimensions", [])
                    scale_min = float(score_card_data.get("scale_min", 0.0))
                    scale_max = float(score_card_data.get("scale_max", max_score))

                    # Strict type forcing for dimensions array just in case LLM gave us dicts that don't pass
                    from backend.models.domain.judge import DimensionResultItem
                    cleaned_dimensions = []
                    for d in dimensions:
                        if isinstance(d, dict):
                            # Default missing fields for strictly required dimension keys
                            cleaned_dimensions.append(
                                DimensionResultItem(
                                    dimension_id=d.get("dimension_id", "unknown"),
                                    dimension_label=d.get("dimension_label", d.get("dimension_id", "Unknown")),
                                    score=float(d.get("score", 0.0)),
                                    reasoning=d.get("reasoning", "No reasoning provided.")
                                )
                            )
                        elif isinstance(d, DimensionResultItem):
                            cleaned_dimensions.append(d)

                    score_cards.append(
                        JudgeScoreCard(
                            agent_name=agent_name,
                            total_score=total_score,
                            max_score=max_score,
                            verdict=verdict,
                            dimensions=cleaned_dimensions,
                            scale_min=scale_min,
                            scale_max=scale_max,
                        )
                    )

                except Exception as e:
                    # FAIL FAST: Do not swallow errors in strict coding standards.
                    logger.error(f"[XAIReporter] Failed to process scorecard for {key}: {e}", exc_info=True)
                    raise AgentExecutionError(
                        detail=ErrorCodes.AGENT_EXECUTION_CRITICAL, original_error=e, agent_name="XAIReporterAgent"
                    ) from e

        # 3. Generate Flat Report (Phase 3)
        # We need execution_id and timestamp from context or generate them
        import uuid
        from datetime import datetime

        from backend.models.dtos.report import XAIFlatReportDTO

        exec_id_str: str | None = None
        if execution_context:
            exec_id_str = execution_context.get("execution_id")

        if not exec_id_str:
            # Fallback if not provided (should not happen in real engine)
            exec_id_str = str(uuid.uuid4())
            logger.warning("[XAIReporterAgent] execution_id missing in context, generated new UUID.")

        try:
            execution_id = uuid.UUID(str(exec_id_str))
        except ValueError:
            execution_id = uuid.uuid4()
            logger.warning(f"[XAIReporterAgent] Invalid execution_id format '{exec_id_str}', generated new UUID.")

        # Aggregate Flattened Scores
        flattened_scores: dict[str, float] = {}
        total_score_sum = 0.0
        count = 0

        # We use the Aggregated Score Cards
        for card in score_cards:
            total_score_sum += card.total_score
            count += 1
            for dim in card.dimensions:
                # Use dimension_id as key
                flattened_scores[dim.dimension_id] = float(dim.score)

        final_avg_score = (total_score_sum / count) if count > 0 else 0.0

        # Identify Strengths/Weaknesses from Flattened Scores
        sorted_scores = sorted(flattened_scores.items(), key=lambda item: item[1], reverse=True)
        top_strength = sorted_scores[0][0] if sorted_scores else None
        top_weakness = sorted_scores[-1][0] if sorted_scores else None

        flat_report = XAIFlatReportDTO(
            execution_id=execution_id,
            timestamp=datetime.now(),
            verdict=result.final_verdict,
            score_total=round(final_avg_score, 2),
            confidence_score=result.confidence_score,
            top_strength_id=top_strength,
            top_weakness_id=top_weakness,
            flattened_scores=flattened_scores,
        )

        # 4. Inject into Result (XAIOutput)
        result = result.model_copy(update={"score_cards": score_cards, "flat_report": flat_report})

        return result

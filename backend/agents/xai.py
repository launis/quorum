from __future__ import annotations

import logging
from typing import Any

# 2. Third Party
from backend.agents.base import BaseAgent

# 3. Local Imports
from backend.exceptions import AgentExecutionError, ErrorCodes
from backend.models.domain import XAIOutput, XAIOutputDTO, XAIReporterInput
from backend.utils.math_utils import normalize_score_to_100

logger = logging.getLogger(__name__)


class XAIReporterAgent(BaseAgent[XAIReporterInput, XAIOutput]):
    """XAI-Raportoija-agentti (XAI Reporter Agent).

    Responsible for generating the final, explainable report.
    """

    state_field = "step_xai"
    REQUIRES_KEYS = []  # Dynamic validation in execute() supports step_judge OR step_judge_cognitive

    INPUT_SCHEMA = XAIReporterInput
    DTO_SCHEMA = XAIOutputDTO
    OUTPUT_SCHEMA = XAIOutput

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

        judges = []
        if input_data.step_judge:
            judges.append(input_data.step_judge)
        if input_data.step_judge_cognitive:
            judges.append(input_data.step_judge_cognitive)

        for judge in judges:
            matrix_id = judge.matrix_id
            name = f"Judge ({matrix_id})"
            judge_results.append((name, judge))
            logger.info(f"[XAIReporterAgent] Found Judge Output: {name}")

        if not judge_results:
            logger.warning("[XAIReporterAgent] No 'step_judge*' data found in inputs.")
            return None

        # Format Context
        lines = ["### AUDIT RESULTS (EVALUATION):"]

        for name, data in judge_results:
            lines.append(f"\n#### EVALUATION FROM: {name}")

            # 1. Total Score
            sc = data.score_card
            total_score = sc.total_score if sc else "N/A"
            lines.append(f"- **Total Score**: {total_score}")

            # 2. Dimensions
            dimensions = sc.dimensions if sc else []
            if dimensions:
                lines.append("  **Dimensions:**")
                for dim in dimensions:
                    d_id = dim.dimension_id.capitalize()
                    score = dim.score
                    reason = dim.reasoning
                    max_val = sc.scale_max if sc else "UNKNOWN"
                    lines.append(f"  - **{d_id}**: {score}/{max_val} - {reason}")
            else:
                pass

            # 3. Critical Findings
            crit_findings = data.critical_findings
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
        # FAIL FAST: XAI requires Judge outputs
        if not input_data.step_judge and not input_data.step_judge_cognitive:
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

        judges = []
        if input_data.step_judge:
            judges.append(input_data.step_judge)
        if input_data.step_judge_cognitive:
            judges.append(input_data.step_judge_cognitive)

        for judge_data in judges:
            try:
                # The scorecard is strictly typed in Phase 8 Standard!
                sc = judge_data.score_card
                if sc:
                    score_cards.append(sc)

            except Exception as e:
                # FAIL FAST: Do not swallow errors in strict coding standards.
                logger.error(f"[XAIReporter] Failed to process scorecard for {judge_data.matrix_id}: {e}", exc_info=True)
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
            total_normalized = normalize_score_to_100(card.total_score, card.scale_min, card.scale_max)
            total_score_sum += total_normalized
            count += 1
            for dim in card.dimensions:
                # Use dimension_id as key
                # Strict: normalize each dimension score individually according to its card's scale
                normalized_dim = normalize_score_to_100(dim.score, card.scale_min, card.scale_max)
                flattened_scores[dim.dimension_id] = normalized_dim

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

        # 4. Promote DTO to Domain Model and Inject Python fields
        # Fallback if already an XAIOutput (e.g. from tests avoiding LLM)
        if isinstance(result, self.OUTPUT_SCHEMA):
            # This must be checked first because OUTPUT_SCHEMA inherits from DTO_SCHEMA
            return result.model_copy(update={"score_cards": score_cards, "flat_report": flat_report})

        if isinstance(result, self.DTO_SCHEMA):
            output = self.OUTPUT_SCHEMA(
                **result.model_dump(),
                score_cards=score_cards,
                flat_report=flat_report
            )
            # Re-apply authority to ensure checksums and metadata are updated properly
            return self._apply_python_authority(output)

        raise AgentExecutionError(
            detail=ErrorCodes.INVALID_JSON_PAYLOAD,
            original_error=TypeError(f"Expected DTO but got {type(result)}"),
            agent_name="XAIReporterAgent"
        )

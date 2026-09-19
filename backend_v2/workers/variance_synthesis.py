"""Cognitive-Mechanical Variance Synthesis Task Builder and Result Models."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationError

from backend_v2.database.repository import UnifiedWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.linguistics import LinguisticsResultDTO
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.dtos.atom_result import ExtensionMetricsDTO
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
from backend_v2.models.enums import (
    CognitiveTier,
    TargetBlockType,
    XaiExtensionType,
)
from backend_v2.models.prompts import (
    STATIC_LINGUISTIC_PROTOCOL,
    VARIANCE_SYSTEM_PROMPT,
    build_linguistic_parameters,
)
from backend_v2.models.state import TraceEvent
from backend_v2.utils.scoring import variance_engine

__all__ = [
    "VarianceExplanationResult",
    "build_variance_metrics_and_task",
]

logger = logging.getLogger(__name__)


class VarianceExplanationResult(BaseModel):
    """Result model for cognitive-mechanical variance explanation."""

    model_config = ConfigDict(strict=True, extra="forbid")

    explanation: str = Field(description="Synthesized cognitive-mechanical variance explanation")


async def build_variance_metrics_and_task(
    repo: UnifiedWorkflowRepository,
    execution: ExecutionRecord,
    active_profile_dto: OutputProfile | None,
    accept_language: str,
    workflow_registry_id: str | None,
    sem_runner: Callable[[Awaitable[Any]], Awaitable[Any]],
) -> tuple[ExtensionMetricsDTO | None, Any | None]:
    """Calculate mechanical variance metrics and build variance explanation task using DEEP tier."""
    if not active_profile_dto:
        return None, None

    has_variance_ext = any(
        ext
        in (
            XaiExtensionType.VARIANCE_VALIDATION,
            XaiExtensionType.VARIANCE_VALIDATION.value,
            "variance_validation",
            "authenticity_evaluation",
        )
        for ext in active_profile_dto.visible_workflow_extensions
    ) or any(
        t
        in (
            TargetBlockType.VARIANCE_VALIDATION_BLOCK,
            TargetBlockType.VARIANCE_VALIDATION_BLOCK.value,
            "variance_validation_block",
        )
        for t in active_profile_dto.target_block_order
    )

    if not has_variance_ext:
        return None, None

    if not active_profile_dto.variance_target_block:
        msg = (
            f"OutputProfile '{active_profile_dto.id}' requires 'variance_target_block' "
            "when variance validation is active."
        )
        logger.error("[variance_synthesis] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
        raise AppException(
            message=msg,
            status_code=400,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        )

    target_block_id = active_profile_dto.variance_target_block
    authenticity_score: float | None = None
    performative_phrases_count: int | None = None
    total_word_count: int | None = None
    cv = execution.context_variables

    if cv is not None and "step_linguistics" in cv:
        step_ling = cv["step_linguistics"]
        if step_ling is not None:
            ling_out = LinguisticsResultDTO.model_validate(step_ling, strict=False)
            patterns = ling_out.performative_patterns
            if isinstance(patterns, list):
                performative_phrases_count = len(patterns)
            if ling_out.total_word_count is not None:
                total_word_count = int(ling_out.total_word_count)

    if authenticity_score is None or performative_phrases_count is None:
        for event in reversed(execution.execution_trace):
            if not isinstance(event, TraceEvent):
                continue
            if event.event_type == "decision" and performative_phrases_count is None:
                try:
                    dec_content = TypeAdapter(dict[str, Any]).validate_python(event.content)
                    if "step_linguistics" in dec_content:
                        ling_out = LinguisticsResultDTO.model_validate(dec_content["step_linguistics"], strict=False)
                        patterns = ling_out.performative_patterns
                        if isinstance(patterns, list):
                            performative_phrases_count = len(patterns)
                        if ling_out.total_word_count is not None:
                            total_word_count = int(ling_out.total_word_count)
                except ValidationError, TypeError, ValueError:
                    pass

            if event.event_type == "output" and authenticity_score is None:
                try:
                    out_content = TypeAdapter(dict[str, Any]).validate_python(event.content)
                    if target_block_id in out_content:
                        det_out = LightweightMatrixOutput.model_validate(out_content[target_block_id], strict=False)
                        if det_out.raw_score is not None:
                            authenticity_score = float(det_out.raw_score)
                except ValidationError, TypeError, ValueError:
                    pass

            if authenticity_score is not None and performative_phrases_count is not None:
                break

    if authenticity_score is None or performative_phrases_count is None:
        return None, None

    variance_res = variance_engine.calculate_mechanical_cognitive_variance(
        llm_authenticity_score=authenticity_score,
        performative_phrases_count=performative_phrases_count,
        total_word_count=total_word_count,
    )
    jargon_density = 0.0
    if total_word_count is not None and total_word_count > 0:
        jargon_density = round((performative_phrases_count / max(1, total_word_count)) * 100.0, 2)

    ext_metrics = ExtensionMetricsDTO(
        authenticity_score=float(authenticity_score),
        performative_phrases_count=float(performative_phrases_count),
        variance_score=float(variance_res.variance_score),
        alignment_verdict=str(variance_res.alignment_verdict),
        jargon_density=float(jargon_density),
        total_word_count=int(total_word_count) if total_word_count is not None else None,
    )

    var_provider = execution.metadata.provider_override if execution.metadata else None
    var_reg_id = execution.metadata.model_registry_id if execution.metadata else None
    if not var_reg_id:
        var_reg_id = workflow_registry_id

    client_var = await LLMClient.from_tier(
        CognitiveTier.DEEP,
        repository=repo,
        provider=var_provider,
        registry_id=var_reg_id,
    )
    var_sys_prompt = f"{VARIANCE_SYSTEM_PROMPT}\n\n{STATIC_LINGUISTIC_PROTOCOL}"
    var_lang_params = build_linguistic_parameters(source_language="Unknown", target_locale=accept_language)

    if (
        not active_profile_dto.variance_synthesis_directive
        or not active_profile_dto.variance_synthesis_directive.strip()
    ):
        logger.warning(
            "[variance_synthesis] OutputProfile '%s' is missing variance_synthesis_directive. "
            "Skipping variance synthesis.",
            active_profile_dto.id,
        )
        return ext_metrics, None

    var_directive_str = active_profile_dto.variance_synthesis_directive.strip()
    var_dynamic_parts = [var_lang_params]
    if active_profile_dto.tone_instruction:
        tone = active_profile_dto.tone_instruction.strip()
        if tone:
            var_dynamic_parts.append(f"<tone_instruction>{tone}</tone_instruction>")
    var_dynamic_parts.append(var_directive_str)
    if active_profile_dto.variance_length_constraint:
        var_dynamic_parts.append(f"<section_budget>{active_profile_dto.variance_length_constraint}</section_budget>")
    var_dynamic_ctx = "\n\n".join(var_dynamic_parts)

    var_messages: list[dict[str, Any]] = [
        {"role": "system", "content": var_sys_prompt},
        {
            "role": "user",
            "content": (
                f"<dynamic_context>\n{var_dynamic_ctx}\n</dynamic_context>\n\n"
                "SCORES TO EXPLAIN:\n"
                f"Cognitive Authenticity Score: {authenticity_score} "
                "(Scale: 1.0 = Routine / Superficial / Illusion of Control / Low Originality, "
                "2.0 = Competent / Consistent & Pertinent Guidance, "
                "3.0 = High Cognitive Authenticity / Deep Original Contribution & Strong Voice)\n"
                f"Mechanical Phrases Load: {performative_phrases_count} phrases "
                f"({jargon_density:.2f} per 100 words) "
                "(Scale: 0.0 = Zero Clichés, 5.0+ = Heavy Jargon/Cliché Load)"
            ),
        },
    ]

    var_task = await sem_runner(
        client_var.run_structured_task(
            messages=var_messages,
            response_model=VarianceExplanationResult,
            mock_identity="variance_explainer",
        )
    )
    return ext_metrics, var_task

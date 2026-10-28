"""Cognitive-Mechanical Variance Synthesis Task Builder and Result Models."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from backend_v2.database.repository import UnifiedWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.linguistics import LinguisticsResultDTO
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock
from backend_v2.models.domain.system_config import ChatMessageDTO
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
    """Result model for cognitive-mechanical variance explanation.

    Attributes:
        explanation: Synthesized cognitive-mechanical variance explanation.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    explanation: Annotated[str, Field(description="Synthesized cognitive-mechanical variance explanation")]


def _has_variance_extension(active_profile_dto: OutputProfile) -> bool:
    """Check whether variance validation is enabled in the output profile.

    Args:
        active_profile_dto: Active output profile configuration.

    Returns:
        True if variance validation extension or target block is enabled, else False.
    """
    has_ext = any(
        ext
        in (
            XaiExtensionType.VARIANCE_VALIDATION,
            XaiExtensionType.VARIANCE_VALIDATION.value,
            "variance_validation",
            "authenticity_evaluation",
        )
        for ext in active_profile_dto.visible_workflow_extensions
    )
    has_block = any(
        t
        in (
            TargetBlockType.VARIANCE_VALIDATION_BLOCK,
            TargetBlockType.VARIANCE_VALIDATION_BLOCK.value,
            "variance_validation_block",
        )
        for t in active_profile_dto.target_block_order
    )
    return has_ext or has_block


def _extract_linguistics_from_execution(execution: ExecutionRecord) -> LinguisticsResultDTO | None:
    """Extract and validate step_linguistics from context variables or trace events.

    Args:
        execution: Active execution record containing context variables and trace events.

    Returns:
        Hydrated LinguisticsResultDTO if present, else None.

    Raises:
        AppException: ErrorCodes.VALIDATION_FAILED if step_linguistics in trace events
            is corrupted and fails model validation.
    """
    cv = execution.context_variables
    if cv is not None and "step_linguistics" in cv:
        step_ling = cv["step_linguistics"]
        if step_ling is not None:
            ling_out = LinguisticsResultDTO.model_validate(step_ling, strict=False)
            if isinstance(ling_out.performative_patterns, list):
                return ling_out

    for event in reversed(execution.execution_trace):
        if not isinstance(event, TraceEvent) or event.event_type != "decision":
            continue
        if type(event.content) is dict and "step_linguistics" in event.content:
            try:
                raw_ling = event.content["step_linguistics"]
                ling_out = (
                    raw_ling
                    if isinstance(raw_ling, LinguisticsResultDTO)
                    else LinguisticsResultDTO.model_validate(raw_ling, strict=False)
                )
                if isinstance(ling_out.performative_patterns, list):
                    return ling_out
            except (ValidationError, TypeError, ValueError) as err:
                logger.error(
                    "[variance_synthesis] Failed to validate step_linguistics: %s",
                    err,
                    exc_info=True,
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )
                raise AppException(
                    message=f"Corrupted step_linguistics in execution trace: {err}",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from err
    return None


def _extract_authenticity_score_from_trace(
    execution_trace: list[Any],
    target_block_id: str,
) -> float | None:
    """Extract and validate cognitive authenticity score for target block from trace events.

    Args:
        execution_trace: Sequence of execution trace events.
        target_block_id: Canonical Opaque Stripe ID of the target matrix prompt block.

    Returns:
        Extracted authenticity score as float if found, else None.

    Raises:
        AppException: ErrorCodes.VALIDATION_FAILED if LightweightMatrixOutput in trace
            events is corrupted and fails model validation.
    """
    for event in reversed(execution_trace):
        if not isinstance(event, TraceEvent) or event.event_type != "output":
            continue
        if isinstance(event.content, LightweightMatrixOutput):
            if event.content.raw_score is not None:
                return float(event.content.raw_score)
        elif type(event.content) is dict and target_block_id in event.content:
            try:
                raw_mat = event.content[target_block_id]
                det_out = (
                    raw_mat
                    if isinstance(raw_mat, LightweightMatrixOutput)
                    else LightweightMatrixOutput.model_validate(raw_mat, strict=False)
                )
                if det_out.raw_score is not None:
                    return float(det_out.raw_score)
            except (ValidationError, TypeError, ValueError) as err:
                logger.error(
                    "[variance_synthesis] Failed to validate LightweightMatrixOutput for %s: %s",
                    target_block_id,
                    err,
                    exc_info=True,
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )
                raise AppException(
                    message=f"Corrupted LightweightMatrixOutput for {target_block_id}: {err}",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from err
    return None


async def _resolve_max_cognitive_score(
    repo: UnifiedWorkflowRepository,
    target_block_id: str,
) -> float:
    """Fetch target matrix prompt block and resolve its maximum cognitive scale score.

    Args:
        repo: Unified workflow repository instance.
        target_block_id: Canonical Opaque Stripe ID of the target matrix prompt block.

    Returns:
        Maximum cognitive scale score as float.

    Raises:
        AppException: ErrorCodes.CONFIGURATION_ERROR if target block is missing or
            lacks valid positive scale extrema definitions.
    """
    target_block = await repo.get_prompt_block(target_block_id)
    if not target_block:
        msg = f"Target prompt block '{target_block_id}' not found in repository."
        logger.error(
            "[variance_synthesis] %s: %s",
            ErrorCodes.CONFIGURATION_ERROR.name,
            msg,
            exc_info=True,
            extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        )
        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        )
    if (
        not isinstance(target_block, MatrixPromptBlock)
        or target_block.computed_max is None
        or target_block.computed_max <= 0.0
    ):
        msg = f"Target prompt block '{target_block_id}' lacks valid scale extrema definitions."
        logger.error(
            "[variance_synthesis] %s: %s",
            ErrorCodes.CONFIGURATION_ERROR.name,
            msg,
            exc_info=True,
            extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        )
        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        )
    return float(target_block.computed_max)


def _build_variance_messages(
    active_profile_dto: OutputProfile,
    var_directive_str: str,
    accept_language: str,
    authenticity_score: float,
    performative_phrases_count: int,
    jargon_density: float,
) -> list[ChatMessageDTO]:
    """Compile system and user ChatMessageDTO list for variance synthesis task.

    Args:
        active_profile_dto: Active output profile configuration.
        var_directive_str: Stripped variance synthesis directive string.
        accept_language: Target locale code for linguistic parameters.
        authenticity_score: Extracted cognitive authenticity score.
        performative_phrases_count: Count of detected performative phrases.
        jargon_density: Calculated performative phrases per 100 words.

    Returns:
        List of system and user ChatMessageDTO instances.
    """
    var_sys_prompt = f"{VARIANCE_SYSTEM_PROMPT}\n\n{STATIC_LINGUISTIC_PROTOCOL}"
    var_lang_params = build_linguistic_parameters(source_language="Unknown", target_locale=accept_language)
    var_dynamic_parts = [var_lang_params]
    if active_profile_dto.tone_instruction:
        tone = active_profile_dto.tone_instruction.strip()
        if tone:
            var_dynamic_parts.append(f"<tone_instruction>{tone}</tone_instruction>")
    var_dynamic_parts.append(var_directive_str)
    if active_profile_dto.variance_length_constraint:
        var_dynamic_parts.append(f"<section_budget>{active_profile_dto.variance_length_constraint}</section_budget>")
    var_dynamic_ctx = "\n\n".join(var_dynamic_parts)

    return [
        ChatMessageDTO(role="system", content=var_sys_prompt),
        ChatMessageDTO(
            role="user",
            content=(
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
        ),
    ]


async def build_variance_metrics_and_task(
    repo: UnifiedWorkflowRepository,
    execution: ExecutionRecord,
    active_profile_dto: OutputProfile | None,
    accept_language: str,
    workflow_registry_id: str | None,
    sem_runner: Callable[[Awaitable[Any]], Awaitable[Any]],
) -> tuple[ExtensionMetricsDTO | None, Any | None]:
    """Calculate mechanical variance metrics and build variance explanation task using DEEP tier.

    Args:
        repo: Unified workflow repository instance for model configuration.
        execution: Active execution record containing trace events and context variables.
        active_profile_dto: Active output profile configuration, or None if omitted.
        accept_language: Client language code for localized prompt compilation.
        workflow_registry_id: Optional model registry ID configured at the workflow level.
        sem_runner: Concurrency semaphore runner for async task invocation.

    Returns:
        Tuple of optional calculated extension metrics and optional structured LLM task.

    Raises:
        AppException: ErrorCodes.CONFIGURATION_ERROR if variance validation is active
            but variance_target_block is unset in the output profile, or target block is missing
            or lacks valid scale extrema definitions.
        AppException: ErrorCodes.VALIDATION_FAILED if step_linguistics or lightweight
            matrix outputs in trace events are corrupted and fail model validation.
    """
    if not active_profile_dto or not _has_variance_extension(active_profile_dto):
        return None, None

    if not active_profile_dto.variance_target_block:
        msg = (
            f"OutputProfile '{active_profile_dto.id}' requires 'variance_target_block' "
            "when variance validation is active."
        )
        logger.error(
            "[variance_synthesis] %s: %s",
            ErrorCodes.CONFIGURATION_ERROR.name,
            msg,
            exc_info=True,
            extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        )
        raise AppException(
            message=msg,
            status_code=400,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        )

    target_block_id = active_profile_dto.variance_target_block
    ling_out = _extract_linguistics_from_execution(execution)
    performative_phrases_count: int | None = None
    total_word_count: int | None = None
    if ling_out is not None:
        performative_phrases_count = len(ling_out.performative_patterns)
        if ling_out.total_word_count is not None:
            total_word_count = int(ling_out.total_word_count)
    authenticity_score = _extract_authenticity_score_from_trace(execution.execution_trace, target_block_id)

    if authenticity_score is None or performative_phrases_count is None:
        logger.warning(
            "[variance_synthesis] OutputProfile '%s' requires variance validation, "
            "but metrics could not be extracted: authenticity_score=%s, performative_phrases_count=%s. "
            "Skipping variance synthesis task.",
            active_profile_dto.id,
            authenticity_score,
            performative_phrases_count,
        )
        return None, None

    max_cognitive_score = await _resolve_max_cognitive_score(repo, target_block_id)
    variance_res = variance_engine.calculate_mechanical_cognitive_variance(
        llm_authenticity_score=authenticity_score,
        performative_phrases_count=performative_phrases_count,
        total_word_count=total_word_count,
        max_cognitive_score=max_cognitive_score,
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
        total_word_count=total_word_count,
    )

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

    var_provider = None
    var_reg_id = None
    if execution.metadata:
        var_provider = execution.metadata.provider_override
        var_reg_id = execution.metadata.model_registry_id
    if not var_reg_id:
        var_reg_id = workflow_registry_id
    client_var = await LLMClient.from_tier(
        CognitiveTier.DEEP,
        repository=repo,
        provider=var_provider,
        registry_id=var_reg_id,
    )
    var_messages = _build_variance_messages(
        active_profile_dto=active_profile_dto,
        var_directive_str=active_profile_dto.variance_synthesis_directive.strip(),
        accept_language=accept_language,
        authenticity_score=authenticity_score,
        performative_phrases_count=performative_phrases_count,
        jargon_density=jargon_density,
    )
    var_task = await sem_runner(
        client_var.run_structured_task(
            messages=var_messages,
            response_model=VarianceExplanationResult,
            mock_identity="variance_explainer",
        )
    )
    return ext_metrics, var_task

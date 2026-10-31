"""Archival hooks for retrieving system precedents."""

from __future__ import annotations

import logging

from fastapi import status
from pydantic import TypeAdapter

from backend_v2.core.hook_registry import (
    HookDeltaDTO,
    HookDependencies,
    HookResult,
    HookState,
    hook_registry,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.archival import ArchivalPrecedentDTO
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.judge import JudgeOutput
from backend_v2.models.dtos.hook_delta import ArchivistPrecedentsResultDTO
from backend_v2.models.state import TraceEvent
from backend_v2.services.storage import get_storage_driver
from backend_v2.settings import get_settings
from backend_v2.utils.pydantic_utils import inflate

logger = logging.getLogger(__name__)

__all__ = ["retrieve_precedent_hook"]


async def _load_trace_events(res: ExecutionRecord) -> list[TraceEvent]:
    """Load trace events from the execution record or fallback disk storage.

    Args:
        res: Completed execution record to inspect.

    Returns:
        List of validated trace events for the execution, or empty list if none exist.

    Raises:
        AppException: Raised with ErrorCodes.STATE_INTEGRITY_ERROR if reading or validating
            the disk trace file fails.
    """
    if res.execution_trace:
        return res.execution_trace

    try:
        driver = get_storage_driver()
        trace_path = f"executions/{res.id}/execution_trace.json"

        if await driver.exists(trace_path):
            raw_trace = await driver.read(trace_path)
            ta = TypeAdapter(list[TraceEvent])
            return ta.validate_json(raw_trace)

        logger.warning("[ArchivalHook] Execution %s has no trace events in DB or Disk. Skipping.", res.id)
        return []
    except Exception as e:
        msg = f"Failed to load trace events from disk for {res.id}: {e}"
        logger.error("[ArchivalHook] %s: %s", ErrorCodes.STATE_INTEGRITY_ERROR.name, msg, exc_info=True)
        raise AppException(
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.STATE_INTEGRITY_ERROR.value, "execution_id": res.id},
        ) from e


def _extract_judge_outputs(trace_events: list[TraceEvent]) -> dict[str, JudgeOutput]:
    """Extract and validate JudgeOutput payloads from execution trace events.

    Args:
        trace_events: Sequence of trace events from a completed execution.

    Returns:
        Mapping of formatted judge labels to validated JudgeOutput domain models.

    Raises:
        AppException: Raised with ErrorCodes.VALIDATION_FAILED if a judge output event
            fails JudgeOutput schema validation.
    """
    judge_outputs: dict[str, JudgeOutput] = {}

    for event in trace_events:
        event_type = event.event_type
        step_name = event.step_name
        content = event.content

        if event_type == "output" and isinstance(step_name, str) and "judge" in step_name:
            try:
                judge_candidate = inflate(content, JudgeOutput)
                if judge_candidate:
                    label = (
                        str(step_name)
                        .replace("step_judge_", "")
                        .replace("step_judge", "Standard")
                        .replace("_", " ")
                        .title()
                    )
                    judge_outputs[label] = judge_candidate
            except Exception as e:
                logger.error(
                    "[ArchivalHook] %s: Output validation failed: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    e,
                    exc_info=True,
                )
                raise AppException(
                    message=f"Event output validation failed: {e}",
                    status_code=status.HTTP_400_BAD_REQUEST,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "original_error": str(e)},
                ) from e

    return judge_outputs


def _build_precedent_dto(res: ExecutionRecord, judge_outputs: dict[str, JudgeOutput]) -> ArchivalPrecedentDTO:
    """Construct an ArchivalPrecedentDTO summary from validated judge outputs.

    Args:
        res: Completed execution record.
        judge_outputs: Mapping of judge step labels to validated JudgeOutput models.

    Returns:
        Constructed ArchivalPrecedentDTO instance with aggregated scores and truncated verdicts.
    """
    score_parts: list[str] = []
    verdict_parts: list[str] = []
    settings = get_settings()
    part_max_chars = settings.archival_verdict_part_max_chars
    summary_max_chars = settings.archival_verdict_summary_max_chars

    for label, judge_model in judge_outputs.items():
        score_card = judge_model.score_card
        avg = score_card.total_score
        verdict_str = score_card.verdict

        score_parts.append(f"{label}: {avg:.2f}")
        # Phase 1, Step 1.3: Slice verdict part only when archival_verdict_part_max_chars > 0
        if part_max_chars > 0:
            verdict_parts.append(f"{label}: {verdict_str[:part_max_chars]}...")
        else:
            verdict_parts.append(f"{label}: {verdict_str}")

    score_summary = " | ".join(score_parts)
    verdict_text = " || ".join(verdict_parts)
    if summary_max_chars > 0:
        verdict_text = verdict_text[:summary_max_chars]

    completed_date = ""
    if res.completed_at:
        completed_date = res.completed_at.isoformat()

    return ArchivalPrecedentDTO(
        id=res.id,
        date=completed_date,
        scores=score_summary,
        verdict=verdict_text,
    )


@hook_registry.register(name="retrieve_precedent")
async def retrieve_precedent_hook(state: HookState | None, deps: HookDependencies) -> HookResult:
    """Retrieve recent completed execution precedents with valid Judge scores.

    Injects a structured list of ArchivalPrecedentDTO items into 'archivist_precedents'
    to allow downstream steps to learn from historical evaluation performance.

    Args:
        state: Current executing hook state.
        deps: Strongly typed hook dependencies container.

    Returns:
        Updated hook result containing injected archival precedents in the state delta.

    Raises:
        AppException: Raised with ErrorCodes.CONFIGURATION_ERROR if exec_repo is missing,
            ErrorCodes.STATE_INTEGRITY_ERROR if a completed execution lacks updated_at or disk
            trace loading fails, ErrorCodes.VALIDATION_FAILED if JudgeOutput validation fails,
            or ErrorCodes.KNOWLEDGE_RETRIEVAL_FAILED if precedent retrieval fails unexpectedly.
    """
    logger.debug("[ArchivalHook] Running retrieve_precedent_hook...")

    if not state:
        return HookResult(success=True, state_delta=HookDeltaDTO())

    repository = deps.exec_repo
    if not repository:
        msg = "Repository not injected. Cannot retrieve precedents."
        logger.error("[ArchivalHook] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg, exc_info=True)
        raise AppException(
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        )

    try:
        settings = get_settings()
        raw_recent = await repository.get_recent_completed_executions(limit=settings.max_precedent_scan_depth)
        recent_executions: list[ExecutionRecord] = TypeAdapter(list[ExecutionRecord]).validate_python(raw_recent)

        for res in recent_executions:
            if not res.updated_at:
                msg = f"Data Integrity Violation: Execution {res.id} marked complete but missing updated_at timestamp."
                logger.error("[ArchivalHook] %s: %s", ErrorCodes.STATE_INTEGRITY_ERROR.name, msg, exc_info=True)
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details={"error_code": ErrorCodes.STATE_INTEGRITY_ERROR.value, "execution_id": res.id},
                )

        precedents: list[ArchivalPrecedentDTO] = []
        for res in recent_executions:
            trace_events = await _load_trace_events(res)
            if not trace_events:
                continue

            judge_outputs = _extract_judge_outputs(trace_events)
            if judge_outputs:
                precedents.append(_build_precedent_dto(res, judge_outputs))

        max_return_count = settings.max_precedent_return_count
        if max_return_count > 0:
            precedents = precedents[-max_return_count:]
        logger.debug("[ArchivalHook] Found %d precedents.", len(precedents))

        return HookResult(
            success=True,
            state_delta=HookDeltaDTO(delta=ArchivistPrecedentsResultDTO(archivist_precedents=precedents)),
        )

    except AppException:
        raise
    except Exception as e:
        logger.error("[ArchivalHook] %s: %s", ErrorCodes.KNOWLEDGE_RETRIEVAL_FAILED.name, e, exc_info=True)
        raise AppException(
            message=f"Failed to retrieve precedents: {e}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.KNOWLEDGE_RETRIEVAL_FAILED.value, "original_error": str(e)},
        ) from e

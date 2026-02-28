"""Archival hooks for retrieving system precedents."""

import logging

from fastapi import status

from backend.database.repository import AbstractWorkflowRepository
from backend.exceptions import AppException, ErrorCodes
from backend.models.domain.judge import JudgeOutput
from backend.models.state import WorkflowState
from backend.utils.pydantic_utils import inflate

logger = logging.getLogger(__name__)


async def retrieve_precedent(
    state: WorkflowState, repository: AbstractWorkflowRepository | None = None
) -> WorkflowState:
    """HOOK: retrieve_precedent.

    Retrieve the last N completed executions with a valid Judge score (Case Law).
    Inject a textual summary of these precedents into 'context_variables["archivist_precedents"]'.
    Designed to allow agents to learn from past performance.

    Args:
        state (WorkflowState): Current workflow state.
        repository (AbstractWorkflowRepository, optional): Data access layer. Defaults to None.

    Returns:
        WorkflowState: Updated state with injected precedents.

    Raises:
        AppException: If repository is missing or retrieval fails.
    """
    logger.debug("[ArchivalHook] Running retrieve_precedent hook...")

    # Strict Enforce: State must be WorkflowState object
    if isinstance(state, dict):
        raise AppException(
            message="Archival Hook received dict state. Strict Pydantic Enforcement Violation.",
            status_code=500,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA},
        )

    if not repository:
        # STRICT CONFIG CHECK
        error_code = ErrorCodes.CONFIGURATION_ERROR
        msg = "Repository not injected. Cannot retrieve precedents."
        logger.error(f"[ArchivalHook] {error_code.name}: {msg}")
        raise AppException(message=msg, status_code=500, details={"error_code": error_code})

    try:
        # 1. Use Repository to get recent completed executions
        recent_executions = await repository.get_recent_completed_executions(limit=5)

        # STRICT Enforce: Repository must return List[ExecutionRecord] objects, NOT dicts.
        if recent_executions and isinstance(recent_executions[0], dict):
            error_code = ErrorCodes.INVALID_OUTPUT_SCHEMA
            msg = "Repository returned dicts instead of Pydantic Models. Strict Pydantic Enforcement Violation."
            logger.error(f"[ArchivalHook] {error_code.name}: {msg}")
            raise AppException(message=msg, status_code=500, details={"error_code": error_code})

        # 2. Filter and Format
        precedents = []

        # FAIL FAST: Strict Data Integrity (All completed executions must have a completed_at timestamp)
        for res in recent_executions:
            if not res.completed_at:
                # Fail Fast Protocol (Part 18): Hard crash on data integrity violation
                error_code = ErrorCodes.STATE_INTEGRITY_ERROR
                msg = f"Data Integrity Violation: Execution {res.id} marked complete but missing timestamp."
                logger.error(f"[ArchivalHook] {error_code.name}: {msg}", exc_info=False)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": error_code.value, "execution_id": res.id}
                )

        for res in recent_executions:
            # Check if it has judge output
            # ExecutionRecord -> results (WorkflowState) -> execution_trace (List[TraceEvent])

            # FAIL FAST: Strict Type Enforcement
            wf_state = res.results
            if isinstance(wf_state, dict):
                # Attempt to strict inflate if it's a dict (e.g. from JSON serialization in DB)
                wf_state = inflate(wf_state, WorkflowState)

            if not isinstance(wf_state, WorkflowState):
                # If it's still not a WorkflowState, we have invalid data structure for a completed execution
                logger.warning(f"Execution {res.id} results is not a valid WorkflowState. Skipping.")
                continue

            # Find ALL Judge outputs in trace (Generic Detection)
            judge_outputs = {}

            # TraceEvents are needing access. Check if WorkflowState has trace?
            # WorkflowState definition: trace_events: List[TraceEvent] = ...
            trace_events = wf_state.execution_trace or []

            for event in trace_events:
                if event.event_type == "output" and "judge" in event.step_name:
                    # Attempt strict inflation to see if it's a JudgeOutput
                    # We don't care about the step name, only the data schema.
                    try:
                        judge_candidate = inflate(event.content, JudgeOutput)
                        if judge_candidate:
                            # Use step_name as label (e.g. "step_judge" -> "Standard", "step_judge_cognitive" -> "Cognitive")
                            # Clean up label for UI
                            label = (
                                event.step_name.replace("step_judge_", "")
                                .replace("step_judge", "Standard")
                                .replace("_", " ")
                                .title()
                            )
                            if label == "Standard":
                                label = "Standard"  # Keep simple

                            judge_outputs[label] = judge_candidate
                    except Exception as e:
                        error_code = ErrorCodes.VALIDATION_FAILED
                        logger.error(f"[ArchivalHook] {error_code.name}: Output validation failed: {e}", exc_info=True)
                        raise AppException(
                            message=f"Event output validation failed: {e}",
                            status_code=status.HTTP_400_BAD_REQUEST,
                            details={
                                "error_code": error_code.value,
                                "original_error": str(e)
                            },
                        ) from e

            if judge_outputs:
                score_parts = []
                verdict_parts = []

                for label, judge_model in judge_outputs.items():
                    avg = judge_model.score_card.total_score
                    score_parts.append(f"{label}: {avg:.2f}")
                    verdict_parts.append(f"{label}: {judge_model.score_card.verdict[:50]}...")

                score_summary = " | ".join(score_parts)
                verdict_text = " || ".join(verdict_parts)

                precedents.append(
                    {
                        "id": res.id,
                        "date": res.completed_at.isoformat() if res.completed_at else "",
                        "scores": score_summary,
                        "verdict": verdict_text[:150],  # Truncate
                    }
                )

        # Keep only last 3
        precedents = precedents[-3:]

        logger.debug(f"[ArchivalHook] Found {len(precedents)} precedents.")

        # 4. Inject
        new_context = state.context_variables.copy()
        # Return STRUCTURED data (List[dict]) matching ArchivistInput schema
        new_context["archivist_precedents"] = precedents
        return state.model_copy(update={"context_variables": new_context})

    except AppException:
        raise
    except Exception as e:
        # FAIL FAST - RFC 7807
        error_code = ErrorCodes.KNOWLEDGE_RETRIEVAL_FAILED
        logger.error(f"[ArchivalHook] {error_code.name}: {e}", exc_info=True)
        raise AppException(
            message=f"Failed to retrieve precedents: {e}", status_code=500, details={
                "error_code": error_code.value,
                "original_error": str(e)
            }
        ) from e

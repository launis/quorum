"""Archival hooks for retrieving system precedents."""

import logging

from fastapi import status

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.utils.pydantic_utils import inflate

logger = logging.getLogger(__name__)


@hook_registry.register(name="retrieve_precedent")
async def retrieve_precedent_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """Workflow Data wrapper for retrieve_precedent.

    Retrieve the last N completed executions with a valid Judge score (Case Law).
    Inject a textual summary of these precedents into 'archivist_precedents'.
    Designed to allow agents to learn from past performance.

    Args:
        state (HookState): Current executing state.
        deps (HookDependencies): Strongly typed dependencies.

    Returns:
        HookResult: Updated data with injected precedents.

    Raises:
        AppException: If repository is missing or retrieval fails.
    """
    logger.debug("[ArchivalHook] Running retrieve_precedent_hook...")

    if not state:
        return HookResult(success=True, state_delta={})

    repository = deps.repository
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

        # FAIL FAST: Strict Data Integrity (All completed executions must have a updated_at timestamp)
        for res in recent_executions:
            if not getattr(res, "updated_at", None):
                # Fail Fast Protocol (Part 18): Hard crash on data integrity violation
                error_code = ErrorCodes.STATE_INTEGRITY_ERROR
                msg = f"Data Integrity Violation: Execution {res.id} marked complete but missing updated_at timestamp."
                logger.error(f"[ArchivalHook] {error_code.name}: {msg}", exc_info=False)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": error_code.value, "execution_id": res.id}
                )

        for res in recent_executions:
            # V2 Event Sourcing: TraceEvents live directly on ExecutionRecord.execution_trace
            # (Legacy V1 used res.results which no longer exists)
            trace_events = getattr(res, "execution_trace", []) or []

            if not trace_events:
                logger.warning(f"Execution {res.id} has no trace events. Skipping.")
                continue

            judge_outputs = {}

            for event in trace_events:
                event_type = event.get("event_type") if isinstance(event, dict) else getattr(event, "event_type", "")
                step_name = event.get("step_name") if isinstance(event, dict) else getattr(event, "step_name", "")
                content = event.get("content") if isinstance(event, dict) else getattr(event, "content", None)

                if event_type == "output" and isinstance(step_name, str) and "judge" in step_name:
                    # Attempt strict inflation to see if it's a JudgeOutput
                    # We don't care about the step name, only the data schema.
                    try:
                        judge_candidate = inflate(content, dict)  # type: ignore
                        if judge_candidate:
                            # Use step_name as label
                            # (e.g. "step_judge" -> "Standard", "step_judge_cognitive" -> "Cognitive")
                            # Clean up label for UI
                            label = (
                                str(step_name)
                                .replace("step_judge_", "")
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
                            details={"error_code": error_code.value, "original_error": str(e)},
                        ) from e

            if judge_outputs:
                score_parts = []
                verdict_parts = []

                for label, judge_model in judge_outputs.items():
                    avg = 0.0
                    verdict_str = ""
                    if isinstance(judge_model, dict) and judge_model.get("score_card"):
                        score_card = judge_model.get("score_card", {})
                        avg = score_card.get("total_score", 0.0)
                        verdict_str = score_card.get("verdict", "")
                    elif hasattr(judge_model, "score_card"):
                        score_card = getattr(judge_model, "score_card", None)
                        avg = getattr(score_card, "total_score", 0.0) if score_card else 0.0
                        verdict_str = getattr(score_card, "verdict", "") if score_card else ""

                    score_parts.append(f"{label}: {avg:.2f}")
                    verdict_parts.append(f"{label}: {verdict_str[:50]}...")

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

        # 4. Return STRUCTURED data (List[dict]) matching ArchivistInput schema
        return HookResult(success=True, state_delta={"archivist_precedents": precedents})

    except AppException:
        raise
    except Exception as e:
        # FAIL FAST - RFC 7807
        error_code = ErrorCodes.KNOWLEDGE_RETRIEVAL_FAILED
        logger.error(f"[ArchivalHook] {error_code.name}: {e}", exc_info=True)
        raise AppException(
            message=f"Failed to retrieve precedents: {e}",
            status_code=500,
            details={"error_code": error_code.value, "original_error": str(e)},
        ) from e

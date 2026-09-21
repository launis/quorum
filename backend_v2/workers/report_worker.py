"""Report and PDF compilation background worker.

Handles PDF assembly, SDUI report generation, and report artifact compilation jobs.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from pydantic import ValidationError

import backend_v2.services.report_service as report_service_mod
from backend_v2.database.factory import get_driver
from backend_v2.database.repository import UnifiedWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.dtos.trace import ExecutionUpdateDTO
from backend_v2.models.enums import ExecutionStatus
from backend_v2.settings import get_settings
from backend_v2.workers.synthesis_worker import (
    generate_profile_synthesis_and_pdf_task as generate_profile_synthesis_and_pdf_task,
)
from backend_v2.workers.variance_synthesis import (
    VarianceExplanationResult as VarianceExplanationResult,
)

__all__ = [
    "VarianceExplanationResult",
    "generate_pdf_job",
    "generate_pdf_task",
    "generate_profile_synthesis_and_pdf_task",
    "generate_report_artifact_job",
    "render_profile_job",
]

logger = logging.getLogger(__name__)


def _format_dlq_failure() -> dict[str, str]:
    """Format Dead Letter Queue failure payload.

    Returns:
        Dictionary indicating DLQ failure status.
    """
    return {"_dlq_status": "FAILED/DLQ"}


def _record_dlq_error(err_msg: str) -> None:
    """Log DLQ error details when failure status update fails.

    Args:
        err_msg: Error message describing update failure.
    """
    logger.error(
        "[ReportWorker] %s",
        err_msg,
        exc_info=True,
        extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
    )


async def generate_report_artifact_job(ctx: Any, report_id: str) -> str | dict[str, str]:
    """Invoked by Arq Worker to compile a Materialized Report Artifact in background.

    Args:
        ctx: Arq worker context.
        report_id: Canonical Opaque Stripe ID of the report artifact (rep_...).

    Returns:
        Status message string upon completion, or DLQ dict on failure.
    """
    logger.info("[Worker] Starting generate_report_artifact_job for report: %s", report_id)
    try:
        driver = await get_driver(get_settings())
        repo = UnifiedWorkflowRepository(driver)
        service = report_service_mod.ReportService(repo, synthesis_runner=generate_profile_synthesis_and_pdf_task)
        await service.process_artifact_compilation(report_id)
        return f"Report Artifact Generated: {report_id}"
    except asyncio.CancelledError:
        logger.warning("[Worker] generate_report_artifact_job cancelled for %s", report_id)
        return _format_dlq_failure()
    except (AppException, ValidationError, OSError, RuntimeError, ValueError, KeyError, ImportError) as e:
        logger.error(
            "[Worker] generate_report_artifact_job failed for %s: %s",
            report_id,
            str(e),
            exc_info=True,
            extra={"error_code": ErrorCodes.PDF_GENERATION_FAILED.value},
        )
        return _format_dlq_failure()


async def generate_pdf_job(
    ctx: Any,
    execution_id: str,
    accept_language: str | None = None,
    profile_id: str | None = None,
) -> str | dict[str, str]:
    """Invoked by Arq Worker to ensure background PDF compilation resilience.

    Args:
        ctx: Arq worker context.
        execution_id: Target execution identifier.
        accept_language: Optional locale override.
        profile_id: Target output profile identifier.

    Returns:
        Status message string upon completion, or DLQ dict on failure.
    """
    try:
        await generate_pdf_task(execution_id, accept_language, profile_id)
        return f"PDF Generated for {execution_id}"
    except asyncio.CancelledError:
        logger.warning("[Worker] generate_pdf_job cancelled for %s", execution_id)
        return _format_dlq_failure()
    except (AppException, ValidationError, OSError, RuntimeError, ValueError, KeyError) as e:
        logger.error("[Worker] generate_pdf_job failed for %s: %s", execution_id, e, exc_info=True)
        return _format_dlq_failure()


async def generate_pdf_task(
    execution_id: str,
    accept_language: str | None = None,
    profile_id: str | None = None,
) -> None:
    """Background Task. Assembles and compiles presentation artifacts via ReportService.

    Delegates to ReportService to compile all 4 presentation formats and synchronize
    the execution record in StorageDriver.

    Args:
        execution_id: Target execution identifier.
        accept_language: Optional locale override.
        profile_id: Target output profile identifier.

    Raises:
        AppException: With ErrorCodes.PDF_GENERATION_FAILED if PDF generation fails.
    """
    logger.info("[Task] Starting Async PDF and report assembly for execution %s", execution_id)
    try:
        driver = await get_driver(get_settings())
        repo = UnifiedWorkflowRepository(driver)

        execution_dict = await repo.get_execution(execution_id)
        if not execution_dict:
            logger.warning("[Task] Execution %s no longer exists (deleted?). Skipping PDF generation.", execution_id)
            return

        service = report_service_mod.ReportService(
            repo,
            synthesis_runner=generate_profile_synthesis_and_pdf_task,
        )
        artifact = await service.get_or_create_default_artifact(
            execution_id=execution_id,
            profile_id=profile_id,
            locale=accept_language,
        )
        await service.process_artifact_compilation(artifact.id)
        logger.info("[Task] PDF and report artifact compiled successfully: %s", artifact.id)

    except (AppException, ValidationError, OSError, RuntimeError, ValueError, KeyError, ImportError) as e:
        logger.error(
            "[Task] PDF generation failed for %s. Cause: %s",
            execution_id,
            str(e),
            exc_info=True,
            extra={"error_code": ErrorCodes.PDF_GENERATION_FAILED.value},
        )
        try:
            driver = await get_driver(get_settings())
            repo = UnifiedWorkflowRepository(driver)
            v_step_id = f"sys_render_{profile_id}"
            fail_step_states = None
            fail_steps = None
            exec_record_local = await repo.get_execution(execution_id, hydrate=False)
            if exec_record_local:
                exec_record_local = ExecutionRecord.model_validate(exec_record_local, strict=False)
                if v_step_id in exec_record_local.step_states:
                    old_state = exec_record_local.step_states[v_step_id]
                    new_states = dict(exec_record_local.step_states)
                    new_step = old_state.model_copy(
                        update={
                            "status": ExecutionStatus.FAILED,
                            "last_error": str(e),
                            "progress": None,
                            "has_warning": True,
                        }
                    )
                    new_states[v_step_id] = new_step
                    new_steps = [
                        s.model_copy(
                            update={
                                "status": ExecutionStatus.FAILED,
                                "last_error": str(e),
                                "progress": None,
                                "has_warning": True,
                            }
                        )
                        if s.id == v_step_id
                        else s
                        for s in exec_record_local.steps
                    ]
                    exec_record_local = exec_record_local.model_copy(
                        update={"step_states": new_states, "steps": new_steps}
                    )
                fail_step_states = exec_record_local.step_states
                fail_steps = exec_record_local.steps

            # REQ-02 / Phase 3 Failure Quarantine:
            # Do NOT update ExecutionRecord.status to FAILED. Preserve Phase 1 PASSED status.
            await repo.update_execution(
                execution_id,
                ExecutionUpdateDTO(
                    steps=fail_steps,
                    step_states=fail_step_states,
                ),
            )
        except (OSError, ValidationError, ValueError, KeyError) as update_err:
            update_msg = f"Failed to update execution failure status: {update_err}"
            _record_dlq_error(update_msg)
        raise e


async def render_profile_job(
    ctx: Any,
    execution_id: str,
    accept_language: str | None = None,
    profile_id: str | None = None,
) -> str | dict[str, str]:
    """Invoked by Arq Worker to ensure background synthesis & PDF compilation resilience.

    Args:
        ctx: Arq worker context.
        execution_id: Target execution identifier.
        accept_language: Optional locale override.
        profile_id: Target output profile identifier.

    Returns:
        Status message string upon completion, or DLQ dict on failure.
    """
    try:
        redis_ctx = None
        if ctx is not None and "redis" in ctx:
            redis_ctx = ctx["redis"]
        await generate_profile_synthesis_and_pdf_task(execution_id, accept_language, profile_id, redis_ctx)
        return f"Render Job Completed for {execution_id}"
    except asyncio.CancelledError:
        logger.warning("[Worker] render_profile_job cancelled for %s", execution_id)
        return _format_dlq_failure()
    except (AppException, ValidationError, OSError, RuntimeError, ValueError, KeyError) as e:
        logger.error("[Worker] render_profile_job failed for %s: %s", execution_id, e, exc_info=True)
        return _format_dlq_failure()

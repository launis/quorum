"""Report and PDF compilation background worker.

Compiles materialized report artifacts in the background.
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
from backend_v2.settings import get_settings
from backend_v2.workers.synthesis_worker import (
    generate_profile_synthesis_and_pdf_task as generate_profile_synthesis_and_pdf_task,
)
from backend_v2.workers.variance_synthesis import (
    VarianceExplanationResult as VarianceExplanationResult,
)

__all__ = [
    "VarianceExplanationResult",
    "generate_profile_synthesis_and_pdf_task",
    "generate_report_artifact_job",
]

logger = logging.getLogger(__name__)


def _format_dlq_failure() -> dict[str, str]:
    """Format Dead Letter Queue failure payload.

    Returns:
        Dictionary indicating DLQ failure status.
    """
    return {"_dlq_status": "FAILED/DLQ"}


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

"""Arq 2026 worker daemon runtime entrypoint.

Configures Arq WorkerSettings, registers lifecycle hooks, and manages worker daemon startup/shutdown.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import Any

from arq.connections import RedisSettings
from arq.typing import StartupShutdown, WorkerCoroutine
from arq.worker import Function

from backend_v2.core.registry import TaskRegistry
from backend_v2.database.factory import get_driver
from backend_v2.database.repository import UnifiedWorkflowRepository
from backend_v2.llm.client import LLMClient
from backend_v2.logging_config import (
    configure_logfire,
    log_startup_system_parameters,
    setup_logging,
)
from backend_v2.services.orchestrator.dag_executor import DAGExecutor
from backend_v2.services.orchestrator.prompt_compiler_adapter import PromptCompilerAdapter
from backend_v2.services.orchestrator.rag_preflight_service import RAGPreflightService
from backend_v2.settings import get_settings
from backend_v2.workers import (
    execute_workflow_job,
    generate_pdf_job,
    generate_report_artifact_job,
    render_profile_job,
)

__all__ = [
    "WorkerSettings",
    "health_check",
    "shutdown",
    "startup",
]

logger = logging.getLogger(__name__)


async def startup(ctx: Any) -> None:
    """Called when the Arq worker starts.

    Initializes dependencies and registers tasks.

    Args:
        ctx: Arq worker context to store initialized services.
    """
    setup_logging()
    configure_logfire()
    log_startup_system_parameters(logger, "ARQ WORKER")

    logger.info("TaskRegistry initialized. Registered tasks: %s", list(TaskRegistry._tasks.keys()))

    driver = await get_driver(get_settings())
    repository = UnifiedWorkflowRepository(driver)
    llm_client = LLMClient()

    compiler = PromptCompilerAdapter()
    rag_preflight = RAGPreflightService(
        workflow_repo=repository,
        system_repo=repository,
        prompt_compiler=compiler,
    )
    engine = DAGExecutor(
        exec_repo=repository,
        workflow_repo=repository,
        comp_repo=repository,
        prompt_block_repo=repository,
        output_profile_repo=repository,
        identity_repo=repository,
        audit_repo=repository,
        system_repo=repository,
        prompt_compiler=compiler,
        rag_preflight=rag_preflight,
    )

    ctx["engine"] = engine
    ctx["repository"] = repository
    ctx["llm_client"] = llm_client

    logger.info("Worker services initialized.")


async def shutdown(ctx: Any) -> None:
    """Called when the worker shuts down.

    Args:
        ctx: Arq worker context.
    """
    logger.info("Arq Worker shutting down.")


async def health_check(ctx: Any) -> str:
    """Simple health check task.

    Args:
        ctx: Arq worker context.

    Returns:
        String 'OK' on success.
    """
    return "OK"


class WorkerSettings:
    """Configuration for the Arq worker."""

    settings = get_settings()

    functions: Sequence[WorkerCoroutine | Function] = [
        health_check,
        execute_workflow_job,
        generate_pdf_job,
        render_profile_job,
        generate_report_artifact_job,
    ]
    cron_jobs: Sequence[Any] | None = None
    on_startup: StartupShutdown | None = startup
    on_shutdown: StartupShutdown | None = shutdown

    redis_settings: RedisSettings = RedisSettings(
        host=settings.redis_host,
        port=settings.redis_port,
    )
    job_timeout: int = settings.worker_job_timeout
    max_jobs: int = settings.max_concurrent_workflows

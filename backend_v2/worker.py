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
from fastapi import status

# Phase 1, Step 1.1: Register all mandatory workflow hooks in the Arq worker entrypoint
import backend_v2.hooks as _hooks
from backend_v2.core.hook_registry import hook_registry
from backend_v2.core.telemetry import configure_telemetry
from backend_v2.database.factory import get_driver
from backend_v2.database.repository import UnifiedWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.logging_config import (
    log_startup_system_parameters,
    setup_logging,
)
from backend_v2.services.orchestrator.dag_executor import DAGExecutor
from backend_v2.services.orchestrator.prompt_compiler_adapter import PromptCompilerAdapter
from backend_v2.services.orchestrator.rag_preflight_service import RAGPreflightService
from backend_v2.settings import get_settings
from backend_v2.workers import (
    execute_workflow_job,
    generate_report_artifact_job,
)

_ = _hooks

__all__ = [
    "WorkerSettings",
    "health_check",
    "shutdown",
    "startup",
]

logger = logging.getLogger(__name__)


async def startup(ctx: Any) -> None:
    """Called when the Arq worker starts.

    Initializes dependencies and verifies mandatory hook registration.

    Args:
        ctx: Arq worker context to store initialized services.

    Raises:
        AppException: If mandatory workflow hooks are missing from HookRegistry
            (ErrorCodes.CONFIGURATION_ERROR).
    """
    setup_logging()
    configure_telemetry(get_settings(), service_name_override="quorum-worker")
    log_startup_system_parameters(logger, "ARQ WORKER")

    # Phase 1, Step 1.1: Enforce Fail-Fast HookRegistry verification at worker startup
    registered_hooks = list(hook_registry.get_all_hooks())
    if "input_processing" not in registered_hooks:
        logger.error(
            "[WorkerStartup] %s: Mandatory hook 'input_processing' not registered in HookRegistry.",
            ErrorCodes.CONFIGURATION_ERROR.name,
        )
        raise AppException(
            message="Mandatory hook 'input_processing' not registered in HookRegistry.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={
                "error_code": ErrorCodes.CONFIGURATION_ERROR.value,
                "missing_hook": "input_processing",
            },
        )
    logger.info("HookRegistry initialized. Registered hooks (%d): %s", len(registered_hooks), registered_hooks)

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

    functions: Sequence[WorkerCoroutine | Function] = (
        health_check,
        execute_workflow_job,
        generate_report_artifact_job,
    )
    cron_jobs: Sequence[Any] | None = None
    on_startup: StartupShutdown | None = startup
    on_shutdown: StartupShutdown | None = shutdown

    redis_settings: RedisSettings = RedisSettings(
        host=settings.redis_host,
        port=settings.redis_port,
    )
    job_timeout: int = settings.worker_job_timeout
    max_jobs: int = settings.max_concurrent_workflows

"""Arq Worker configuration and startup logic.

Modernized for GraphEngine and TaskRegistry (V2.9).
"""

import logging
import asyncio
from datetime import UTC, datetime
from typing import Any

from arq.connections import RedisSettings

from backend.core.engine import GraphEngine
from backend.core.registry import TaskRegistry
from backend.llm.client import LLMClient
from backend.logging_config import configure_logfire, setup_logging
from backend.settings import get_settings

# Initialize settings
settings = get_settings()
logger = logging.getLogger(__name__)


# --- Worker Job Tasks ---


async def execute_workflow_job(
    ctx: Any,
    workflow_id: str,
    inputs: dict,
    execution_id: str | None = None,
    organization_id: str | None = None,
) -> dict:
    """Background job to execute a workflow using GraphEngine.

    Args:
        ctx (Any): Arq worker context containing initialized services.
        workflow_id (str): ID of the workflow configuration to run.
        inputs (dict): Raw input arguments for the workflow.
        execution_id (str): ID of the execution record to update.
        organization_id (str): Organization ID context.

    Returns:
        dict: The final workflow state.
    """
    logger.info(f"[Job] Executing workflow: {workflow_id} (Execution ID: {execution_id}, Org: {organization_id})")

    # Inject Organization ID into inputs (Blackboard State) if provided
    # This ensures that valid WorkflowState objects created from this dict will have organization_id populated.
    if organization_id and "organization_id" not in inputs:
        inputs["organization_id"] = organization_id

    # Retrieve pre-initialized Engine
    engine: GraphEngine = ctx["engine"]
    # Retrieve Repository (for loading definition)
    repository = ctx["repository"]

    try:
        # Load Definition
        # We must load the definition to pass it to the engine.
        workflow_def = await repository.get_workflow(workflow_id)

        if not workflow_def:
            # Fallback for file-based testing if DB is empty (Phase 4.1 context)
            # This is helpful for the user's immediate "comprehensive_audit.json" testing
            import json
            import os

            from backend.models.workflow import WorkflowDefinition

            file_path = f"data/workflows/{workflow_id}.json"
            if os.path.exists(file_path):
                logger.info(f"Loading workflow {workflow_id} from file system.")
                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)
                    if "description" not in data:
                        data["description"] = "File loaded"
                    workflow_def = WorkflowDefinition(**data)

        if not workflow_def:
            raise ValueError(f"Workflow '{workflow_id}' not found.")

        # Execute with Persistence Hook
        result = await engine.execute_workflow(
            definition=workflow_def, initial_input=inputs, repository=repository, execution_id=execution_id
        )

        # Final Status Update (Completed)
        if execution_id:
            await repository.update_execution(
                execution_id, {"status": "completed", "results": result, "completed_at": datetime.now(UTC)}
            )

        return result

    except Exception as e:
        logger.error(f"[Job] Workflow {workflow_id} failed: {e}", exc_info=True)
        # Final Status Update (Failed)
        if execution_id:
            try:
                await repository.update_execution(
                    execution_id, {"status": "failed", "error": str(e), "completed_at": datetime.now(UTC)}
                )
            except Exception as update_err:
                logger.error(f"Failed to update execution failure status: {update_err}")
        raise
    except asyncio.CancelledError as e:
        logger.warning(f"[Job] Workflow {workflow_id} CANCELLED (Timeout/Shutdown). Execution ID: {execution_id}")
        if execution_id:
            try:
                await repository.update_execution(
                    execution_id,
                    {
                        "status": "failed",
                        "error": "Task execution was cancelled or timed out.",
                        "completed_at": datetime.now(UTC),
                    },
                )
            except Exception as update_err:
                logger.error(f"Failed to update execution cancellation status: {update_err}")
        raise


# --- Lifecycle ---


async def startup(ctx: Any) -> None:
    """Called when the worker starts.

    Initializes dependencies and registers tasks.
    """
    setup_logging()
    configure_logfire()
    
    # VISUAL SEPARATOR FOR LOG READABILITY
    logger.info("======================================================================")
    logger.info("   ARQ WORKER (V2.9) - STARTING UP")
    logger.info("======================================================================")

    # 1. CRITICAL: Register Tasks
    # Import all task modules here to trigger the @TaskRegistry.register_task decorators.
    # This ensures the Registry is populated before we try to run anything.
    try:
        import backend.tasks.security  # noqa
        import backend.tasks.retrieval  # noqa
        import backend.tasks.analysis  # noqa
        import backend.tasks.critique  # noqa


        # New V2.9 Tasks
        import backend.tasks.interaction  # noqa
        import backend.tasks.judgment  # noqa
        import backend.tasks.coaching  # noqa
        import backend.tasks.reporting  # noqa
        import backend.tasks.panel  # noqa

        logger.info(f"TaskRegistry initialized. Registered tasks: {list(TaskRegistry._tasks.keys())}")
    except Exception as e:
        logger.error(f"Failed to register tasks: {e}", exc_info=True)
        raise

    # 2. Initialize Dependencies
    from backend.dependencies import get_async_repository

    # Repository (Firestore/TinyDB)
    repository = await get_async_repository()

    # LLM Client (Instructor) - Singleton init
    llm_client = LLMClient()
    # Note: LLMClient is usually stateless or singleton, but good to init here.

    # 3. Initialize GraphEngine
    # We pass dependencies if GraphEngine accepts them, otherwise we rely on the context/singletons.
    # Currently GraphEngine() is generic.
    engine = GraphEngine()

    # 4. Store in Context
    ctx["engine"] = engine
    ctx["repository"] = repository
    ctx["llm_client"] = llm_client

    logger.info("Worker services initialized.")


async def shutdown(ctx: Any) -> None:
    """Called when the worker shuts down."""
    logger.info("Arq Worker shutting down.")


async def health_check(ctx: Any) -> str:
    """Simple health check task."""
    return "OK"


class WorkerSettings:
    """Configuration for the Arq worker."""

    functions = [health_check, execute_workflow_job]
    on_startup = startup
    on_shutdown = shutdown

    redis_settings = RedisSettings(
        host=settings.redis_host,
        port=settings.redis_port,
    )
    job_timeout = 900  # 15 minutes

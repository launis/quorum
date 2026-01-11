import logging
from typing import Any

from arq.connections import RedisSettings

from backend.logging_config import configure_logfire, setup_logging
from backend.settings import get_settings

# Initialize settings
settings = get_settings()

# --- Worker Job Tasks ---


async def execute_workflow_task(ctx: Any, execution_id: str, workflow_id: str, inputs: dict) -> None:
    """Background job to execute a workflow.

    Orchestrates the full workflow execution via `PipelineRunner`.

    Args:
        ctx (Any): Arq worker context containing initialized services (repository, registry, etc.).
        execution_id (str): Unique identifier for this execution.
        workflow_id (str): ID of the workflow configuration to run.
        inputs (dict): Raw input arguments for the workflow.

    Side Effects:
        - **Redis**: Updates job status and logs execution progress.
        - **Firestore (via Repository)**:
            - Creates/Updates `executions` collection with initial state.
            - Updates execution status to 'COMPLETED' or 'FAILED' upon finish.
            - Persists final `WorkflowState` including agent outputs.
    """
    logging.info(f"[Job] executing workflow {workflow_id} (Execution ID: {execution_id})")

    # Retrieve pre-initialized Engine from context
    engine = ctx["engine"]

    try:
        # Delegate Execution to the Engine (Shared Logic)
        await engine.execute_workflow_task(execution_id, workflow_id, inputs)
        logging.info(f"[Job] Workflow execution {execution_id} completed via Engine.")

    except Exception as e:
        logging.error(f"[Job] Workflow execution failed: {e}", exc_info=True)


async def startup(ctx: Any) -> None:
    """Called when the worker starts.
    We initialize logging and Logfire here to ensure worker logs are captured.
    """
    setup_logging()
    configure_logfire()
    logging.info("Arq Worker started successfully.")

    # Initialize Services via Dependencies
    # usage of get_engine() automatically resolves all sub-dependencies (Repo, Storage, Registry)
    from backend.dependencies import get_engine

    # We call get_engine() which handles manual resolution invocation
    engine = await get_engine()

    # Store in context for jobs
    ctx["engine"] = engine

    # Also expose sub-services if needed for other tasks, but Engine covers execution
    ctx["repository"] = engine.repository
    ctx["registry"] = engine.registry

    logging.info("Worker services initialized (Unified Engine).")


async def shutdown(ctx: Any) -> None:
    """Called when the worker shuts down."""
    logging.info("Arq Worker shutting down.")


async def health_check(ctx: Any) -> str:
    """Simple health check task."""
    return "OK"


class WorkerSettings:
    """Configuration for the Arq worker."""

    functions = [health_check, execute_workflow_task]  # Registered tasks
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = RedisSettings(
        host=settings.redis_host,
        port=settings.redis_port,
    )
    job_timeout = 900  # 15 minutes (Default is 300s/5m)

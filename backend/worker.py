"""Arq Worker configuration and startup logic.

Modernized for GraphEngine and TaskRegistry (V2.9).
"""

import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

from arq.connections import RedisSettings

from backend.core.engine import GraphEngine
from backend.core.registry import TaskRegistry
from backend.exceptions import ErrorCodes
from backend.llm.client import LLMClient
from backend.logging_config import configure_logfire, setup_logging
from backend.services.pdf_generator import PdfReportService
from backend.services.progress import ProgressService
from backend.services.storage import get_storage_driver
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
    user_id: str | None = None,
) -> dict:
    """Background job to execute a workflow using GraphEngine.

    Args:
        ctx (Any): Arq worker context containing initialized services.
        workflow_id (str): ID of the workflow configuration to run.
        inputs (dict): Raw input arguments for the workflow.
        execution_id (str): ID of the execution record to update.
        organization_id (str): Organization ID context.
        user_id (str): User ID context.

    Returns:
        dict: The final workflow state.
    """
    logger.info(
        f"[Job] Executing workflow: {workflow_id} (Execution ID: {execution_id}, Org: {organization_id}, User: {user_id})"
    )

    # LOGFIRE INTEGRATION: Bind execution_id to this trace context
    # This groups all subsequent logs (Agent, LLM, DB) under this execution_id.
    import logfire

    with logfire.span("execute_workflow_job", tags={"execution_id": execution_id or "unknown"}):
        # Inject Organization ID into inputs (Blackboard State) if provided
        # This ensures that valid WorkflowState objects created from this dict will have organization_id populated.
        if organization_id and "organization_id" not in inputs:
            inputs["organization_id"] = organization_id

        # Inject User ID into inputs (Blackboard State) if provided
        if user_id and "user_id" not in inputs:
            inputs["user_id"] = user_id

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

            start_time = datetime.now(UTC)

            # Execute with Persistence Hook
            result = await engine.execute_workflow(
                definition=workflow_def, initial_input=inputs, repository=repository, execution_id=execution_id
            )

            # Final Status Update (Completed)
            if execution_id:
                # Extract cost estimate
                cost_estimate = 0.0
                models_used: dict[str, int] = {}
                duration_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

                if isinstance(result, dict):
                    trace = result.get("execution_trace", [])
                    if isinstance(trace, list):
                        for event in trace:
                            if isinstance(event, dict) and event.get("event_type") == "output":
                                content = event.get("content", {})
                                if isinstance(content, dict):
                                    meta = content.get("metadata", {})
                                    if isinstance(meta, dict):
                                        # Extract Model usage
                                        m = meta.get("model")
                                        if m:
                                            models_used[m] = models_used.get(m, 0) + 1

                                        # Extract Cost per step
                                        tu = meta.get("token_usage", {})
                                        if isinstance(tu, dict):
                                            cost_estimate += tu.get("cost_usd", 0.0)

                await repository.update_execution(
                    execution_id,
                    {
                        "status": "completed",
                        "results": result,
                        "completed_at": datetime.now(UTC).isoformat(),
                        "cost_estimate": cost_estimate,
                        "duration_ms": duration_ms,
                        "models_used": models_used
                    }
                )

            # --- TEMPORARY DEBUG DUMP (User Request) ---
            try:
                debug_path = (
                    f"C:\\Users\\risto\\Downloads\\debug_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
                with open(debug_path, "w", encoding="utf-8") as f:
                    if hasattr(result, "model_dump_json"):
                        f.write(result.model_dump_json(indent=2))
                    else:
                        import json

                        # Ensure we handle datetime by using a default str converter if needed
                        # But standard json.dump might fail on datetime.
                        # Safe approach: use pydantic's adapter or just str() fallback?
                        # Actually, Engine returns a dict with datetime objects usually.
                        # Let's use a custom encoder or pydantic's TypeAdapter.
                        from pydantic import TypeAdapter

                        # We assume it matches WorkflowState structure generally
                        f.write(TypeAdapter(dict).dump_json(result, indent=2).decode("utf-8"))
                logger.info(f"[Job] Temporary Debug Dump saved to: {debug_path}")
            except Exception as dump_err:
                logger.error(f"[Job] Failed to save debug dump: {dump_err}")
            # -------------------------------------------

            return result

        except Exception as e:
            logger.error(f"[Job] Workflow {workflow_id} failed: {e}", exc_info=True)
            # Final Status Update (Failed)
            if execution_id:
                try:
                    await repository.update_execution(
                        execution_id, {"status": "failed", "error": str(e), "completed_at": datetime.now(UTC).isoformat()}
                    )
                except Exception as update_err:
                    logger.error(f"Failed to update execution failure status: {update_err}")
            raise
        except asyncio.CancelledError:
            logger.warning(f"[Job] Workflow {workflow_id} CANCELLED (Timeout/Shutdown). Execution ID: {execution_id}")
            if execution_id:
                try:
                    await repository.update_execution(
                        execution_id,
                        {
                            "status": "failed",
                            "error": "Task execution was cancelled or timed out.",
                            "completed_at": datetime.now(UTC).isoformat(),
                        },
                    )
                except Exception as update_err:
                    logger.error(f"Failed to update execution cancellation status: {update_err}")
            raise


async def generate_pdf_job(ctx: Any, *, execution_id: str) -> str:
    """Background job to generate a PDF report for an execution.

    Args:
        ctx: Arq worker context.
        execution_id: The execution UUID.

    Returns:
        str: Path to the generated file.
    """
    logger.info(f"[Job] Generating PDF for execution: {execution_id}")

    try:
        # 1. Instantiate Repository
        # We reuse the one in context if available, or factory if needed.
        # Startup initializes ctx["repository"]
        repository = ctx["repository"]

        # 2. Instantiate ProgressService
        # Arq context has 'redis'
        redis = ctx["redis"]
        progress = ProgressService(redis)

        # 3. Instantiate PdfReportService
        service = PdfReportService(repository, progress)

        # 4. Generate PDF
        pdf_bytes = await service.generate_execution_pdf(execution_id)

        # 5. Save Result via StorageService
        storage = get_storage_driver()
        # Relative path: executions/{id}/report.pdf
        output_path_rel = f"executions/{execution_id}/report.pdf"

        # Returns absolute path (if local) or URI (if cloud)
        saved_path = await storage.save(output_path_rel, pdf_bytes)

        logger.info(f"[Job] PDF generated successfully: {saved_path}")
        return saved_path

    except Exception as e:
        error_code = ErrorCodes.PDF_GENERATION_FAILED
        logger.error(f"{error_code}: PDF generation failed for {execution_id}. Cause: {e}", exc_info=True)
        # We ensure the worker doesn't crash by catching generic Exception
        # Arq will mark the job as failed if we re-raise, but mandate says "Ensure job failure does not crash the worker".
        # Logging exception is sufficient. Usually we rely on Arq's retry mechanism if we raise.
        # But if we want to "not crash", we might suppress?
        # "Ensure job failure does not crash the worker" usually means catch-all.
        # However, for Arq to know it failed, we usually should raise.
        # I will re-raise so Arq sees it as failed job, but the worker process itself stays alive (which is default Arq behavior).
        raise


# --- Lifecycle ---


async def startup(ctx: Any) -> None:
    """Called when the worker starts.

    Initializes dependencies and registers tasks.
    """
    setup_logging()
    configure_logfire()

    # VISUAL SEPARATOR FOR LOG READABILITY (File Only)
    logger.info("======================================================================")
    logger.info("   ARQ WORKER (V2.9) - STARTING UP")
    logger.info("======================================================================")

    # 1. PRINT TO CONSOLE (Minimal)
    logger.info("===================================================")
    logger.info("  CQ WORKER (V2.9) STARTED")
    logger.info("  -> Log: backend_debug.log (CHECK FOR DETAILS)")
    logger.info("===================================================")

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

    functions = [health_check, execute_workflow_job, generate_pdf_job]
    on_startup = startup
    on_shutdown = shutdown

    redis_settings = RedisSettings(
        host=settings.redis_host,
        port=settings.redis_port,
    )
    job_timeout = 900  # 15 minutes

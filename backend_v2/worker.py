"""Arq Worker configuration and startup logic.

Modernized for GraphEngine and TaskRegistry (V2.9).
"""

import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

from arq.connections import RedisSettings

from backend_v2.core.engine import GraphEngine
from backend_v2.core.registry import TaskRegistry
from backend_v2.exceptions import ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.logging_config import configure_logfire, setup_logging
from backend_v2.services.pdf_generator import PdfReportService
from backend_v2.services.storage import get_storage_driver
from backend_v2.settings import get_settings

# Initialize settings
settings = get_settings()
logger = logging.getLogger(__name__)

# Pre-register all hooks for background execution
import backend_v2.hooks  # noqa: F401

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
    msg = (
        f"[Job] Executing workflow: {workflow_id} "
        f"(Execution ID: {execution_id}, Org: {organization_id}, User: {user_id})"
    )
    logger.info(msg)

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

                from backend_v2.models.workflow import WorkflowDefinition

                file_path = f"data/workflows/{workflow_id}.json"
                if os.path.exists(file_path):
                    logger.info(f"Loading workflow {workflow_id} from file system.")
                    with open(file_path, encoding="utf-8") as f:
                        data = json.load(f)
                        if "description" not in data:
                            data["description"] = "File loaded"
                        workflow_def = WorkflowDefinition(**data)

            if not workflow_def:
                from backend_v2.exceptions import WorkflowNotFoundError
                raise WorkflowNotFoundError(workflow_id)

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
            from backend_v2.exceptions import AppException
            if not isinstance(e, AppException):
                msg = f"Workflow {workflow_id} failed: {e}"
                logger.error(
                    f"[Worker] {ErrorCodes.INTERNAL_SERVER_ERROR.name}: {msg}",
                    exc_info=True
                )
                e = AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR}
                )

            # Final Status Update (Failed)
            if execution_id:
                try:
                    await repository.update_execution(
                        execution_id,
                        {"status": "failed", "error": str(e), "completed_at": datetime.now(UTC).isoformat()}
                    )
                except Exception as update_err:
                    update_msg = f"Failed to update execution failure status: {update_err}"
                    logger.error(
                        f"[Worker] {ErrorCodes.INTERNAL_SERVER_ERROR.name}: {update_msg}",
                        exc_info=True
                    )
            raise e
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
                    update_msg = f"Failed to update execution cancellation status: {update_err}"
                    logger.error(
                        f"[Worker] {ErrorCodes.INTERNAL_SERVER_ERROR.name}: {update_msg}",
                        exc_info=True
                    )
            raise


async def generate_pdf_job(ctx: Any, *, execution_id: str) -> str:
    """Legacy background job for raw pdf. Replaced by generate_pdf_task but left for compatibility."""
    return ""

async def generate_pdf_task(execution_id: str, accept_language: str | None = None) -> None:
    """
    Background Task. Assembles the SDUI JSON via Transformer and passes to PDF generator.
    Called directly by FastAPI BackgroundTasks without Arq overhead for instant MVP.
    """
    logger.info(f"[Task] Starting Async PDF Koonti for execution {execution_id}")
    try:
        from backend_v2.settings import get_settings
        from backend_v2.database.factory import get_repository
        from backend_v2.services.blueprint import BlueprintTransformer
        
        repo = await get_repository(get_settings())
        transformer = BlueprintTransformer(repo)
        
        # 1. Generate Omni-Channel JSON Payload
        payload = await transformer.build_render_payload(execution_id, accept_language)
        
        # 2. Feed structured JSON to PDF Engine instead of DB fetching
        service = PdfReportService(repo)
        pdf_bytes = await service.generate_execution_pdf(execution_id, blueprint_payload=payload)
        
        # 3. Save bytes
        storage = get_storage_driver()
        output_path_rel = f"executions/{execution_id}/report.pdf"
        saved_path = await storage.save(output_path_rel, pdf_bytes)
        logger.info(f"[Task] PDF generated successfully: {saved_path}")

    except Exception as e:
        logger.error(f"[Task] PDF generation failed for {execution_id}. Cause: {e}", exc_info=True)



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

    # 1. CRITICAL: Register Tasks & Hooks
    # Import all task modules and hooks here to trigger their decorators.
    # This ensures the Registries are populated before we try to run anything.
    logger.info(f"TaskRegistry initialized. Registered tasks: {list(TaskRegistry._tasks.keys())}")

    # 2. Initialize Dependencies
    from backend_v2.database.factory import get_repository

    # Repository (Firestore/TinyDB)
    repository = await get_repository(settings)

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

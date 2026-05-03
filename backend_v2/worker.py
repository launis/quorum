"""Arq Worker configuration and startup logic.

Modernized for GraphEngine and TaskRegistry (V2.9).
"""

import asyncio
import json
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

import logfire
from arq.connections import RedisSettings

from backend_v2.core.hook_registry import HookDependencies, HookState, hook_registry
from backend_v2.core.registry import TaskRegistry
from backend_v2.database.factory import get_driver
from backend_v2.database.repository import UnifiedWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes, WorkflowNotFoundError
from backend_v2.llm.client import LLMClient
from backend_v2.logging_config import configure_logfire, setup_logging
from backend_v2.models.enums import SystemConcurrency
from backend_v2.models.state import StateProjector
from backend_v2.models.v2_core import ExecutionRecord, RenderedSynthesisCache, Workflow
from backend_v2.services.blueprint import BlueprintTransformer
from backend_v2.services.orchestrator.dag_executor import DAGExecutor
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler
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
    inputs: dict[str, Any],
    execution_id: str | None = None,
    organization_id: str | None = None,
    user_id: str | None = None,
) -> dict[str, Any]:
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
    with logfire.span("execute_workflow_job", tags={"execution_id": execution_id or "unknown"}):
        # Inject Organization ID into inputs (Blackboard State) if provided
        # This ensures that valid WorkflowState objects created from this dict will have organization_id populated.  # noqa: E501
        if organization_id and "organization_id" not in inputs:
            inputs["organization_id"] = organization_id

        # Inject User ID into inputs (Blackboard State) if provided
        if user_id and "user_id" not in inputs:
            inputs["user_id"] = user_id

        # Retrieve pre-initialized Engine
        engine = ctx["engine"]
        # Retrieve Repository (for loading definition)
        repository = ctx["repository"]

        try:
            # Load Definition
            # We must load the definition to pass it to the engine.
            workflow_dict = await repository.get_workflow(workflow_id)

            if not workflow_dict:
                raise WorkflowNotFoundError(workflow_id)

            # V2 MUST validate strictly before execution
            workflow_def = Workflow.model_validate(workflow_dict)

            start_time = datetime.now(UTC)

            # V2 Strict Context Execution Engine
            exec_id = execution_id or f"exe_{uuid.uuid4().hex}"
            await engine.execute_workflow(execution_id=exec_id, workflow=workflow_def, raw_inputs=inputs)

            # Final Status Update (Completed)
            if exec_id:
                models_used: dict[str, int] = {}
                duration_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

                await repository.update_execution(
                    exec_id,
                    {
                        "status": "completed",
                        "completed_at": datetime.now(UTC).isoformat(),
                        "duration_ms": duration_ms,
                        "models_used": models_used,
                    },
                )

                # TRIGGER ASYNC RENDER JOB (Epic 14 M4)
                redis = ctx.get("redis")
                if redis:
                    # Enqueue job to generate Synthesis cache and Static PDF
                    default_profile = getattr(workflow_def, "default_profile_id", "default")
                    if not default_profile:
                        default_profile = "default"
                    await redis.enqueue_job("render_profile_job", exec_id, profile_id=default_profile)
                    logger.info(f"[Job] Enqueued render_profile_job for {exec_id} with profile {default_profile}")
                else:
                    logger.warning(f"[Job] Redis context missing. Could not enqueue render_profile_job for {exec_id}")

            return {
                "status": "COMPLETED",
                "execution_id": exec_id,
                "workflow_id": workflow_id,
                "duration_ms": duration_ms if exec_id else 0,
            }

        except Exception as e:
            if not isinstance(e, AppException):
                msg = f"Workflow {workflow_id} failed: {e}"
                logger.error(
                    "[Worker] %s", msg, exc_info=True, extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
                )
                e = AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
                )

            # Final Status Update (Failed)
            local_exec_id = locals().get("exec_id", execution_id)
            if local_exec_id:
                try:
                    await repository.update_execution(
                        local_exec_id,
                        {"status": "failed", "error": str(e), "completed_at": datetime.now(UTC).isoformat()},
                    )
                except Exception as update_err:
                    update_msg = f"Failed to update execution failure status: {update_err}"
                    logger.error(
                        "[Worker] %s",
                        update_msg,
                        exc_info=True,
                        extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
                    )
            raise e
        except asyncio.CancelledError:
            local_exec_id = locals().get("exec_id", execution_id)
            logger.warning(f"[Job] Workflow {workflow_id} CANCELLED (Timeout/Shutdown). Execution ID: {local_exec_id}")  # noqa: E501
            if local_exec_id:
                try:
                    await repository.update_execution(
                        local_exec_id,
                        {
                            "status": "failed",
                            "error": "Task execution was cancelled or timed out.",
                            "completed_at": datetime.now(UTC).isoformat(),
                        },
                    )
                except Exception as update_err:
                    update_msg = f"Failed to update execution cancellation status: {update_err}"
                    logger.error(
                        "[Worker] %s",
                        update_msg,
                        exc_info=True,
                        extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
                    )
            raise


async def generate_pdf_job(
    ctx: Any, execution_id: str, accept_language: str | None = None, profile_id: str = "default"
) -> str:
    """Invoked by Arq Worker to ensure background PDF compilation resilience."""
    await generate_pdf_task(execution_id, accept_language, profile_id)
    return f"PDF Generated for {execution_id}"


async def generate_pdf_task(execution_id: str, accept_language: str | None = None, profile_id: str = "default") -> None:  # noqa: E501
    """Background Task. Assembles the SDUI JSON via Transformer and passes to PDF generator.
    Called by Arq worker for resilient PDF background compilation.
    """
    logger.info(f"[Task] Starting Async PDF Koonti for execution {execution_id}")
    try:
        driver = await get_driver(get_settings())
        repo = UnifiedWorkflowRepository(driver)
        transformer = BlueprintTransformer(exec_repo=repo, workflow_repo=repo, comp_repo=repo, identity_repo=repo)  # noqa: E501

        # 0. Guard: Execution may have been deleted while PDF job was queued
        execution_dict = await repo.get_execution(execution_id)
        if not execution_dict:
            logger.warning(f"[Task] Execution {execution_id} no longer exists (deleted?). Skipping PDF generation.")  # noqa: E501
            return

        # V2 MANDATE: Strict Pydantic parsing at the boundary
        execution_record = (
            ExecutionRecord.model_validate(execution_dict, strict=False) if isinstance(execution_dict, dict) else execution_dict  # noqa: E501
        )

        # 0b. Get explicit locale via Execution
        if execution_record.metadata and "target_locale" in execution_record.metadata:
            loc = execution_record.metadata["target_locale"]
            if loc and not accept_language:
                accept_language = loc

        # 0c. Override default profile dynamically if present in SSOT ExecutionRecord
        if execution_record.output_profile_id:
            profile_id = execution_record.output_profile_id

        # 1. Generate Omni-Channel JSON Payload
        dto = await transformer.build_report_dto(execution_id, profile_id, accept_language)

        # 2. Feed structured DTO to PDF Engine instead of DB fetching
        service = PdfReportService(exec_repo=repo, workflow_repo=repo)
        pdf_bytes = await service.generate_execution_pdf(execution_id, report_dto=dto)

        # 3. Save bytes
        storage = get_storage_driver()
        output_path_rel = f"executions/{execution_id}/report.pdf"
        saved_path = await storage.save(output_path_rel, pdf_bytes)

        # 4. Save path to DB so frontend can fetch it
        await repo.update_execution(execution_id, {"pdf_report_path": saved_path})
        logger.info(f"[Task] PDF generated successfully and path saved: {saved_path}")

    except Exception as e:
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
            await repo.update_execution(
                execution_id,
                {
                    "status": "failed",
                    "error": f"PDF Generation failed: {str(e)}",
                    "completed_at": datetime.now(UTC).isoformat(),
                },
            )
        except Exception:
            logger.error(
                "[Task] Failed to update execution failure status",
                exc_info=True,
                extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
            )
        raise e


async def render_profile_job(
    ctx: Any, execution_id: str, accept_language: str | None = None, profile_id: str = "default"
) -> str:
    """Invoked by Arq Worker to ensure background synthesis & PDF compilation resilience."""
    await generate_profile_synthesis_and_pdf_task(execution_id, accept_language, profile_id, ctx.get("redis"))  # noqa: E501
    return f"Render Job Completed for {execution_id}"


async def generate_profile_synthesis_and_pdf_task(
    execution_id: str,
    accept_language: str | None = None,
    profile_id: str = "default",
    redis: Any | None = None,  # noqa: E501
) -> None:
    """Background Task. Synthesizes Markdown and enqueues PDF generation. Epic 14 M4."""
    logger.info(f"[Task] Starting Async Text Synthesis for execution {execution_id} (Profile: {profile_id})")  # noqa: E501
    try:
        driver = await get_driver(get_settings())
        repo = UnifiedWorkflowRepository(driver)

        execution_data = await repo.get_execution(execution_id)
        if not execution_data:
            logger.warning(f"[Task] Execution {execution_id} no longer exists. Skipping render.")
            return

        # V2 MANDATE: Strict Pydantic parsing at the boundary
        execution = (
            ExecutionRecord.model_validate(execution_data, strict=False) if isinstance(execution_data, dict) else execution_data  # noqa: E501
        )

        has_synthesis = profile_id in (execution.profile_syntheses or {})
        if has_synthesis:
            logger.info(f"[Task] Synthesis already exists for profile {profile_id}. Proceeding to PDF generation.")  # noqa: E501
            if redis:
                await redis.enqueue_job("generate_pdf_job", execution_id, accept_language, profile_id)
            return

        projector = StateProjector()
        for evt in execution.execution_trace:
            # Memory FinOps Protocol: Prevent 200-page RAW inputs from hydrating into RAM
            # Synthesis only needs the analytical DTOs (event_type="output")
            if evt.event_type == "input":
                continue
            projector.apply_delta(evt)
        final_inputs = projector.snapshot

        # 0b. Get explicit locale via Execution
        metadata = execution.metadata or {}
        loc = metadata.get("target_locale")
        if loc and not accept_language:
            accept_language = loc

        # Temporarily inject target_profile_id and language into metadata to guide hook correctly
        metadata["target_profile_id"] = profile_id
        if accept_language:
            metadata["target_locale"] = accept_language

        # V2 Integrity Mandate: Inject step_results explicitly for SynthesisHook
        metadata["step_results"] = final_inputs

        global_context_vars = {"steps": final_inputs}
        state = HookState(
            execution_id=execution_id,
            workflow_id=execution.workflow_id,
            inputs={"steps": final_inputs},
            metadata=metadata,
            global_context_vars=global_context_vars,
        )
        deps = HookDependencies(
            exec_repo=repo, workflow_repo=repo, comp_repo=repo, identity_repo=repo, audit_repo=repo, system_repo=repo
        )  # noqa: E501

        # Execute Text Consolidation Hook
        hook_res = await hook_registry.execute("text_consolidation_hook", state, deps)

        if hook_res.success and hook_res.state_delta:
            cache = RenderedSynthesisCache(
                synthesized_markdown=hook_res.state_delta.get("synthesized_markdown", ""),
                section_syntheses=hook_res.state_delta.get("section_syntheses", {}),
                cited_sources=hook_res.state_delta.get("cited_sources", []),
                xai_highlights=hook_res.state_delta.get("xai_highlights", []),
            )
            # Add new synthesis to record
            current_syntheses = execution.profile_syntheses or {}
            current_syntheses[profile_id] = cache
            dict_syntheses = {k: v.model_dump(mode="json") for k, v in current_syntheses.items()}
            update_payload = {"profile_syntheses": dict_syntheses}
            await repo.update_execution(execution_id, update_payload)
            logger.info(f"[Task] Synthesis cached for {execution_id} (Profile: {profile_id})")

        # Now trigger the statically cached PDF job based on our newly cached synthesis
        if redis:
            await redis.enqueue_job("generate_pdf_job", execution_id, accept_language, profile_id)

    except Exception as e:
        logger.error(
            "[Task] Text Synthesis generation failed for %s. Cause: %s",
            execution_id,
            str(e),
            exc_info=True,
            extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
        )
        try:
            driver = await get_driver(get_settings())
            repo = UnifiedWorkflowRepository(driver)
            await repo.update_execution(
                execution_id,
                {
                    "status": "failed",
                    "error": f"Text Synthesis failed: {str(e)}",
                    "completed_at": datetime.now(UTC).isoformat(),
                },
            )
        except Exception:
            logger.error(
                "[Task] Failed to update execution failure status",
                exc_info=True,
                extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
            )
        raise e


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
    # Repository (Firestore/TinyDB)
    driver = await get_driver(get_settings())
    repository = UnifiedWorkflowRepository(driver)

    # LLM Client (Instructor) - Singleton init
    llm_client = LLMClient()
    # Note: LLMClient is usually stateless or singleton, but good to init here.

    # 3. Initialize DAGExecutor (V2 SSOT Enforcer)
    compiler = PromptCompiler()
    engine = DAGExecutor(
        exec_repo=repository,
        workflow_repo=repository,
        comp_repo=repository,
        identity_repo=repository,
        audit_repo=repository,
        system_repo=repository,
        prompt_compiler=compiler,
    )

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

    functions = [health_check, execute_workflow_job, generate_pdf_job, render_profile_job]
    on_startup = startup
    on_shutdown = shutdown

    redis_settings = RedisSettings(
        host=settings.redis_host,
        port=settings.redis_port,
    )
    job_timeout = settings.worker_job_timeout
    max_jobs = SystemConcurrency.MAX_CONCURRENT_WORKFLOWS.value

"""Arq Worker configuration and startup logic.

Modernized for GraphEngine and TaskRegistry (V2.9).
"""

import asyncio
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
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput

# --- Phase 9 Imports ---
from backend_v2.models.dtos.output_profile import OutputProfileResponseDTO
from backend_v2.models.enums import StrictnessAnchor
from backend_v2.models.state import StateProjector
from backend_v2.models.v2_core import (
    ExecutionRecord,
    ExecutionStepState,
    PromptBlock,
    RenderedSynthesisCache,
    Workflow,
    WorkflowInputs,
)
from backend_v2.services.blueprint import BlueprintTransformer
from backend_v2.services.orchestrator.dag_executor import DAGExecutor
from backend_v2.services.orchestrator.prompt_compiler_adapter import PromptCompilerAdapter
from backend_v2.services.pdf_generator import PdfReportService
from backend_v2.services.storage import get_storage_driver
from backend_v2.settings import get_settings
from backend_v2.utils.math_utils import normalize_score_to_100
from backend_v2.utils.scoring import get_scoring_engine

# Initialize settings
settings = get_settings()
logger = logging.getLogger(__name__)

# Pre-register all hooks for background execution
import json

import backend_v2.hooks  # noqa: F401

# --- Worker Job Tasks ---
from backend_v2.services.orchestrator.strategies.llm_execution.chunk_worker import ChunkWorker
from backend_v2.utils.redis_patcher import ASYNC_ACCUMULATOR_LUA


async def evaluate_chunk_job(
    ctx: Any,
    execution_id: str,
    step_id: str,
    chunk_index: int,
    total_chunks: int,
    file_path: str | None,
    chunk_items: list[Any],
    criteria_blocks_dump: list[dict[str, Any]],
    base_system_prompt: str,
    has_search: bool,
    has_shuffled_atoms: bool,
    atom_to_block_ids: dict[str, list[str]],
    effective_mcp_tools: list[str],
    target_locale: str,
    synthesis_instructions: dict[str, Any] | None,
    strictness_level: int,
    step_metadata: dict[str, Any] | None = None,
) -> None:
    """Asynchronous Arq worker job to evaluate a single text chunk.

    Args:
        ctx: Context provided by the Arq worker containing services.
        execution_id: ID of the execution.
        step_id: ID of the current execution step.
        chunk_index: Index of the chunk being processed.
        total_chunks: Total number of chunks in this step.
        file_path: Optional path to the raw file.
        chunk_items: List of items in this chunk.
        criteria_blocks_dump: Serialized prompt blocks.
        base_system_prompt: System prompt for generation.
        has_search: Boolean indicating if search is enabled.
        has_shuffled_atoms: Boolean indicating shuffled parsing.
        atom_to_block_ids: Mapping from atoms to blocks.
        effective_mcp_tools: List of enabled MCP tools.
        target_locale: Locale for output formatting.
        synthesis_instructions: Instructions for synthesis.
        strictness_level: Level of strictness applied.
        step_metadata: Additional metadata for the step.

    Raises:
        AppException: If chunk execution fails and is routed to DLQ.
    """
    logger.info(f"[Job] evaluate_chunk_job started for {execution_id}:{step_id} chunk {chunk_index}")

    # 1. Fetch raw PDF if file_path is provided to leverage OS Page Cache
    user_payload = ""
    if file_path:
        storage = get_storage_driver()
        # Mock reading file for now, typically returns parsed text
        try:
            content = await storage.read(file_path)
            user_payload = content.decode("utf-8") if isinstance(content, bytes) else str(content)
        except Exception as e:
            logger.error(f"Failed to fetch file_path {file_path}: {e}")
            user_payload = f"Error reading file: {e}"

    # Reconstruct primitives into objects
    compiler = PromptCompilerAdapter()
    criteria_blocks = [PromptBlock.model_validate(cb) for cb in criteria_blocks_dump]

    # Mock a chunk object matching what ChunkWorker expects
    class DummyChunk:
        def __init__(self, items: list[Any]) -> None:
            self.items = items

    chunk_obj = DummyChunk(chunk_items)
    atom_mapping = {k: set(v) for k, v in atom_to_block_ids.items()}

    llm_client = LLMClient()
    sem = asyncio.Semaphore(1)

    # Run chunk processing
    c_final, c_usage, c_traces, c_prompt_context = await ChunkWorker.process_chunk(
        chunk=chunk_obj,
        sem=sem,
        compiler=compiler,
        criteria_blocks=criteria_blocks,
        user_payload=user_payload,
        global_source_text=user_payload,
        base_system_prompt=base_system_prompt,
        has_search=has_search,
        has_shuffled_atoms=has_shuffled_atoms,
        atom_to_block_ids=atom_mapping,
        effective_mcp_tools=effective_mcp_tools,
        bound_client=llm_client,
        step_id=step_id,
        target_locale=target_locale,
        synthesis_instructions=synthesis_instructions,
        output_profile=None,
        strictness_level=strictness_level,
        step_metadata=step_metadata,
    )

    if isinstance(c_final, dict) and c_final.get("_dlq_status") == "FAILED/DLQ":
        reason = c_final.get("reason", "Unknown DLQ Failure")
        logger.error(
            f"[Job] Chunk execution failed and routed to DLQ. Aborting worker task. Reason: {reason}",
            extra={"error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED.name},
        )
        raise AppException(
            message=f"Chunk execution failed and routed to DLQ. Reason: {reason}",
            status_code=500,
            details={"error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED.value},
        )

    # 2. Redis Lua Script to update State without Race Conditions
    redis = ctx.get("redis")
    if not redis:
        logger.warning("Redis not found in context. Chunk state cannot be accumulated.")
        return

    hkey = f"exec:{execution_id}:step:{step_id}"

    payload_dict = {
        "final": c_final,
        "usage": c_usage.model_dump() if c_usage else None,
        "traces": [t.model_dump() for t in c_traces] if c_traces else [],
        "prompt_context": c_prompt_context.model_dump() if c_prompt_context else None,
    }

    payload_str = json.dumps(payload_dict)

    # Execute atomic Lua script
    is_done = await redis.eval(
        ASYNC_ACCUMULATOR_LUA,
        1,  # Number of keys
        hkey,
        str(total_chunks),
        payload_str,
        str(chunk_index),
    )

    if is_done == 1:
        logger.info(f"Chunk {chunk_index} finished. All {total_chunks} chunks completed for {step_id}.")
        # The main orchestrator loop polling Redis will now pick this up and execute MatrixReducer


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

        # V2 Strict Context Execution Engine
        exec_id = execution_id or f"exe_{uuid.uuid4().hex}"

        try:
            # Load Definition
            # We must load the definition to pass it to the engine.
            workflow_dict = await repository.get_workflow(workflow_id)

            if not workflow_dict:
                raise WorkflowNotFoundError(workflow_id)

            # V2 MUST validate strictly before execution
            workflow_def = Workflow.model_validate(workflow_dict)

            start_time = datetime.now(UTC)

            inputs_obj = WorkflowInputs.model_validate(inputs)

            # Retrieve dynamic strictness level from DB (No Hardcoding)
            execution_data = await repository.get_execution(exec_id)
            if not execution_data:
                msg = f"Execution {exec_id} not found in DB before execution! Cannot resolve dynamic strictness."
                logger.error("[Job] %s", msg)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value}
                )

            # Enforce schema validation
            if isinstance(execution_data, dict):
                exec_record = ExecutionRecord.model_validate(execution_data, strict=False)
            else:
                exec_record = execution_data

            # Epic 47 Phase 2: Dynamic Strictness Level resolution
            profile_id = exec_record.output_profile_id
            if not profile_id and hasattr(workflow_def, "default_profile_id"):
                profile_id = workflow_def.default_profile_id

            p_dict = await repository.get_output_profile_by_id(profile_id) if profile_id else None
            active_profile_dto = OutputProfileResponseDTO.model_validate(p_dict) if p_dict else None

            strictness_level: int | None = None
            if active_profile_dto and active_profile_dto.strictness_level is not None:
                strictness_level = active_profile_dto.strictness_level
            elif workflow_def:
                strictness_level = workflow_def.default_strictness_level

            if strictness_level is None:
                msg = (
                    "Strict Fail-Fast Enforced: Missing mandatory "
                    f"strictness_level configuration for workflow '{workflow_def.id}'."
                )
                logger.error("[Worker] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}
                )

            redis = ctx.get("redis")
            updated_exec_record = await engine.execute_workflow(
                execution_id=exec_id,
                workflow=workflow_def,
                raw_inputs=inputs_obj,
                strictness_level=strictness_level,
                arq_pool=redis,
            )

            # Final Status Update (Completed)
            if exec_id:
                # Phase 2, Step 2.1: Parse execution_trace to extract final models_used and step_metrics
                models_used: dict[str, int] = (
                    updated_exec_record.models_used.copy() if updated_exec_record.models_used else {}
                )
                step_metrics: dict[str, Any] = {}
                total_cost_usd = 0.0
                total_prompt_tokens = 0
                total_completion_tokens = 0
                total_cached_tokens = 0
                total_reasoning_tokens = 0
                is_degraded = False

                for event in updated_exec_record.execution_trace:
                    if event.event_type in ("error", "dlq_routed"):
                        is_degraded = True
                    if event.event_type != "output":
                        continue

                    step_meta = event.content.get("_step_metadata", {})
                    usage = step_meta.get("token_usage", {})
                    model_strategy = step_meta.get("model_strategy", "unknown")
                    chunk_size = step_meta.get("chunk_size", 1)

                    p_tokens = usage.get("prompt_tokens", 0)
                    c_tokens = usage.get("completion_tokens", 0)
                    t_tokens = usage.get("total_tokens", 0)
                    c_cost = usage.get("cost_usd", 0.0)

                    total_prompt_tokens += p_tokens
                    total_completion_tokens += c_tokens
                    total_cached_tokens += usage.get("cached_tokens", 0)
                    total_reasoning_tokens += usage.get("reasoning_tokens", 0)
                    total_cost_usd += c_cost

                    models_used[model_strategy] = models_used.get(model_strategy, 0) + t_tokens

                    step_id = event.step_name
                    if step_id not in step_metrics:
                        step_metrics[step_id] = {
                            "model": model_strategy,
                            "cost_usd": 0.0,
                            "total_tokens": 0,
                            "chunk_count": 0,
                        }
                    step_metrics[step_id]["cost_usd"] += c_cost
                    step_metrics[step_id]["total_tokens"] += t_tokens
                    step_metrics[step_id]["chunk_count"] += chunk_size

                # Execution fingerprint snapshot
                execution_summary = {
                    "strictness_level": strictness_level,
                    "target_locale": getattr(workflow_def, "default_locale", "fi"),
                    "is_ensemble_run": getattr(workflow_def, "default_strictness_level", 1) >= 3,
                    "system_concurrency_snapshot": {
                        "LLM_MAX_CHUNK_SIZE": get_settings().llm_max_chunk_size,
                        "SCHEMA_MAX_EVALUATIONS": get_settings().schema_max_evaluations,
                        "SCHEMA_MAX_CHUNK_RECORDS": get_settings().schema_max_chunk_records,
                        "MATRIX_SAMPLING_LIMIT": get_settings().matrix_sampling_limit,
                    },
                    "models_used": models_used,
                    "cost_estimate": total_cost_usd,
                    "is_degraded": is_degraded,
                    "aggregated_usage": {
                        "prompt_tokens": total_prompt_tokens,
                        "completion_tokens": total_completion_tokens,
                        "cached_tokens": total_cached_tokens,
                        "reasoning_tokens": total_reasoning_tokens,
                    },
                }

                updated_meta = dict(updated_exec_record.metadata) if updated_exec_record.metadata else {}
                updated_meta["execution_summary"] = execution_summary
                updated_meta["step_metrics"] = step_metrics
                updated_meta["dag_cost_usd"] = total_cost_usd

                updated_exec_record = updated_exec_record.model_copy(
                    update={"models_used": models_used, "cost_estimate": total_cost_usd, "metadata": updated_meta}
                )

                duration_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

                # TRIGGER ASYNC RENDER JOB (Epic 14 M4)
                redis = ctx.get("redis")
                if redis:
                    # Enqueue job to generate Synthesis cache and Static PDF
                    has_profile = hasattr(updated_exec_record, "output_profile_id")
                    has_val = has_profile and updated_exec_record.output_profile_id
                    profile_id = updated_exec_record.output_profile_id if has_val else None
                    if not profile_id and hasattr(workflow_def, "default_profile_id"):
                        profile_id = workflow_def.default_profile_id

                    v_step_id = f"sys_render_{profile_id}"
                    v_step = ExecutionStepState(id=v_step_id, label="Generating Output Report", status="running")

                    new_states = dict(updated_exec_record.step_states)
                    new_states[v_step_id] = v_step
                    updated_exec_record = updated_exec_record.model_copy(update={"step_states": new_states})
                    step_states_dict = {k: v.model_dump() for k, v in updated_exec_record.step_states.items()}

                    await repository.update_execution(
                        exec_id,
                        {
                            "status": "running",  # keep execution running until PDF is done
                            "step_states": step_states_dict,
                            "duration_ms": duration_ms,
                            "models_used": models_used,
                            "metadata": updated_meta,
                            "cost_estimate": total_cost_usd,
                            "execution_trace": [
                                evt.model_dump(mode="json") for evt in updated_exec_record.execution_trace
                            ],
                        },
                    )

                if redis:
                    # Enqueue the background synthesis and PDF generation
                    await redis.enqueue_job("render_profile_job", exec_id, profile_id=profile_id)
                    logger.info(f"[Job] Enqueued render_profile_job for {exec_id} with profile {profile_id}")
                else:
                    logger.warning(f"[Job] Redis context missing. Could not enqueue render_profile_job for {exec_id}")
                    await repository.update_execution(
                        exec_id,
                        {
                            "status": "completed",
                            "completed_at": datetime.now(UTC).isoformat(),
                            "duration_ms": duration_ms,
                            "models_used": models_used,
                            "metadata": updated_meta,
                            "cost_estimate": total_cost_usd,
                            "execution_trace": [
                                evt.model_dump(mode="json") for evt in updated_exec_record.execution_trace
                            ],
                        },
                    )

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
            if exec_id:
                try:
                    await repository.update_execution(
                        exec_id,
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
            logger.warning(f"[Job] Workflow {workflow_id} CANCELLED (Timeout/Shutdown). Execution ID: {exec_id}")  # noqa: E501
            if exec_id:
                try:
                    await repository.update_execution(
                        exec_id,
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
    ctx: Any, execution_id: str, accept_language: str | None = None, profile_id: str | None = None
) -> str:
    """Invoked by Arq Worker to ensure background PDF compilation resilience.

    Args:
        ctx: Arq worker context.
        execution_id: Target execution identifier.
        accept_language: Optional locale override.
        profile_id: Target output profile identifier.

    Returns:
        Status message string upon completion.
    """
    await generate_pdf_task(execution_id, accept_language, profile_id)
    return f"PDF Generated for {execution_id}"


async def generate_pdf_task(
    execution_id: str, accept_language: str | None = None, profile_id: str | None = None
) -> None:  # noqa: E501
    """Background Task. Assembles the SDUI JSON via Transformer and passes to PDF generator.
    Called by Arq worker for resilient PDF background compilation.

    Args:
        execution_id: Target execution identifier.
        accept_language: Optional locale override.
        profile_id: Target output profile identifier.

    Raises:
        AppException: Inherited from inner logic if generation or update fails.
    """
    logger.info(f"[Task] Starting Async PDF Koonti for execution {execution_id}")
    try:
        driver = await get_driver(get_settings())
        repo = UnifiedWorkflowRepository(driver)
        transformer = BlueprintTransformer(
            exec_repo=repo, workflow_repo=repo, comp_repo=repo, identity_repo=repo, system_repo=repo
        )  # noqa: E501

        # 0. Guard: Execution may have been deleted while PDF job was queued
        execution_dict = await repo.get_execution(execution_id)
        if not execution_dict:
            logger.warning(f"[Task] Execution {execution_id} no longer exists (deleted?). Skipping PDF generation.")  # noqa: E501
            return

        # V2 MANDATE: Strict Pydantic parsing at the boundary
        execution_record = (
            ExecutionRecord.model_validate(execution_dict, strict=False)
            if isinstance(execution_dict, dict)
            else execution_dict  # noqa: E501
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

        # 1.5 Scan for Performative AI Slop (Prong 2)
        # Simply inspect penalties_applied computed in build_report_dto
        has_slop_penalty = any(p.startswith("PENALTY_SLOP:") for p in (dto.penalties_applied or []))
        if has_slop_penalty:
            slop_penalty = next(p for p in dto.penalties_applied if p.startswith("PENALTY_SLOP:"))
            phrases_str = slop_penalty.split(":", 1)[1]
            logger.warning(f"[Task] OutputQualityScanner detected slop for {execution_id}: {phrases_str}")

            # Update DB ExecutionRecord metadata for frontend quick querying
            exec_record_local = await repo.get_execution(execution_id, hydrate=False)
            if exec_record_local:
                new_meta = dict(exec_record_local.metadata)
                new_meta["has_slop_warning"] = True
                await repo.update_execution(execution_id, {"metadata": new_meta})
        else:
            logger.info(f"[Task] OutputQualityScanner approved {execution_id}: no slop penalty applied.")

        # 2. Feed structured DTO to PDF Engine instead of DB fetching
        service = PdfReportService(exec_repo=repo, workflow_repo=repo)
        pdf_bytes = await service.generate_execution_pdf(execution_id, report_dto=dto)

        # 3. Save bytes
        storage = get_storage_driver()
        output_path_rel = f"executions/{execution_id}/report.pdf"
        saved_path = await storage.save(output_path_rel, pdf_bytes)

        # 4. Save path to DB so frontend can fetch it
        v_step_id = f"sys_render_{profile_id}"

        updates: dict[str, Any] = {}
        updates["pdf_report_path"] = saved_path
        updates["status"] = "completed"

        exec_record_local = await repo.get_execution(execution_id, hydrate=False)
        if exec_record_local:
            if v_step_id in exec_record_local.step_states:
                old_state = exec_record_local.step_states[v_step_id]
                new_states = dict(exec_record_local.step_states)
                new_states[v_step_id] = old_state.model_copy(update={"status": "completed"})
                exec_record_local = exec_record_local.model_copy(update={"step_states": new_states})
            updates["step_states"] = {k: v.model_dump() for k, v in exec_record_local.step_states.items()}

        await repo.update_execution(execution_id, updates)
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
            v_step_id = f"sys_render_{profile_id}"
            updates = {}
            updates["status"] = "failed"
            updates["error"] = f"PDF Generation failed: {str(e)}"
            updates["completed_at"] = datetime.now(UTC).isoformat()
            exec_record_local = await repo.get_execution(execution_id, hydrate=False)
            if exec_record_local:
                if v_step_id in exec_record_local.step_states:
                    old_state = exec_record_local.step_states[v_step_id]
                    new_states = dict(exec_record_local.step_states)
                    new_states[v_step_id] = old_state.model_copy(update={"status": "failed", "last_error": str(e)})
                    exec_record_local = exec_record_local.model_copy(update={"step_states": new_states})
                updates["step_states"] = {k: v.model_dump() for k, v in exec_record_local.step_states.items()}

            await repo.update_execution(execution_id, updates)
        except Exception:
            logger.error(
                "[Task] Failed to update execution failure status",
                exc_info=True,
                extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
            )
        raise e


async def render_profile_job(
    ctx: Any, execution_id: str, accept_language: str | None = None, profile_id: str | None = None
) -> str:
    """Invoked by Arq Worker to ensure background synthesis & PDF compilation resilience.

    Args:
        ctx: Arq worker context.
        execution_id: Target execution identifier.
        accept_language: Optional locale override.
        profile_id: Target output profile identifier.

    Returns:
        Status message string upon completion.
    """
    await generate_profile_synthesis_and_pdf_task(execution_id, accept_language, profile_id, ctx.get("redis"))  # noqa: E501
    return f"Render Job Completed for {execution_id}"


async def generate_profile_synthesis_and_pdf_task(
    execution_id: str,
    accept_language: str | None = None,
    profile_id: str | None = None,
    redis: Any | None = None,  # noqa: E501
) -> None:
    """Background Task. Synthesizes Markdown and enqueues PDF generation. Epic 14 M4.

    Args:
        execution_id: Target execution identifier.
        accept_language: Optional locale override.
        profile_id: Target output profile identifier.
        redis: Optional Redis context.

    Raises:
        Exception: If synthesis or execution update fails.
    """
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
            ExecutionRecord.model_validate(execution_data, strict=False)
            if isinstance(execution_data, dict)
            else execution_data  # noqa: E501
        )

        syntheses = execution.profile_syntheses if execution.profile_syntheses is not None else {}
        has_synthesis = profile_id in syntheses
        if has_synthesis:
            logger.info(f"[Task] Synthesis already exists for profile {profile_id}. Proceeding to PDF generation.")  # noqa: E501
            if redis:
                await redis.enqueue_job("generate_pdf_job", execution_id, accept_language, profile_id)
            return

        async def _update_render_status(msg: str) -> None:
            v_step_id = f"sys_render_{profile_id}"
            exec_record_local = await repo.get_execution(execution_id, hydrate=False)
            if exec_record_local:
                old_state = exec_record_local.step_states.get(v_step_id)
                if old_state:
                    updated_state = old_state.model_copy(update={"label": msg, "status": "running"})
                else:
                    updated_state = ExecutionStepState(id=v_step_id, label=msg, status="running")
                new_states = dict(exec_record_local.step_states)
                new_states[v_step_id] = updated_state
                updates = {"step_states": {k: v.model_dump() for k, v in new_states.items()}}
                await repo.update_execution(execution_id, updates)

        await _update_render_status("Lasketaan dynaamisia tuloksia...")

        projector = StateProjector()
        for evt in execution.execution_trace:
            # Memory FinOps Protocol: Prevent 200-page RAW inputs from hydrating into RAM
            # Synthesis only needs the analytical DTOs (event_type="output")
            if evt.event_type == "input":
                continue
            projector.apply_delta(evt)
        final_inputs = projector._build_dto_list()

        # 0b. Get explicit locale via Execution
        metadata = dict(execution.metadata) if execution.metadata is not None else {}
        loc = metadata["target_locale"] if "target_locale" in metadata else None
        if loc and not accept_language:
            accept_language = loc

        # Fetch output profile to resolve dynamic strictness & strategy
        p_dict = await repo.get_output_profile_by_id(profile_id) if profile_id else None
        active_profile_dto = OutputProfileResponseDTO.model_validate(p_dict) if p_dict else None

        w_dict = await repo.get_workflow_by_id(execution.workflow_id)
        workflow_def = Workflow.model_validate(w_dict) if w_dict else None

        strictness_level = StrictnessAnchor.STANDARD.value
        scoring_strategy_val = "AVERAGE"
        if active_profile_dto:
            if active_profile_dto.strictness_level is not None:
                strictness_level = active_profile_dto.strictness_level
            elif workflow_def:
                strictness_level = workflow_def.default_strictness_level

            if active_profile_dto.scoring_strategy is not None:
                prof_strat = active_profile_dto.scoring_strategy
                scoring_strategy_val = prof_strat.value if hasattr(prof_strat, "value") else prof_strat
            elif workflow_def:
                wf_strat = workflow_def.default_scoring_strategy
                scoring_strategy_val = wf_strat.value if hasattr(wf_strat, "value") else wf_strat
        else:
            if workflow_def:
                strictness_level = workflow_def.default_strictness_level
                wf_strat = workflow_def.default_scoring_strategy
                scoring_strategy_val = wf_strat.value if hasattr(wf_strat, "value") else wf_strat

        # Calculate scores dynamically for all matrices
        engine = get_scoring_engine(scoring_strategy_val)

        # Pre-fetch block metadata for math_min/math_max
        all_blocks_raw = await repo.get_all_prompt_blocks()
        blocks_meta = {}
        for rb in all_blocks_raw:
            pb = PromptBlock.model_validate(rb)
            if pb.scales:
                s_vals = [float(s.score) for s in pb.scales]
                if s_vals:
                    blocks_meta[pb.id] = {"math_min": min(s_vals), "math_max": max(s_vals)}

        for i, step_dto in enumerate(final_inputs):
            pb_id = step_dto.block_id
            data = step_dto.payload
            if pb_id in blocks_meta:
                try:
                    mapped_data = LightweightMatrixOutput.map_llm_extensions_to_domain(data)
                    lw_matrix = LightweightMatrixOutput.model_validate(mapped_data, strict=False)
                    if lw_matrix.level_breakdown:
                        stats = {float(k): v for k, v in lw_matrix.level_breakdown.items()}
                        b_meta = blocks_meta.get(pb_id)
                        if b_meta:
                            math_min = b_meta["math_min"]
                            math_max = b_meta["math_max"]
                            dampening_score, xai_log_dto, _ = engine.calculate(
                                stats, math_min, math_max, strictness_level=strictness_level
                            )
                            norm_val = normalize_score_to_100(
                                score=dampening_score,
                                math_min=b_meta["math_min"],
                                math_max=b_meta["math_max"],
                            )
                            lw_matrix = lw_matrix.model_copy(
                                update={
                                    "raw_score": float(dampening_score),
                                    "normalized_score": float(norm_val),
                                    "xai_log": xai_log_dto,
                                }
                            )

                            new_payload = lw_matrix.model_dump(exclude_none=True)

                            # V2 Infrastructure Mandate: Preserve accumulators that bypass strict schemas
                            if "atom_quotes" in data:
                                new_payload["atom_quotes"] = data["atom_quotes"]

                            # V2 Frozen Model update
                            final_inputs[i] = step_dto.model_copy(update={"payload": new_payload})

                            # Persist the dynamic score back to the execution trace so blueprint.py can find it
                            for trace_evt in execution.execution_trace:
                                valid_event = trace_evt.event_type in ["output", "input"]
                                if valid_event and trace_evt.step_name == step_dto.step_id:
                                    if pb_id in trace_evt.content:
                                        trace_evt.content[pb_id] = new_payload
                                        break
                except Exception as e:
                    logger.warning(f"Failed to calculate dynamic score for {pb_id}: {e}")

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
        await _update_render_status("Generoidaan tekoälysynteesiä (tämä saattaa kestää verkosta riippuen)...")
        hook_res = await hook_registry.execute("text_consolidation_hook", state, deps)

        if hook_res.success and hook_res.state_delta:
            delta = dict(hook_res.state_delta)
            # Remove V2 engine metrics that are not part of the Cache schema
            step_metadata_updates = delta.pop("step_metadata_updates", None)
            mcp_tool_audit = delta.pop("mcp_tool_audit", None)

            # Enforce Fail-Fast Hydration (No Naked Dict Extraction)
            cache = RenderedSynthesisCache.model_validate(delta)

            # Add new synthesis to record
            current_syntheses = dict(execution.profile_syntheses) if execution.profile_syntheses is not None else {}
            pid: str = profile_id if profile_id is not None else "default"
            current_syntheses[pid] = cache
            dict_syntheses = {k: v.model_dump(mode="json") for k, v in current_syntheses.items()}
            update_payload: dict[str, Any] = {}
            update_payload["profile_syntheses"] = dict_syntheses

            # Epic 6/14: Safely append LLM token usage and pricing back into ExecutionRecord metadata
            if step_metadata_updates and "token_usage" in step_metadata_updates:
                usage = step_metadata_updates["token_usage"]
                if usage:
                    # Phase 2, Step 2.2: Remove old trace iteration loop and use pre-calculated DAG costs
                    meta = dict(execution.metadata) if execution.metadata else {}

                    dag_cost = meta.get("dag_cost_usd", execution.cost_estimate or 0.0)
                    new_synth_cost = usage.get("cost_usd", 0.0)
                    cumulative_synth_cost = meta.get("synthesis_cost_usd", 0.0) + new_synth_cost
                    total_cost = dag_cost + cumulative_synth_cost

                    total_p_tokens = usage.get("prompt_tokens", 0)
                    total_c_tokens = usage.get("completion_tokens", 0)
                    total_t_tokens = usage.get("total_tokens", 0)

                    exec_summary = meta.get("execution_summary", {})
                    if "aggregated_usage" in exec_summary:
                        agg = exec_summary["aggregated_usage"]
                        total_p_tokens += agg.get("prompt_tokens", 0)
                        total_c_tokens += agg.get("completion_tokens", 0)
                        total_t_tokens += agg.get("prompt_tokens", 0) + agg.get("completion_tokens", 0)
                    else:
                        total_p_tokens += meta.get("prompt_tokens", 0)
                        total_c_tokens += meta.get("completion_tokens", 0)
                        total_t_tokens += meta.get("total_tokens", 0)

                    # Isolate DAG cost vs Synthesis cost
                    meta["synthesis_cost_usd"] = cumulative_synth_cost
                    meta["dag_cost_usd"] = dag_cost

                    meta["total_tokens"] = total_t_tokens
                    meta["prompt_tokens"] = total_p_tokens
                    meta["completion_tokens"] = total_c_tokens
                    meta["cost_estimate"] = total_cost

                    update_payload["metadata"] = meta
                    update_payload["cost_estimate"] = total_cost

                    if execution.models_used:
                        update_payload["models_used"] = dict(execution.models_used)

            # Save the updated trace with dynamically calculated matrix scores
            update_payload["execution_trace"] = [evt.model_dump(mode="json") for evt in execution.execution_trace]

            await repo.update_execution(execution_id, update_payload)

            # Epic 6: Save MCP tool audits directly to the driver's subcollection to avoid overwriting blobs
            if mcp_tool_audit and isinstance(mcp_tool_audit, list):
                coll_path = f"executions/{execution_id}/audit_trails"
                for item in mcp_tool_audit:
                    item_id = item["id"] if "id" in item and item["id"] else str(uuid.uuid4())
                    item["id"] = item_id
                    await driver.upsert(coll_path, item, item_id)

            logger.info(f"[Task] Synthesis cached for {execution_id} (Profile: {profile_id})")
        else:
            logger.warning(f"Synthesis payload not found for execution {execution_id}. DAG execution incomplete?")

        # Now trigger the statically cached PDF job based on our newly cached synthesis
        await _update_render_status("Koostetaan tulosteita valmiiksi...")
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
            v_step_id = f"sys_render_{profile_id}"
            updates: dict[str, Any] = {}
            updates["status"] = "failed"
            updates["error"] = f"Text Synthesis failed: {str(e)}"
            updates["completed_at"] = datetime.now(UTC).isoformat()
            exec_record_local = await repo.get_execution(execution_id, hydrate=False)
            if exec_record_local:
                if v_step_id in exec_record_local.step_states:
                    old_state = exec_record_local.step_states[v_step_id]
                    updated_state = old_state.model_copy(update={"status": "failed", "last_error": str(e)})
                    new_step_states = dict(exec_record_local.step_states)
                    new_step_states[v_step_id] = updated_state
                    exec_record_local = exec_record_local.model_copy(update={"step_states": new_step_states})
                updates["step_states"] = {k: v.model_dump() for k, v in exec_record_local.step_states.items()}

            await repo.update_execution(execution_id, updates)
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

    Args:
        ctx: Arq worker context to store initialized services.
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
    compiler = PromptCompilerAdapter()
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

    functions = [health_check, evaluate_chunk_job, execute_workflow_job, generate_pdf_job, render_profile_job]
    on_startup = startup
    on_shutdown = shutdown

    redis_settings = RedisSettings(
        host=settings.redis_host,
        port=settings.redis_port,
    )
    job_timeout = settings.worker_job_timeout
    max_jobs = get_settings().max_concurrent_workflows

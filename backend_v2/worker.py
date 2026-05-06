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
from backend_v2.models.enums import SystemConcurrency
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
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler
from backend_v2.services.pdf_generator import PdfReportService
from backend_v2.services.storage import get_storage_driver
from backend_v2.settings import get_settings
from backend_v2.utils.math_utils import normalize_score_to_100
from backend_v2.utils.scoring import get_scoring_engine

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

            strictness_level = None
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

            updated_exec_record = await engine.execute_workflow(
                execution_id=exec_id,
                workflow=workflow_def,
                raw_inputs=inputs_obj,
                strictness_level=strictness_level,
            )

            # Final Status Update (Completed)
            if exec_id:
                models_used: dict[str, int] = {}
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
                        },
                    )

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
    """Invoked by Arq Worker to ensure background PDF compilation resilience."""
    await generate_pdf_task(execution_id, accept_language, profile_id)
    return f"PDF Generated for {execution_id}"


async def generate_pdf_task(
    execution_id: str, accept_language: str | None = None, profile_id: str | None = None
) -> None:  # noqa: E501
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
    """Invoked by Arq Worker to ensure background synthesis & PDF compilation resilience."""
    await generate_profile_synthesis_and_pdf_task(execution_id, accept_language, profile_id, ctx.get("redis"))  # noqa: E501
    return f"Render Job Completed for {execution_id}"


async def generate_profile_synthesis_and_pdf_task(
    execution_id: str,
    accept_language: str | None = None,
    profile_id: str | None = None,
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

        projector = StateProjector()
        for evt in execution.execution_trace:
            # Memory FinOps Protocol: Prevent 200-page RAW inputs from hydrating into RAM
            # Synthesis only needs the analytical DTOs (event_type="output")
            if evt.event_type == "input":
                continue
            projector.apply_delta(evt)
        final_inputs = projector.snapshot

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

        strictness_level = 50
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
                    lw_matrix = LightweightMatrixOutput.model_validate(data, strict=False)
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
                    meta = dict(execution.metadata) if execution.metadata else {}
                    t_tokens = meta["total_tokens"] if "total_tokens" in meta else 0
                    t_tokens += usage["total_tokens"] if "total_tokens" in usage else 0
                    meta["total_tokens"] = t_tokens

                    p_tokens = meta["prompt_tokens"] if "prompt_tokens" in meta else 0
                    p_tokens += usage["prompt_tokens"] if "prompt_tokens" in usage else 0
                    meta["prompt_tokens"] = p_tokens

                    c_tokens = meta["completion_tokens"] if "completion_tokens" in meta else 0
                    c_tokens += usage["completion_tokens"] if "completion_tokens" in usage else 0
                    meta["completion_tokens"] = c_tokens

                    c_est = meta["cost_estimate"] if "cost_estimate" in meta else 0.0
                    c_est += usage["cost_estimate"] if "cost_estimate" in usage else 0.0
                    meta["cost_estimate"] = c_est
                    update_payload["metadata"] = meta

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

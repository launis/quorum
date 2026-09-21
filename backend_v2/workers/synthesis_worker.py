"""Async Text Synthesis and Output Profile Cache Worker Task.

Synthesizes Markdown and updates RenderedSynthesisCache for downstream static rendering.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
from typing import Any

from pydantic import ValidationError

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDependencies,
    HookState,
)
from backend_v2.database.factory import get_driver
from backend_v2.database.repository import UnifiedWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.execution import ExecutionRecord, ExecutionStep
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.synthesis import RenderedSynthesisCache
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.synthesis import (
    MatrixExplanationContextDTO,
    MatrixExplanationContextList,
    SynthesisDistillationDTO,
)
from backend_v2.models.dtos.trace import ExecutionUpdateDTO
from backend_v2.models.enums import (
    CognitiveTier,
    ExecutionStatus,
    TargetBlockType,
)
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.prompts import (
    ANTI_JARGON_MANDATE_BLOCK,
    STATIC_LINGUISTIC_PROTOCOL,
    SYNTHESIS_CITATION_RULES_HARVARD,
    SYNTHESIS_SDUI_MANDATES,
    SYNTHESIS_SYSTEM_PROMPT,
    build_linguistic_parameters,
)
from backend_v2.models.state import StateProjector
from backend_v2.services.localization import set_language
from backend_v2.services.orchestrator.synthesis_distiller import synthesis_distiller_hook
from backend_v2.settings import get_settings
from backend_v2.workers.synthesis_reducers import (
    extract_user_role_from_trace,
    handle_starvation_if_detected,
    handle_synthesis_failure_state,
    process_executive_summary_result,
    process_matrix_sections_result,
    process_row_explanations_result,
    process_xai_highlights_result,
    recover_trace_telemetry,
)
from backend_v2.workers.synthesis_tasks import (
    create_executive_summary_task,
    create_matrix_sections_tasks,
    create_row_explanations_task,
    create_xai_highlights_task,
)
from backend_v2.workers.variance_synthesis import (
    VarianceExplanationResult as VarianceExplanationResult,
)
from backend_v2.workers.variance_synthesis import (
    build_variance_metrics_and_task,
)

__all__ = [
    "VarianceExplanationResult",
    "generate_profile_synthesis_and_pdf_task",
]

logger = logging.getLogger(__name__)


async def generate_profile_synthesis_and_pdf_task(
    execution_id: str,
    accept_language: str | None = None,
    profile_id: str | None = None,
    redis: Any | None = None,
) -> None:
    """Background Task. Synthesizes Markdown and enqueues PDF generation.

    Args:
        execution_id: Target execution identifier.
        accept_language: Optional locale override.
        profile_id: Target output profile identifier.
        redis: Optional Redis context.

    Raises:
        AppException: If synthesis or execution update fails with VALIDATION_FAILED,
            CONFIGURATION_ERROR, or INTERNAL_SERVER_ERROR.
    """
    if accept_language is not None and not accept_language.strip():
        msg = "Strict Fail-Fast Enforced: 'accept_language' is mandatory and cannot be empty."
        logger.error("[Task] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(
            message=msg,
            status_code=400,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    logger.info("[Task] Starting Async Text Synthesis for execution %s (Profile: %s)", execution_id, profile_id)
    try:
        driver = await get_driver(get_settings())
        repo = UnifiedWorkflowRepository(driver)

        execution_data = await repo.get_execution(execution_id)
        if not execution_data:
            logger.warning("[Task] Execution %s no longer exists. Skipping render.", execution_id)
            return

        execution = ExecutionRecord.model_validate(execution_data, strict=False)
        resolved_lang = accept_language.strip() if accept_language else execution.target_locale
        if not resolved_lang or not resolved_lang.strip():
            msg = "Strict Fail-Fast Enforced: 'accept_language' is mandatory and cannot be empty."
            logger.error("[Task] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        accept_language = resolved_lang.strip()
        v_step_id = f"sys_render_{profile_id}"

        syntheses: dict[str, Any] = {}
        if execution.profile_syntheses is not None:
            syntheses = execution.profile_syntheses
        has_synthesis = profile_id in syntheses
        if has_synthesis:
            logger.info("[Task] Synthesis already exists for profile %s. Proceeding to PDF generation.", profile_id)
            if redis:
                await redis.enqueue_job("generate_pdf_job", execution_id, accept_language, profile_id)
            return

        async def _update_render_status(msg: str) -> None:
            exec_record_local = await repo.get_execution(execution_id, hydrate=False)
            if exec_record_local:
                exec_record_local = ExecutionRecord.model_validate(exec_record_local, strict=False)
                old_state: ExecutionStep | None = None
                if v_step_id in exec_record_local.step_states:
                    old_state = exec_record_local.step_states[v_step_id]
                if old_state:
                    updated_state = old_state.model_copy(update={"label": msg, "status": ExecutionStatus.RUNNING})
                else:
                    updated_state = ExecutionStep(
                        id=v_step_id,
                        label=msg,
                        status=ExecutionStatus.RUNNING,
                        progress=0,
                        has_warning=False,
                    )
                new_states = dict(exec_record_local.step_states)
                new_states[v_step_id] = updated_state
                new_steps = [
                    s.model_copy(update={"label": msg, "status": ExecutionStatus.RUNNING}) if s.id == v_step_id else s
                    for s in exec_record_local.steps
                ]
                if not any(s.id == v_step_id for s in exec_record_local.steps):
                    new_steps.append(updated_state)
                await repo.update_execution(
                    execution_id,
                    ExecutionUpdateDTO(steps=new_steps, step_states=new_states),
                )

        await _update_render_status("Calculating dynamic results...")

        projector = StateProjector()
        for evt in execution.execution_trace:
            if evt.event_type == "input":
                continue
            projector.apply_delta(evt)
        final_inputs = projector._build_dto_list()

        if not accept_language and execution.target_locale:
            accept_language = execution.target_locale

        if accept_language:
            set_language(accept_language)

        if await handle_starvation_if_detected(
            execution=execution,
            profile_id=profile_id,
            accept_language=accept_language,
            repo=repo,
            redis=redis,
            update_render_status_fn=_update_render_status,
        ):
            return

        resolved_pid = profile_id
        if not resolved_pid or resolved_pid == "default":
            resolved_pid = execution.output_profile_id

        if resolved_pid:
            p_dict = await repo.get_output_profile_by_id(resolved_pid)
            if not p_dict:
                msg = f"Strict Fail-Fast Enforced: OutputProfile '{resolved_pid}' not found in repository."
                logger.error("[Worker] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
                raise ResourceNotFoundError(resource_type="output_profile", resource_id=resolved_pid)
            active_profile_dto: OutputProfile | None = OutputProfile.model_validate(p_dict, strict=False)
            profile_id = resolved_pid
        else:
            active_profile_dto = None

        w_dict = await repo.get_workflow_by_id(execution.workflow_id)
        if not w_dict:
            msg = f"Strict Fail-Fast Enforced: Missing mandatory workflow '{execution.workflow_id}'."
            logger.error("[Worker] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        workflow_def = Workflow.model_validate(w_dict)
        hook_metadata = execution.metadata or ExecutionMetadata()
        hook_state = HookState(
            execution_id=execution_id,
            workflow_id=execution.workflow_id,
            metadata=hook_metadata,
            global_context_vars=GlobalContextVarsDTO(language=accept_language, profile_id=profile_id),
            inputs=ExecutionInputsDTO(target_locale=accept_language, dynamic_inputs={"steps": final_inputs}),
        )
        hook_deps = HookDependencies(
            exec_repo=repo,
            workflow_repo=repo,
            comp_repo=repo,
            prompt_block_repo=repo,
            output_profile_repo=repo,
            identity_repo=repo,
            audit_repo=repo,
            system_repo=repo,
        )
        hook_result = await synthesis_distiller_hook(hook_state, hook_deps)
        if hook_result.state_delta is None or not hook_result.state_delta.delta:
            raise AppException(
                message="Fail-Fast: hook_result.state_delta cannot be None.",
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        try:
            distilled_dto = SynthesisDistillationDTO.model_validate(hook_result.state_delta.delta)
        except ValidationError as e:
            raise AppException(
                message=f"Fail-Fast: distilled_inputs missing from state_delta: {e}",
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from e

        distilled_inputs = distilled_dto.distilled_inputs
        matrices_to_explain: list[MatrixExplanationContextDTO] = list(distilled_dto.matrices_to_explain)

        is_synthesis_expected = True
        if active_profile_dto is not None:
            if active_profile_dto.requires_executive_synthesis:
                is_synthesis_expected = True
            elif active_profile_dto.requires_group_synthesis:
                is_synthesis_expected = True
            elif active_profile_dto.visible_block_extensions or active_profile_dto.visible_workflow_extensions:
                is_synthesis_expected = True
            else:
                is_synthesis_expected = False

        base_dynamic_parts: list[str] = [
            SYNTHESIS_CITATION_RULES_HARVARD,
            build_linguistic_parameters(source_language="Unknown", target_locale=accept_language),
        ]
        if active_profile_dto and active_profile_dto.synthesis_length_constraint:
            base_dynamic_parts.append(
                f"<global_length_constraint_chars>{active_profile_dto.synthesis_length_constraint}</global_length_constraint_chars>"
            )
        if active_profile_dto and active_profile_dto.tone_instruction and active_profile_dto.tone_instruction.strip():
            base_dynamic_parts.append(
                f"<tone_instruction>{active_profile_dto.tone_instruction.strip()}</tone_instruction>"
            )

        synthesis_provider = None
        synthesis_reg_id = None
        if execution.metadata:
            synthesis_provider = execution.metadata.provider_override
            synthesis_reg_id = execution.metadata.model_registry_id
        if not synthesis_reg_id:
            synthesis_reg_id = workflow_def.model_registry_id

        client = await LLMClient.from_tier(
            CognitiveTier.BALANCED,
            repository=repo,
            provider=synthesis_provider,
            registry_id=synthesis_reg_id,
        )

        matrices_json = ""
        if matrices_to_explain:
            matrices_json = MatrixExplanationContextList.dump_json(
                matrices_to_explain, indent=2, exclude_none=True
            ).decode("utf-8")
        matrix_context = ""
        if matrices_json:
            matrix_context = f"\n\nMATRICES TO EXPLAIN:\n{matrices_json}"
        sys_prompt = (
            f"{SYNTHESIS_SYSTEM_PROMPT}\n\n"
            f"{SYNTHESIS_SDUI_MANDATES}\n\n"
            f"{ANTI_JARGON_MANDATE_BLOCK}\n\n"
            f"{STATIC_LINGUISTIC_PROTOCOL}"
        )

        synthesis_sem = asyncio.Semaphore(get_settings().max_concurrent_llm_steps)

        async def _run_with_sem(coro: Any) -> Any:
            async with synthesis_sem if synthesis_sem is not None else contextlib.nullcontext():
                return await coro

        t_exec_summary = None
        t_matrix_sections: list[tuple[str, Any]] = []
        t_xai = None
        t_row = None
        ext_metrics = None

        async with asyncio.TaskGroup() as tg:
            if is_synthesis_expected:
                t_exec_summary = tg.create_task(
                    create_executive_summary_task(
                        client=client,
                        sys_prompt=sys_prompt,
                        base_dynamic_parts=base_dynamic_parts,
                        distilled_inputs=distilled_inputs,
                        matrix_context=matrix_context,
                        active_profile_dto=active_profile_dto,
                        sem_runner=_run_with_sem,
                    )
                )
                t_matrix_task = tg.create_task(
                    create_matrix_sections_tasks(
                        client=client,
                        sys_prompt=sys_prompt,
                        base_dynamic_parts=base_dynamic_parts,
                        distilled_inputs=distilled_inputs,
                        matrix_context=matrix_context,
                        active_profile_dto=active_profile_dto,
                        distilled_data=distilled_dto,
                        sem_runner=_run_with_sem,
                    )
                )
                t_xai = tg.create_task(
                    create_xai_highlights_task(
                        client=client,
                        sys_prompt=sys_prompt,
                        base_dynamic_parts=base_dynamic_parts,
                        distilled_inputs=distilled_inputs,
                        matrix_context=matrix_context,
                        active_profile_dto=active_profile_dto,
                        sem_runner=_run_with_sem,
                    )
                )

            t_row = tg.create_task(
                create_row_explanations_task(
                    repo=repo,
                    matrices_to_explain=matrices_to_explain,
                    active_profile_dto=active_profile_dto,
                    accept_language=accept_language,
                    execution=execution,
                    workflow_registry_id=workflow_def.model_registry_id,
                    sem_runner=_run_with_sem,
                )
            )

            async def _var_runner() -> tuple[Any, Any]:
                return await build_variance_metrics_and_task(
                    repo=repo,
                    execution=execution,
                    active_profile_dto=active_profile_dto,
                    accept_language=accept_language,
                    workflow_registry_id=workflow_def.model_registry_id,
                    sem_runner=_run_with_sem,
                )

            t_var_wrapper = tg.create_task(_var_runner())

        t_matrix_sections = []
        if is_synthesis_expected:
            t_matrix_sections = t_matrix_task.result()
        ext_metrics, t_variance_result = t_var_wrapper.result()

        synth_cost = 0.0
        synth_tokens = 0
        sec_dict = {}

        exec_summary_res = None
        if t_exec_summary is not None:
            exec_summary_res = t_exec_summary.result()
        exec_dto, exec_blocks, c1, tok1 = process_executive_summary_result(
            exec_summary_res,
            active_profile_dto,
        )
        if exec_blocks:
            sec_dict[TargetBlockType.EXECUTIVE_SUMMARY_BLOCK.value] = exec_blocks
        synth_cost += c1
        synth_tokens += tok1

        mat_dict, c2, tok2 = process_matrix_sections_result(t_matrix_sections)
        sec_dict.update(mat_dict)
        synth_cost += c2
        synth_tokens += tok2

        xai_res = None
        if t_xai is not None:
            xai_res = t_xai.result()
        xai_highlights_list, c3, tok3 = process_xai_highlights_result(
            xai_res,
            active_profile_dto,
        )
        synth_cost += c3
        synth_tokens += tok3

        row_res = None
        if t_row is not None:
            row_res = t_row.result()
        cache_row_explanations, c4, tok4 = process_row_explanations_result(
            row_res,
            matrices_to_explain,
            active_profile_dto,
        )
        synth_cost += c4
        synth_tokens += tok4

        variance_expl = None
        if t_variance_result:
            var_dto, usage = t_variance_result
            if var_dto is not None:
                variance_expl = var_dto.explanation
            if usage:
                synth_cost += usage.cost_usd
                synth_tokens += usage.total_tokens

        user_role_val: str | None = None
        user_role_just: str | None = None
        if exec_dto is not None:
            user_role_val = exec_dto.user_role
            user_role_just = exec_dto.user_role_justification
        if active_profile_dto and active_profile_dto.user_role_target_block:
            user_role_val, user_role_just = extract_user_role_from_trace(
                execution=execution,
                role_target_block_id=active_profile_dto.user_role_target_block,
                default_role=user_role_val,
                default_justification=user_role_just,
            )

        cited_sources: list[str] = []
        if exec_dto is not None and exec_dto.cited_sources:
            cited_sources = list(exec_dto.cited_sources)

        cache = RenderedSynthesisCache(
            section_syntheses=sec_dict,
            row_explanations=cache_row_explanations,
            variance_explanation=variance_expl,
            cited_sources=cited_sources,
            xai_highlights=xai_highlights_list,
            user_role=user_role_val,
            user_role_justification=user_role_just,
            extension_metrics=ext_metrics,
        )

        current_syntheses: dict[str, Any] = {}
        if execution.profile_syntheses is not None:
            current_syntheses = dict(execution.profile_syntheses)
        pid = "default"
        if profile_id is not None:
            pid = profile_id
        current_syntheses[pid] = cache

        prev_tokens = execution.cumulative_synthesis_tokens
        prev_cost = execution.cumulative_synthesis_cost
        new_cum_tokens = prev_tokens + synth_tokens
        new_cum_cost = prev_cost + synth_cost
        dag_cost = float(execution.dag_cost_usd)
        if dag_cost == 0.0 and execution.cost_estimate > 0.0 and execution.cost_estimate > prev_cost:
            dag_cost = float(execution.cost_estimate - prev_cost)

        dag_cost, rec_p, rec_c, rec_cac, rec_r = await recover_trace_telemetry(execution, dag_cost)
        total_cost = dag_cost + new_cum_cost
        dto = ExecutionUpdateDTO(
            profile_syntheses=current_syntheses,
            cumulative_synthesis_tokens=new_cum_tokens,
            cumulative_synthesis_cost=new_cum_cost,
            cost_estimate=total_cost,
        )
        if dag_cost > execution.dag_cost_usd:
            dto = dto.model_copy(update={"dag_cost_usd": dag_cost})
        if rec_p is not None and execution.prompt_tokens == 0:
            dto = dto.model_copy(update={"prompt_tokens": rec_p})
        if rec_c is not None and execution.completion_tokens == 0:
            dto = dto.model_copy(update={"completion_tokens": rec_c})
        if rec_cac is not None and execution.cached_tokens == 0:
            dto = dto.model_copy(update={"cached_tokens": rec_cac})
        if rec_r is not None and execution.reasoning_tokens == 0:
            dto = dto.model_copy(update={"reasoning_tokens": rec_r})

        await repo.update_execution(execution_id, dto)
        logger.info("[Task] Synthesis cached for %s (Profile: %s)", execution_id, profile_id)

        await _update_render_status("Compiling output documents...")
        if redis:
            await redis.enqueue_job("generate_pdf_job", execution_id, accept_language, profile_id)

    except Exception as e:
        is_validation_err = isinstance(e, ValidationError)
        if not is_validation_err and isinstance(e, ExceptionGroup):
            val_errors, _ = e.split(ValidationError)
            if val_errors:
                is_validation_err = True

        if is_validation_err:
            msg = f"Strictness Fail-Fast: Invalid data payload during synthesis/pdf task: {str(e)}"
            logger.error(
                "[Task] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                exc_info=True,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            e = AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        else:
            logger.error(
                "[Task] Text Synthesis generation failed for %s: %s",
                execution_id,
                str(e),
                exc_info=True,
                extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
            )

        await handle_synthesis_failure_state(execution_id, profile_id, e)
        raise e

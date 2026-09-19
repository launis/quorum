"""Processors, reducers and telemetry helpers for LLM synthesis outputs."""

from __future__ import annotations

import logging
from typing import Any, cast

from pydantic import TypeAdapter, ValidationError

from backend_v2.database.factory import get_driver
from backend_v2.database.repository import UnifiedWorkflowRepository
from backend_v2.exceptions import ErrorCodes
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
from backend_v2.models.dtos.synthesis import (
    ExecutiveSummarySectionResult,
    MatrixExplanationContextDTO,
    MatrixExplanationsResult,
    MatrixSectionSynthesesResult,
    XaiHighlightsResult,
)
from backend_v2.models.dtos.trace import (
    ExecutionUpdateDTO,
    TraceEventMetadataEnvelope,
)
from backend_v2.models.enums import ExecutionStatus, RoleClassification
from backend_v2.models.state import (
    ErrorTraceEvent,
    TombstoneEvent,
    TraceEvent,
)
from backend_v2.models.v2_core import DataStarvationEvent, RenderedSynthesisCache
from backend_v2.models.view.sdui import AnySduiBlock, ParagraphBlock
from backend_v2.services.length_budget_enforcer import enforce_sentence_boundary_budget
from backend_v2.services.storage import get_storage_driver
from backend_v2.settings import get_settings

__all__ = [
    "extract_user_role_from_trace",
    "handle_synthesis_failure_state",
    "handle_starvation_if_detected",
    "process_executive_summary_result",
    "process_matrix_sections_result",
    "process_row_explanations_result",
    "process_xai_highlights_result",
    "recover_trace_telemetry",
]

logger = logging.getLogger(__name__)


def extract_user_role_from_trace(
    execution: ExecutionRecord,
    role_target_block_id: str,
    default_role: str | None = None,
    default_justification: str | None = None,
) -> tuple[str | None, str | None]:
    """Extract user role and justification deterministically from evaluated matrix score."""
    role_raw_score: float | None = None
    if execution.execution_trace:
        for event in execution.execution_trace:
            if event.event_type == "output":
                try:
                    out_content = TypeAdapter(dict[str, Any]).validate_python(event.content)
                    if role_target_block_id in out_content:
                        role_mat_out = LightweightMatrixOutput.model_validate(
                            out_content[role_target_block_id], strict=False
                        )
                        if role_mat_out.raw_score is not None:
                            role_raw_score = float(role_mat_out.raw_score)
                            break
                except ValidationError, TypeError, ValueError:
                    pass
    if role_raw_score is not None:
        clamped_score = max(1, min(5, int(round(role_raw_score))))
        _role_score_map: dict[int, RoleClassification] = {
            1: RoleClassification.PASSENGER,
            2: RoleClassification.PASSENGER,
            3: RoleClassification.NAVIGATOR,
            4: RoleClassification.DRIVER,
            5: RoleClassification.ARCHITECT,
        }
        user_role_val = _role_score_map[clamped_score].value
        user_role_just = (
            f"Derived deterministically from evaluated matrix '{role_target_block_id}' score {role_raw_score}."
        )
        return user_role_val, user_role_just

    return default_role, default_justification


def process_executive_summary_result(
    result_tuple: tuple[Any, Any] | None,
    active_profile_dto: OutputProfile | None,
) -> tuple[ExecutiveSummarySectionResult | None, list[AnySduiBlock], float, int]:
    """Process executive summary result, apply length constraint, and return blocks & usage."""
    if not result_tuple:
        return None, [], 0.0, 0
    exec_res, usage = result_tuple
    exec_dto = exec_res if isinstance(exec_res, ExecutiveSummarySectionResult) else None
    blocks: list[AnySduiBlock] = []
    if exec_dto and exec_dto.executive_summary:
        summary_blocks = exec_dto.executive_summary
        if active_profile_dto and active_profile_dto.synthesis_length_constraint:
            budget = active_profile_dto.synthesis_length_constraint
            budgeted = []
            for blk in summary_blocks:
                if isinstance(blk, ParagraphBlock) and len(blk.text) > budget:
                    blk = blk.model_copy(update={"text": enforce_sentence_boundary_budget(blk.text, budget)})
                budgeted.append(blk)
            summary_blocks = budgeted
            exec_dto = exec_dto.model_copy(update={"executive_summary": summary_blocks})
        blocks = cast(list[AnySduiBlock], summary_blocks)

    cost = usage.cost_usd if usage else 0.0
    tokens = usage.total_tokens if usage else 0
    return exec_dto, blocks, cost, tokens


def process_matrix_sections_result(
    task_results: list[tuple[str, tuple[Any, Any] | None]],
) -> tuple[dict[str, list[AnySduiBlock]], float, int]:
    """Process matrix synthesis sections and calculate aggregated token usage."""
    sec_dict: dict[str, list[AnySduiBlock]] = {}
    cost = 0.0
    tokens = 0
    for lay_id, res_tuple in task_results:
        if not res_tuple:
            continue
        mat_res, usage = res_tuple
        if mat_res and isinstance(mat_res, MatrixSectionSynthesesResult):
            aggregated: list[AnySduiBlock] = []
            for sec in mat_res.sections:
                if sec.content_blocks:
                    aggregated.extend(cast(list[AnySduiBlock], sec.content_blocks))
            if aggregated:
                sec_dict[lay_id] = aggregated
        if usage:
            cost += usage.cost_usd
            tokens += usage.total_tokens
    return sec_dict, cost, tokens


def process_xai_highlights_result(
    result_tuple: tuple[Any, Any] | None,
    active_profile_dto: OutputProfile | None,
) -> tuple[list[Any], float, int]:
    """Process XAI highlights result and enforce length constraint."""
    if not result_tuple:
        return [], 0.0, 0
    xai_res, usage = result_tuple
    highlights = []
    if xai_res and isinstance(xai_res, XaiHighlightsResult):
        highlights = xai_res.xai_highlights
        if active_profile_dto and active_profile_dto.xai_length_constraint:
            budget = active_profile_dto.xai_length_constraint
            highlights = [
                item.model_copy(update={"content": enforce_sentence_boundary_budget(item.content, budget)})
                if len(item.content) > budget
                else item
                for item in highlights
            ]
    cost = usage.cost_usd if usage else 0.0
    tokens = usage.total_tokens if usage else 0
    return highlights, cost, tokens


def process_row_explanations_result(
    result_tuple: tuple[Any, Any] | None,
    matrices_to_explain: list[MatrixExplanationContextDTO],
    active_profile_dto: OutputProfile | None,
) -> tuple[dict[str, str], float, int]:
    """Process row explanations and format cache map."""
    if not result_tuple:
        return {}, 0.0, 0
    row_dto, usage = result_tuple
    raw_map: dict[str, str] = {}
    if row_dto and isinstance(row_dto, MatrixExplanationsResult) and row_dto.explanations:
        raw_map = {item.matrix_id: item.row_explanation for item in row_dto.explanations}

    cache_explanations: dict[str, str] = {}
    for m_dto in matrices_to_explain:
        real_id = m_dto.real_matrix_id
        alias_id = m_dto.matrix_id
        if not real_id:
            continue
        expl = " - "
        if alias_id in raw_map:
            expl = raw_map[alias_id]
        elif real_id in raw_map:
            expl = raw_map[real_id]
        if (
            expl
            and expl.strip() not in {"-", " - "}
            and active_profile_dto
            and active_profile_dto.row_explanation_length_constraint
        ):
            if len(expl) > active_profile_dto.row_explanation_length_constraint:
                expl = enforce_sentence_boundary_budget(expl, active_profile_dto.row_explanation_length_constraint)
        cache_explanations[real_id] = expl

    cost = usage.cost_usd if usage else 0.0
    tokens = usage.total_tokens if usage else 0
    return cache_explanations, cost, tokens


async def handle_starvation_if_detected(
    execution: ExecutionRecord,
    profile_id: str | None,
    accept_language: str,
    repo: Any,
    redis: Any | None,
    update_render_status_fn: Any,
) -> bool:
    """Check for data starvation event and short-circuit if detected."""
    starvation_detected = False
    for trace_evt in execution.execution_trace:
        if trace_evt.event_type == "output":
            try:
                t_content = TypeAdapter(dict[str, Any]).validate_python(trace_evt.content)
                if t_content.get("event_type") == "starvation":
                    starvation_detected = True
                    break
            except ValidationError, ValueError, TypeError, KeyError:
                continue

    if not starvation_detected:
        return False

    logger.warning("[Task] Data starvation detected in execution %s trace. Short-circuiting.", execution.id)
    starvation_dto = DataStarvationEvent(total_atoms=0, reason="Data starvation: insufficient atoms")
    cache = RenderedSynthesisCache(
        section_syntheses={},
        row_explanations={},
        cited_sources=[],
        xai_highlights=[],
        user_role=None,
        user_role_justification=None,
        extension_metrics=None,
        data_starvation=starvation_dto,
    )
    current_syntheses: dict[str, Any] = {}
    if execution.profile_syntheses is not None:
        current_syntheses = dict(execution.profile_syntheses)
    starvation_pid = profile_id if profile_id is not None else "default"
    current_syntheses[starvation_pid] = cache
    await repo.update_execution(execution.id, ExecutionUpdateDTO(profile_syntheses=current_syntheses))
    await update_render_status_fn("Compiling output documents...")
    if redis:
        await redis.enqueue_job("generate_pdf_job", execution.id, accept_language, profile_id)
    return True


async def recover_trace_telemetry(
    execution: ExecutionRecord,
    dag_cost: float,
) -> tuple[float, int | None, int | None, int | None, int | None]:
    """Recover DAG telemetry tokens and cost from offloaded execution trace blob if needed."""
    rec_p = None
    rec_c = None
    rec_cac = None
    rec_r = None
    final_cost = dag_cost

    if final_cost == 0.0 and execution.execution_trace_storage_path:
        try:
            storage_driver = get_storage_driver()
            blob_data = await storage_driver.read(execution.execution_trace_storage_path)
            if blob_data:
                stored_trace = TypeAdapter(list[ErrorTraceEvent | TombstoneEvent | TraceEvent]).validate_json(blob_data)
                p, c, cac, r, cost = 0, 0, 0, 0, 0.0
                for ev in stored_trace:
                    if ev.content:
                        try:
                            env = TraceEventMetadataEnvelope.model_validate(ev.content)
                            if env.step_metadata and env.step_metadata.token_usage:
                                u = env.step_metadata.token_usage
                                p += u.prompt_tokens
                                c += u.completion_tokens
                                cac += u.cached_tokens
                                r += u.reasoning_tokens
                                cost += u.cost_usd
                        except ValidationError, ValueError:
                            pass
                if cost > 0.0:
                    final_cost = cost
                if p > 0 or c > 0:
                    rec_p, rec_c, rec_cac, rec_r = p, c, cac, r
        except (OSError, UnicodeDecodeError, ValidationError, ValueError, KeyError) as err:
            logger.warning("[Task] Failed to recover DAG telemetry from storage blob: %s", err)

    return final_cost, rec_p, rec_c, rec_cac, rec_r


async def handle_synthesis_failure_state(
    execution_id: str,
    profile_id: str | None,
    error: Exception,
) -> None:
    """Quarantine Phase 3 failure by updating virtual step state without failing ExecutionRecord status."""
    if not profile_id:
        return
    try:
        driver = await get_driver(get_settings())
        repo = UnifiedWorkflowRepository(driver)
        v_step_id = f"sys_render_{profile_id}"
        fail_step_states = None
        fail_steps = None
        exec_record_local = await repo.get_execution(execution_id, hydrate=False)
        if exec_record_local:
            exec_record_local = ExecutionRecord.model_validate(exec_record_local, strict=False)
            if v_step_id in exec_record_local.step_states:
                old_state = exec_record_local.step_states[v_step_id]
                updated_state = old_state.model_copy(
                    update={
                        "status": ExecutionStatus.FAILED,
                        "last_error": str(error),
                        "progress": None,
                        "has_warning": True,
                    }
                )
                new_step_states = dict(exec_record_local.step_states)
                new_step_states[v_step_id] = updated_state
                new_steps = [
                    s.model_copy(
                        update={
                            "status": ExecutionStatus.FAILED,
                            "last_error": str(error),
                            "progress": None,
                            "has_warning": True,
                        }
                    )
                    if s.id == v_step_id
                    else s
                    for s in exec_record_local.steps
                ]
                exec_record_local = exec_record_local.model_copy(
                    update={"step_states": new_step_states, "steps": new_steps}
                )
                fail_step_states = exec_record_local.step_states
                fail_steps = exec_record_local.steps

        # REQ-02 / Phase 3 Failure Quarantine:
        # Do NOT update ExecutionRecord.status to FAILED. Preserve Phase 1 PASSED status.
        await repo.update_execution(
            execution_id,
            ExecutionUpdateDTO(
                steps=fail_steps,
                step_states=fail_step_states,
            ),
        )
    except OSError, ValidationError, ValueError, KeyError:
        logger.error(
            "[Task] Failed to update execution failure status",
            exc_info=True,
            extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
        )

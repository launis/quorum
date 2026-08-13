"""Synthesis Distiller Hook for the Cognitive Quorum DAG Pipeline.

Replaces the legacy 'God Code' in synthesis.py by providing a deterministic
logic DAG node that distills evaluation data, fetches historical context,
and prepares the matrices_to_explain list for the downstream row explanations
LLM step.

Epic 93 Phase 2: Pipeline Unification — Milestone 1.
"""

import json
import logging

from fastapi import status

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState, hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.enums import HistoricalContextMode
from backend_v2.models.state import StepOutputDTO
from backend_v2.models.v2_core import ExecutionRecord, PromptBlock, Step, Workflow
from backend_v2.utils.alias_engine import AliasEngine

logger = logging.getLogger(__name__)


from backend_v2.services.orchestrator.matrix_explanation_service import MatrixExplanationService
from backend_v2.services.orchestrator.synthesis_payload_compressor import SynthesisPayloadCompressor


async def _fetch_historical_context(
    mode: HistoricalContextMode, deps: HookDependencies, state: HookState, profile_to_use: str
) -> str:
    """Fetch and format historical execution summaries based on the selected mode.

    Args:
        mode: The requested historical context retrieval strategy.
        deps: Global hook dependencies.
        state: Executing context state.
        profile_to_use: Evaluated target output profile ID.

    Returns:
        Markdown structured historical context string or empty string if disabled.
    """
    # Epic 93 Phase 2, Milestone 1.3: Historical context fetch inside distiller hook
    if mode == HistoricalContextMode.DISABLED:
        return ""

    try:
        user_id = state.global_context_vars["user_id"]
    except KeyError:
        user_id = None

    try:
        org_id = state.global_context_vars["organization_id"]
    except KeyError:
        org_id = None

    if not (user_id or org_id):
        return ""

    logger.debug(
        "[SynthesisDistiller] Fetching historical summary for org_id=%s, user_id=%s, mode=%s",
        org_id,
        user_id,
        mode.value,
    )
    all_execs = await deps.exec_repo.get_all_executions(organization_id=org_id, user_id=user_id)

    valid_past = []
    for e in all_execs:
        if e.id == state.execution_id:
            continue
        if e.status.value != "completed":
            continue

        best_cache = None
        if e.profile_syntheses:
            if profile_to_use in e.profile_syntheses:
                best_cache = e.profile_syntheses[profile_to_use]
            else:
                continue

        if not best_cache or not best_cache.section_syntheses:
            continue

        all_blocks = []
        for blocks in best_cache.section_syntheses.values():
            all_blocks.extend(blocks)

        if not all_blocks:
            continue

        valid_past.append((e, json.dumps([b.model_dump(mode="json") for b in all_blocks], ensure_ascii=False)))

    valid_past.sort(key=lambda x: x[0].completed_at or x[0].created_at, reverse=True)

    if mode == HistoricalContextMode.SLIDING_WINDOW_3:
        valid_past = valid_past[:3]

    if not valid_past:
        return ""

    historical_parts = []
    for past_e, past_md in reversed(valid_past):
        dt_str = past_e.completed_at.strftime("%Y-%m-%d") if past_e.completed_at else "Unknown Date"
        historical_parts.append(f"--- Execution Date: {dt_str} ---\n{past_md}")

    return "<HistoricalContext>\n" + "\n\n".join(historical_parts) + "\n</HistoricalContext>\n\n"


def _build_title_map(workflow_data: Workflow | None, all_steps: list[Step], language: str) -> dict[str, str]:
    """Build an O(1) lookup map for resolving localized step and input titles.

    Args:
        workflow_data: The SSOT workflow definition blueprint.
        all_steps: Master list of all steps from the registry.
        language: Target translation locale code.

    Returns:
        Dictionary mapping step/input keys to resolved title strings.

    Raises:
        AppException: If a step references a missing blueprint (VALIDATION_FAILED).
    """
    # Epic 93 Phase 2, Milestone 1.4: Title map migration
    title_map: dict[str, str] = {}
    if not workflow_data:
        return title_map

    if workflow_data.steps:
        step_def_map = {s.id: s for s in all_steps}
        for step in workflow_data.steps:
            try:
                target_step = step_def_map[step.task_blueprint]
            except KeyError:
                target_step = None

            if not target_step:
                msg = (
                    f"Data integrity failure: StepRule '{step.id}' "
                    f"references missing Step (TaskBlueprint) '{step.task_blueprint}'."
                )
                logger.error("[SynthesisDistiller] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise AppException(
                    message=msg,
                    status_code=400,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

            title_map[str(step.id).lower()] = target_step.name.resolve(language)

    if workflow_data.expected_inputs:
        for exp_in in workflow_data.expected_inputs:
            title_map[str(exp_in.input_key).lower()] = exp_in.label.resolve(language)

    return title_map


@hook_registry.register(name="synthesis_distiller_hook")
async def synthesis_distiller_hook(state: HookState, deps: HookDependencies) -> HookResult:
    """HOOK: synthesis_distiller_hook.

    Logic DAG node that distills execution state data for downstream synthesis and
    row explanation LLM steps. Performs metadata stripping, historical context
    fetching, title map resolution, and matrices_to_explain assembly.

    Epic 93 Phase 2, Milestone 1.6: Hook registration.

    Args:
        state: Immutable cognitive state including inputs.
        deps: HookDependencies providing data access.

    Returns:
        HookResult with state_delta containing distilled_inputs, historical_context,
        title_map, and matrices_to_explain.

    Raises:
        AppException: If state or metadata validation fails.
    """
    logger.debug("[SynthesisDistiller] Running synthesis_distiller_hook...")

    if not state:
        msg = "Strict Fail-Fast Enforced: Missing HookState in synthesis_distiller_hook."
        logger.error("[SynthesisDistiller] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

    inputs = state.inputs
    if not isinstance(inputs, dict):
        msg = "Missing or invalid 'inputs'. Expected dict."
        logger.error("[SynthesisDistiller] %s: %s", ErrorCodes.INVALID_OUTPUT_SCHEMA.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value},
        )

    if "steps" not in inputs:
        msg = "Strict Fail-Fast Enforced: 'steps' key is missing from state inputs."
        logger.error("[SynthesisDistiller] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

    # Phase 2, Milestone 1.6: Parse available DTOs from state
    available_dtos: list[StepOutputDTO] = []
    steps_list = inputs["steps"]
    if isinstance(steps_list, list):
        for item in steps_list:
            if isinstance(item, StepOutputDTO):
                available_dtos.append(item)
            elif isinstance(item, dict):
                available_dtos.append(StepOutputDTO.model_validate(item))

    # Phase 2, Milestone 1.6: Fetch workflow and execution for context resolution
    raw_workflow_data = await deps.workflow_repo.get_workflow_by_id(state.workflow_id)
    if not raw_workflow_data:
        msg = f"Workflow '{state.workflow_id}' not found."
        raise AppException(
            message=msg,
            status_code=status.HTTP_404_NOT_FOUND,
            details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
        )
    workflow_data = Workflow.model_validate(raw_workflow_data)

    raw_exec_data = await deps.exec_repo.get_execution(state.execution_id)
    execution_data = ExecutionRecord.model_validate(raw_exec_data) if raw_exec_data else None

    output_profile_id = execution_data.output_profile_id if execution_data else None
    if not output_profile_id:
        msg = f"Execution {state.execution_id} missing mandatory output_profile_id."
        logger.error("[SynthesisDistiller] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        )

    # Phase 2, Milestone 1.6: Resolve output profile for historical context mode
    p_dict = await deps.output_profile_repo.get_output_profile_by_id(output_profile_id)
    if not p_dict:
        msg = f"Resolved output profile '{output_profile_id}' not found in SSOT database."
        logger.error("[SynthesisDistiller] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
        raise AppException(
            message=msg,
            status_code=status.HTTP_404_NOT_FOUND,
            details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
        )

    # ARCHITECTURAL MANDATE: Filter available_dtos based on Output Profile target_blocks
    # This strictly limits Token Context Window explosions during LLM Synthesis
    target_block_ids = set()
    for layout in p_dict.get("layouts", []):
        tbs = layout.get("target_blocks", [])
        if tbs:
            for tb in tbs:
                if isinstance(tb, str):
                    target_block_ids.add(tb)
                elif hasattr(tb, "value"):
                    target_block_ids.add(tb.value)
                elif isinstance(tb, dict) and "value" in tb:
                    target_block_ids.add(tb["value"])

    filtered_dtos = []
    for dto in available_dtos:
        if "*" in target_block_ids or dto.block_id in target_block_ids:
            filtered_dtos.append(dto)
        else:
            logger.debug(f"[SynthesisDistiller] Skipping {dto.block_id} - not in target_blocks.")
    available_dtos = filtered_dtos

    if not state.metadata or "target_locale" not in state.metadata:
        msg = "Strict Fail-Fast Enforced: 'target_locale' missing from execution metadata."
        logger.error("[SynthesisDistiller] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
    language = str(state.metadata["target_locale"]).strip().lower()

    historical_mode = workflow_data.historical_context_mode

    # Phase 2, Milestone 1.3: Fetch historical context inside distiller
    historical_context_text = await _fetch_historical_context(
        mode=historical_mode, deps=deps, state=state, profile_to_use=output_profile_id
    )

    # Phase 2, Milestone 1.4: Build title map
    raw_steps = await deps.workflow_repo.get_all_steps()
    all_steps = [Step.model_validate(rs) for rs in raw_steps]

    title_map = _build_title_map(workflow_data, all_steps, language)

    alias_engine = AliasEngine()

    uid_to_alias: dict[str, str] = {}
    for step_dto_obj in available_dtos:
        step_id = step_dto_obj.step_id
        block_id = step_dto_obj.block_id
        uid = f"{step_id}_{block_id}"
        uid_to_alias[uid] = alias_engine.register(uid, prefix="DOC-")

    consolidated_distilled_parts: list[str] = []

    for step_dto_obj in available_dtos:
        step_id = step_dto_obj.step_id
        block_id = step_dto_obj.block_id
        uid = f"{step_id}_{block_id}"

        short_alias = uid_to_alias.get(uid, uid)

        k_str = uid.lower()
        step_title = title_map[k_str] if k_str in title_map else str(uid)
        v_str = SynthesisPayloadCompressor.compress_synthesis_payload(step_dto_obj.payload)

        # Inject the SHORT ALIAS instead of the long UID
        consolidated_distilled_parts.append(f'<source id="{short_alias}" title="{step_title}">\n{v_str}\n</source>')

    # Phase 2, Milestone 1.5: Assemble matrices_to_explain
    raw_blocks = await deps.prompt_block_repo.get_all_prompt_blocks()
    blocks_by_id = {str(b["id"]): PromptBlock.model_validate(b) for b in raw_blocks if "id" in b}
    matrices_to_explain = MatrixExplanationService.assemble_matrices_to_explain(available_dtos, title_map, blocks_by_id)

    return HookResult(
        success=True,
        state_delta={
            "distilled_inputs": "\n\n".join(consolidated_distilled_parts),
            "historical_context": historical_context_text,
            "title_map": title_map,
            "matrices_to_explain": matrices_to_explain,
            "source_alias_map": alias_engine.alias_map,
            "output_profile_id": output_profile_id,
            "language": language,
            "alias_registry": alias_engine.alias_map,
            "max_extensions": p_dict.get("max_extension_items", 3),
        },
    )

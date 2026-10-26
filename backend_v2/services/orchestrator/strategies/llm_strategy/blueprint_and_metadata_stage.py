"""Stage 1 blueprint resolution, pre-hook execution, and step context metadata helpers."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable, Mapping
from dataclasses import dataclass
from typing import Any

from pydantic import JsonValue

from backend_v2.core.hook_registry import ExecutionInputsDTO, GlobalContextVarsDTO, HookDependencies, HookState
from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.models.domain.inputs import DomainInputValue
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import PromptBlock, PromptBlockAdapter
from backend_v2.models.domain.step import Step as V2Step
from backend_v2.models.domain.step import StepRule
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.atom_result import AtomResultDTO
from backend_v2.models.dtos.hook_delta import StepContextMetadataDTO
from backend_v2.models.dtos.step_output import StepOutputDTO
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import StateProjector, TraceEvent
from backend_v2.services.orchestrator.strategies.base import StrategyContext, StrategyDependencies
from backend_v2.services.orchestrator.strategies.llm_execution.source_document_packer import SourceDocumentPacker

__all__ = [
    "BlueprintStageResult",
    "NodeStatePayload",
    "_SCHEMA_BLOCK_EXTENSION",
    "_SCHEMA_BLOCK_MATRIX",
    "_SCHEMA_BLOCK_SYSTEM",
    "_SCHEMA_BLOCK_TEXT",
    "dlq_handle_debug_log_error",
    "execute_blueprint_and_pre_hooks_stage",
    "extract_step_context_metadata",
]

logger = logging.getLogger(__name__)

# Schema block category constants and state payload type alias for Stage 1-2 routing.
_SCHEMA_BLOCK_MATRIX = "MATRIX"
_SCHEMA_BLOCK_TEXT = "TEXT"
_SCHEMA_BLOCK_EXTENSION = "EXTENSION"
_SCHEMA_BLOCK_SYSTEM = "SYSTEM"

type NodeStatePayload = DomainInputValue | ExecutionMetadata | Mapping[str, DomainInputValue] | list[Any] | JsonValue
type PreHooksRunner = Callable[
    [V2Step, StepRule, HookState, HookDependencies], Awaitable[tuple[HookState, list[TraceEvent]]]
]


def dlq_handle_debug_log_error(exc: Exception, step_logger: logging.Logger = logger) -> None:
    """Handle debug prompt logging failures in development gracefully.

    Args:
        exc: Exception encountered during debug prompt logging.
        step_logger: Logger instance used to emit structured warning logs.
    """
    step_logger.warning("[LLMStrategy] Failed to write debug prompt log: %s", exc)


def extract_step_context_metadata(
    hook_state: HookState,
    context: StrategyContext | None = None,
) -> StepContextMetadataDTO:
    """Extract global vars, document aliases, and DAG input results from HookState.

    Args:
        hook_state: Ingress hook state holding inputs and context variables.
        context: Strategy configuration parameters holding context_variables.

    Returns:
        StepContextMetadataDTO containing gvars, doc_aliases, and dag_results.
    """
    gvars = {}
    if isinstance(hook_state.global_context_vars, GlobalContextVarsDTO):
        gvars = hook_state.global_context_vars.model_dump(mode="json", exclude_none=True)
    elif (
        not isinstance(hook_state.global_context_vars, (str, int, float, bool, list))
        and hook_state.global_context_vars is not None
    ):
        gvars = dict(hook_state.global_context_vars)
    doc_aliases: list[str] = ["N/A"]
    if context is not None and context.context_variables.global_atom_blackboard is not None:
        atoms_by_input = context.context_variables.global_atom_blackboard.atoms_by_input
        if atoms_by_input:
            doc_aliases = list(atoms_by_input.keys())
    raw_inputs_dict: Mapping[str, DomainInputValue] = hook_state.inputs.raw_inputs
    dynamic_inputs_dict: Mapping[str, DomainInputValue] = hook_state.inputs.dynamic_inputs
    dag_results: dict[str, AtomResultDTO] = {}
    candidate_items: list[Any] = []
    combined_inputs: list[Any] = list(raw_inputs_dict.values()) + list(dynamic_inputs_dict.values())
    for step_res in combined_inputs:
        if isinstance(step_res, list):
            candidate_items.extend(step_res)
        elif isinstance(step_res, AtomResultDTO):
            dag_results[step_res.tda_id] = step_res
        elif not isinstance(step_res, (str, int, float, bool, list)) and step_res is not None:
            if "results" in step_res and isinstance(step_res["results"], list):
                candidate_items.extend(step_res["results"])
    for item in candidate_items:
        if isinstance(item, AtomResultDTO):
            dag_results[item.tda_id] = item
        elif not isinstance(item, (str, int, float, bool, list)) and item is not None:
            a_id = None
            if "tda_id" in item:
                a_id = item["tda_id"]
            elif "atom_id" in item:
                a_id = item["atom_id"]
            if a_id:
                item_dict = dict(item)
                if "atom_id" in item_dict:
                    del item_dict["atom_id"]
                if "status" not in item_dict:
                    item_dict["status"] = ExecutionStatus.PASSED
                if "source_quotes" not in item_dict and (
                    "contextual_override" not in item_dict or not item_dict["contextual_override"]
                ):
                    item_dict["contextual_override"] = True
                if "evaluation_reasoning" not in item_dict:
                    item_dict["evaluation_reasoning"] = "Extracted"
                if "tda_id" not in item_dict:
                    item_dict["tda_id"] = str(a_id)
                dag_results[str(a_id)] = AtomResultDTO.model_validate(item_dict, strict=False)
    return StepContextMetadataDTO(gvars=gvars, doc_aliases=doc_aliases, dag_results=dag_results)


@dataclass(frozen=True)
class BlueprintStageResult:
    """Immutable output container for Stage 1 blueprint and pre-hook execution.

    Attributes:
        step_obj: Validated V2Step blueprint entity.
        workflow_obj: Optional validated parent Workflow entity.
        hook_state: Resulting HookState after executing step pre-hooks.
        hook_deps: Dependency container injected into step hooks.
        pre_events: Ordered list of TraceEvents emitted by pre-hooks.
        block_map: Mapping of PromptBlock IDs to validated PromptBlock models.
        role_block: Optional resolved Agent Role PromptBlock.
        protocol_block: Optional resolved Extraction Protocol PromptBlock.
        execution_persona_block: Optional resolved Execution Persona PromptBlock.
        criteria_blocks_models: Ordered list of resolved criteria PromptBlock models.
        output_profile_id: Mandatory target OutputProfile identifier.
        output_profile: Resolved OutputProfile domain model.
        target_locale: Target locale code for execution.
        global_source_text: Packed source document text payload.
        state_data: Dynamic node state payload mapping after pre-hooks.
        inputs_payload: Structured ExecutionInputsDTO passed into HookState.
    """

    step_obj: V2Step
    workflow_obj: Workflow | None
    hook_state: HookState
    hook_deps: HookDependencies
    pre_events: list[TraceEvent]
    block_map: dict[str, PromptBlock]
    role_block: PromptBlock | None
    protocol_block: PromptBlock | None
    execution_persona_block: PromptBlock | None
    criteria_blocks_models: list[PromptBlock]
    output_profile_id: str
    output_profile: OutputProfile
    target_locale: str
    global_source_text: str
    state_data: dict[str, NodeStatePayload]
    inputs_payload: ExecutionInputsDTO


def _resolve_optional_prompt_block(
    block_id: str | None,
    block_label: str,
    block_map: Mapping[str, PromptBlock],
    step_id: str,
    step_logger: logging.Logger,
) -> PromptBlock | None:
    """Resolve an optional prompt block by ID from block_map or raise ConfigurationError.

    Args:
        block_id: Optional PromptBlock identifier configured on the step.
        block_label: Human-readable block category label for error reporting.
        block_map: Mapping of available PromptBlock IDs to models.
        step_id: Step identifier for structured error logging.
        step_logger: Logger instance used to emit RFC 7807 error logs.

    Returns:
        Resolved PromptBlock model or None when block_id is not configured.

    Raises:
        ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if block_id is missing.
    """
    if not block_id:
        return None
    if block_id in block_map:
        return block_map[block_id]
    msg = f"{block_label} '{block_id}' not found."
    step_logger.error(msg, extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "step_id": step_id})
    raise ConfigurationError(msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})


async def _resolve_prompt_block_map(
    context: StrategyContext,
    deps: StrategyDependencies,
    step_logger: logging.Logger,
) -> dict[str, PromptBlock]:
    """Resolve the active PromptBlock lookup map from StrategyContext or repository.

    Args:
        context: Strategy configuration parameters holding pre-hydrated prompt_blocks.
        deps: Strategy dependencies container holding prompt_block_repo.
        step_logger: Logger instance used to emit RFC 7807 error logs.

    Returns:
        Mapping of PromptBlock IDs to validated PromptBlock domain models.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED if any database PromptBlock is malformed.
    """
    if isinstance(context.prompt_blocks, list) and context.prompt_blocks:
        return {b.id: b for b in context.prompt_blocks if b.id}

    all_prompt_blocks_raw = await deps.prompt_block_repo.get_all_prompt_blocks()
    all_prompt_blocks: list[PromptBlock] = []
    for raw in all_prompt_blocks_raw:
        try:
            all_prompt_blocks.append(PromptBlockAdapter.validate_python(raw, strict=False))
        except Exception as e:
            step_logger.error(
                "[LLMStrategy] Malformed PromptBlock in DB — Fail-Fast.",
                exc_info=True,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.name},
            )
            raise AppException(
                message="Malformed PromptBlock in DB",
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from e
    return {b.id: b for b in all_prompt_blocks if b.id}


def _resolve_initial_global_context_vars(context: StrategyContext) -> GlobalContextVarsDTO:
    """Resolve the initial GlobalContextVarsDTO from StrategyContext.

    Args:
        context: Strategy configuration parameters.

    Returns:
        Validated GlobalContextVarsDTO instance.
    """
    if isinstance(context.global_context_vars, GlobalContextVarsDTO):
        return context.global_context_vars
    if not isinstance(context.global_context_vars, (str, int, float, bool, list)) and context.global_context_vars:
        known_fields = GlobalContextVarsDTO.model_fields.keys()
        filtered_vars = {k: v for k, v in context.global_context_vars.items() if k in known_fields}
        return GlobalContextVarsDTO.model_validate(filtered_vars)
    return GlobalContextVarsDTO()


def _extract_state_data(hook_state: HookState) -> dict[str, NodeStatePayload]:
    """Extract dynamic state_data mapping from HookState after pre-hooks.

    Args:
        hook_state: HookState resulting from pre-hook execution.

    Returns:
        Mapping of dynamic state keys to NodeStatePayload values.
    """
    state_data: dict[str, NodeStatePayload]
    if isinstance(hook_state.inputs, ExecutionInputsDTO):
        state_data = dict(hook_state.inputs.dynamic_inputs)
        if "inputs" not in state_data and hook_state.inputs.raw_inputs:
            state_data["inputs"] = hook_state.inputs.raw_inputs
    elif not isinstance(hook_state.inputs, (str, int, float, bool, list)) and hook_state.inputs is not None:
        state_data = dict(hook_state.inputs)
    else:
        state_data = {}
    return state_data


async def execute_blueprint_and_pre_hooks_stage(
    step: StepRule,
    projector: StateProjector,
    context: StrategyContext,
    deps: StrategyDependencies,
    run_pre_hooks_fn: PreHooksRunner,
    step_logger: logging.Logger = logger,
) -> BlueprintStageResult:
    """Execute Stage 1 blueprint validation, pre-hooks, and prompt block resolution.

    Args:
        step: Rule defining the workflow execution block configuration.
        projector: Database representation of current structured historical trace.
        context: Strategy configuration parameters (model, metadata, strictness).
        deps: Strategy dependencies container holding repository interfaces.
        run_pre_hooks_fn: Bound pre-hook runner coroutine from the strategy instance.
        step_logger: Logger instance used to preserve logger name parity in error logs.

    Returns:
        BlueprintStageResult containing resolved entities, blocks, and hook state.

    Raises:
        AppException: With ErrorCodes.CONFIGURATION_ERROR, ErrorCodes.VALIDATION_FAILED,
            or ErrorCodes.RESOURCE_NOT_FOUND upon missing or malformed database entities.
        ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR upon missing configuration.
    """
    # Unpack source document inputs from state projection before running pre-hooks.
    raw_inputs_map = {d.block_id: d.payload for d in projector.snapshot if d.step_id == "inputs"}
    inputs_unwrapped: object = raw_inputs_map["inputs"] if "inputs" in raw_inputs_map else raw_inputs_map
    targets = SourceDocumentPacker.resolve_context_targets(step.input_mappings)
    global_source_text = SourceDocumentPacker.pack(
        inputs_unwrapped, context.expected_inputs, targets=targets, step_outputs=projector.snapshot
    )
    snapshot_steps: list[StepOutputDTO] = []
    if isinstance(projector.snapshot, list):
        snapshot_steps = list(projector.snapshot)
    current_state: dict[str, DomainInputValue] = {"steps": snapshot_steps}
    blueprint_id = step.task_blueprint
    if not blueprint_id:
        msg = f"Step {step.id} has no task_blueprint configured."
        step_logger.error(
            "Step has no task_blueprint configured.",
            extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "step_id": step.id},
        )
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})
    step_candidate = await deps.workflow_repo.get_step_by_id(blueprint_id)
    if not step_candidate:
        msg = f"Configuration error: Step '{blueprint_id}' not found."
        step_logger.error(msg, extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "step_id": step.id})
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})
    step_obj = step_candidate if isinstance(step_candidate, V2Step) else V2Step.model_validate(step_candidate)

    hook_deps = HookDependencies(
        exec_repo=deps.exec_repo,
        workflow_repo=deps.workflow_repo,
        comp_repo=deps.comp_repo,
        prompt_block_repo=deps.prompt_block_repo,
        output_profile_repo=deps.output_profile_repo,
        identity_repo=deps.identity_repo,
        audit_repo=deps.audit_repo,
        system_repo=deps.system_repo,
    )
    initial_gvars = _resolve_initial_global_context_vars(context)
    safe_raw_inputs: dict[str, DomainInputValue] = {}
    if type(inputs_unwrapped) is dict:
        safe_raw_inputs = dict(inputs_unwrapped)
    inputs_dto = ExecutionInputsDTO(dynamic_inputs=current_state, raw_inputs=safe_raw_inputs)
    hook_state = HookState(
        execution_id=context.execution_id,
        workflow_id=context.workflow_id,
        step_id=step.id,
        task_blueprint=blueprint_id,
        metadata=context.metadata,
        global_context_vars=initial_gvars,
        inputs=inputs_dto,
    )
    hook_state, pre_events = await run_pre_hooks_fn(step_obj, step, hook_state, hook_deps)
    state_data = _extract_state_data(hook_state)
    block_map = await _resolve_prompt_block_map(context, deps, step_logger)

    target_profile = context.output_profile_id
    if not target_profile:
        msg = f"ExecutionContext missing mandatory 'output_profile_id' for workflow {context.workflow_id}."
        step_logger.error(
            msg,
            extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "workflow_id": context.workflow_id},
        )
        raise ConfigurationError(msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})

    role_block = _resolve_optional_prompt_block(step_obj.role_block_id, "Role Block", block_map, step.id, step_logger)
    protocol_block = _resolve_optional_prompt_block(
        step_obj.extraction_protocol_block_id, "Extraction Protocol Block", block_map, step.id, step_logger
    )
    execution_persona_block = _resolve_optional_prompt_block(
        step_obj.execution_persona_block_id, "Execution Persona Block", block_map, step.id, step_logger
    )

    criteria_blocks_models: list[PromptBlock] = []
    for m_id in step_obj.criteria_block_ids:
        if m_id in block_map:
            criteria_blocks_models.append(block_map[m_id])
        else:
            msg = f"Criteria PromptBlock '{m_id}' not found."
            step_logger.error(msg, extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "step_id": step.id})
            raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

    target_locale = context.target_locale
    if not target_locale:
        msg = f"ExecutionContext missing mandatory 'target_locale' for workflow {context.workflow_id}."
        step_logger.error(
            msg,
            extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "workflow_id": context.workflow_id},
        )
        raise ConfigurationError(msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})

    workflow_candidate = await deps.workflow_repo.get_workflow(context.workflow_id)
    workflow_obj: Workflow | None = None
    if isinstance(workflow_candidate, Workflow):
        workflow_obj = workflow_candidate
    elif workflow_candidate:
        workflow_obj = Workflow.model_validate(workflow_candidate)

    profile_data = await deps.output_profile_repo.get_output_profile_by_id(target_profile)
    if not profile_data:
        msg = f"OutputProfile '{target_profile}' not found in database."
        step_logger.error(
            "[LLMStrategy] %s: %s",
            ErrorCodes.RESOURCE_NOT_FOUND.name,
            msg,
            extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.name, "output_profile_id": target_profile},
        )
        raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value})

    output_profile = (
        profile_data
        if isinstance(profile_data, OutputProfile)
        else OutputProfile.model_validate(profile_data, strict=False)
    )

    return BlueprintStageResult(
        step_obj=step_obj,
        workflow_obj=workflow_obj,
        hook_state=hook_state,
        hook_deps=hook_deps,
        pre_events=pre_events,
        block_map=block_map,
        role_block=role_block,
        protocol_block=protocol_block,
        execution_persona_block=execution_persona_block,
        criteria_blocks_models=criteria_blocks_models,
        output_profile_id=target_profile,
        output_profile=output_profile,
        target_locale=target_locale,
        global_source_text=global_source_text,
        state_data=state_data,
        inputs_payload=inputs_dto,
    )

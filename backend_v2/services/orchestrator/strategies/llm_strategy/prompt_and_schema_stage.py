"""Stage 2 context building, prompt compilation, atom chunking, and dynamic schema resolution."""

from __future__ import annotations

import inspect
import json
import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from backend_v2.core.hook_registry import GlobalContextVarsDTO, HookState
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.chunking import ChunkingRequest
from backend_v2.models.domain.execution import ExecutionRecord, FrozenContext
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock, PromptBlock
from backend_v2.models.domain.step import Step as V2Step
from backend_v2.models.domain.step import StepRule
from backend_v2.models.dtos.engine import FlattenedAtom
from backend_v2.models.dtos.prompt import PromptMappingDTO
from backend_v2.models.dtos.quote_evidence import SourceDocumentContext
from backend_v2.models.enums import PromptBlockCategory
from backend_v2.services.orchestrator.chunking_service import ChunkingService
from backend_v2.services.orchestrator.engines.synthesis_engine import SynthesisEngine
from backend_v2.services.orchestrator.strategies.base import StrategyContext, StrategyDependencies
from backend_v2.services.orchestrator.strategies.llm_execution.context_builder import ContextBuilder
from backend_v2.services.orchestrator.strategies.llm_execution.prompt_factory import PromptFactory, PromptPayload
from backend_v2.services.orchestrator.strategies.llm_strategy.blueprint_and_metadata_stage import (
    _SCHEMA_BLOCK_EXTENSION,
    _SCHEMA_BLOCK_MATRIX,
    _SCHEMA_BLOCK_SYSTEM,
    _SCHEMA_BLOCK_TEXT,
    BlueprintStageResult,
)
from backend_v2.settings import Settings, get_settings
from backend_v2.utils.alias_engine import AliasEngine

if TYPE_CHECKING:
    from backend_v2.services.orchestrator.engines.base import ExecutionEngine

__all__ = ["PromptAndSchemaStageResult", "execute_prompt_and_schema_stage"]

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class PromptAndSchemaStageResult:
    """Immutable output container for Stage 2 context building, prompt compilation, and schema resolution."""

    hook_state: HookState
    prompt_payload: PromptPayload
    user_payload: str
    criteria_blocks: list[PromptBlock]
    matrix_block: MatrixPromptBlock | None
    hydrated_shuffled_atoms: list[FlattenedAtom] | None
    target_chunks: list[Any]
    dynamic_schema: Any | None
    is_synthesis_step: bool
    source_doc_ctx: list[SourceDocumentContext]
    alias_engine: AliasEngine
    input_mappings: PromptMappingDTO
    schema_map: dict[str, str]
    blueprint_labels: dict[str, str]


async def _resolve_schema_map_and_labels(
    stage1: BlueprintStageResult,
    deps: StrategyDependencies,
) -> tuple[dict[str, str], dict[str, str]]:
    """Resolve workflow step schema_map and localized blueprint_labels for ContextBuilder.

    Args:
        stage1: Resolved Stage 1 blueprint and prompt block container.
        deps: Strategy dependencies container holding workflow_repo and prompt_compiler.

    Returns:
        2-tuple of (schema_map, blueprint_labels) mappings.
    """
    schema_map: dict[str, str] = {}
    blueprint_labels: dict[str, str] = {}
    if stage1.workflow_obj is None:
        return schema_map, blueprint_labels

    for s in stage1.workflow_obj.steps:
        is_matrix = False
        blueprint_def_raw = await deps.workflow_repo.get_step(s.task_blueprint)
        if blueprint_def_raw:
            blueprint_obj = V2Step.model_validate(blueprint_def_raw)
            if blueprint_obj.name:
                blueprint_labels[s.id] = deps.prompt_compiler.resolve_i18n(blueprint_obj.name, "en")
            all_bp_blocks: list[str] = []
            if blueprint_obj.role_block_id:
                all_bp_blocks.append(blueprint_obj.role_block_id)
            if blueprint_obj.extraction_protocol_block_id:
                all_bp_blocks.append(blueprint_obj.extraction_protocol_block_id)
            if blueprint_obj.execution_persona_block_id:
                all_bp_blocks.append(blueprint_obj.execution_persona_block_id)
            all_bp_blocks.extend(blueprint_obj.criteria_block_ids)

            for m_id in all_bp_blocks:
                if m_id in stage1.block_map:
                    b = stage1.block_map[m_id]
                    if b.category_id == PromptBlockCategory.MATRIX:
                        is_matrix = True
                        schema_map[m_id] = _SCHEMA_BLOCK_MATRIX
                    else:
                        schema_map[m_id] = _SCHEMA_BLOCK_TEXT
                    if b.output_extensions:
                        for ext in b.output_extensions:
                            schema_map[ext] = _SCHEMA_BLOCK_EXTENSION

        if is_matrix:
            schema_map[s.id] = _SCHEMA_BLOCK_MATRIX
        else:
            schema_map[s.id] = _SCHEMA_BLOCK_TEXT

    schema_map["_step_metadata"] = _SCHEMA_BLOCK_SYSTEM
    schema_map["_audit_signature"] = _SCHEMA_BLOCK_SYSTEM
    schema_map["inputs"] = _SCHEMA_BLOCK_TEXT
    schema_map["raw_inputs"] = _SCHEMA_BLOCK_TEXT
    schema_map["matrix_reducer"] = _SCHEMA_BLOCK_SYSTEM
    return schema_map, blueprint_labels


async def _validate_execution_source_documents(
    execution_id: str,
    inputs_payload: Any,
    deps: StrategyDependencies,
    step_logger: logging.Logger,
) -> list[SourceDocumentContext]:
    """Fetch ExecutionRecord and validate SourceDocumentContext entries for source documents.

    Args:
        execution_id: Execution identifier to query from exec_repo.
        inputs_payload: Raw inputs mapping extracted from Stage 1 HookState.
        deps: Strategy dependencies container holding exec_repo.
        step_logger: Logger instance used to emit structured RFC 7807 error logs.

    Returns:
        List of validated SourceDocumentContext models.

    Raises:
        AppException: With ErrorCodes.RESOURCE_NOT_FOUND or ErrorCodes.VALIDATION_FAILED
            when the execution record cannot be fetched or hydrated.
    """
    execution_record_raw = None
    try:
        res = deps.exec_repo.get_execution(execution_id)
        if inspect.isawaitable(res):
            execution_record_raw = await res
        else:
            execution_record_raw = res
    except Exception as e:
        step_logger.error(
            "[LLMStrategy] %s: Failed to fetch execution record '%s'",
            ErrorCodes.RESOURCE_NOT_FOUND.name,
            execution_id,
            exc_info=True,
            extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.name, "execution_id": execution_id},
        )
        raise AppException(
            message=f"Execution record '{execution_id}' not found.",
            status_code=404,
            details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
        ) from e

    source_docs: list[SourceDocumentContext] = []
    if execution_record_raw:
        try:
            if isinstance(execution_record_raw, ExecutionRecord):
                exec_obj = execution_record_raw
            else:
                exec_obj = ExecutionRecord.model_validate(execution_record_raw, strict=False)
            manifest: dict[str, str] = {}
            if exec_obj.source_identity_manifest is not None:
                manifest = exec_obj.source_identity_manifest

            inputs_dict: object = inputs_payload
            if type(inputs_payload) is dict and "inputs" in inputs_payload:
                inputs_dict = inputs_payload["inputs"]
            if type(inputs_dict) is dict:
                for k, text_content in inputs_dict.items():
                    if isinstance(text_content, str):
                        display_name = k
                        if k in manifest:
                            display_name = str(manifest[k])
                        doc_ctx = SourceDocumentContext(
                            opaque_id=k,
                            text_content=text_content,
                            display_name=display_name,
                        )
                        doc_ctx.model_dump(mode="json")
                        source_docs.append(doc_ctx)
        except Exception as e:
            step_logger.error(
                "[LLMStrategy] %s: Failed to construct source documents context from execution record '%s'",
                ErrorCodes.VALIDATION_FAILED.name,
                execution_id,
                exc_info=True,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "execution_id": execution_id},
            )
            raise AppException(
                message="Failed to parse execution record for source documents context.",
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from e
    return source_docs


async def execute_prompt_and_schema_stage(
    stage1: BlueprintStageResult,
    step: StepRule,
    context: StrategyContext,
    deps: StrategyDependencies,
    frozen_ctx: FrozenContext | None = None,
    engine: ExecutionEngine | None = None,
    settings_getter: Callable[[], Settings] = get_settings,
    step_logger: logging.Logger = logger,
) -> PromptAndSchemaStageResult:
    """Execute Stage 2 context building, prompt compilation, atom chunking, and schema resolution.

    Args:
        stage1: Resolved Stage 1 blueprint and pre-hook output container.
        step: Rule defining the workflow execution block configuration.
        context: Strategy configuration parameters (model, metadata, strictness).
        deps: Strategy dependencies container holding repositories and compiler.
        frozen_ctx: Optional frozen context snapshot triggering upfront schema compilation.
        engine: Optional execution engine instance to detect SynthesisEngine steps.
        settings_getter: Callable returning global Settings SSOT.
        step_logger: Logger instance used to preserve logger name parity in error logs.

    Returns:
        PromptAndSchemaStageResult encapsulating prompt payload, chunks, and dynamic schema.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED or ErrorCodes.RESOURCE_NOT_FOUND
            upon missing shuffled_atoms, invalid synthesis groups, or corrupted execution records.
    """
    # Phase 2, Step 1: Resolve schema_map, ContextBuilder, PromptFactory, chunking, and dynamic schema
    hook_state = stage1.hook_state
    output_profile = stage1.output_profile
    target_locale = stage1.target_locale
    criteria_blocks_models = stage1.criteria_blocks_models
    inputs_payload = stage1.inputs_payload.raw_inputs
    effective_mcp_tools = stage1.step_obj.allowed_mcp_tools
    input_mappings = PromptMappingDTO(mappings=dict(step.input_mappings))

    schema_map, blueprint_labels = await _resolve_schema_map_and_labels(stage1, deps)
    criteria_blocks = sorted(criteria_blocks_models, key=lambda x: str(x.id))

    llm_context_data, new_input_mappings = ContextBuilder.build(
        input_mappings=input_mappings,
        state_data=hook_state,
        output_profile=output_profile,
        schema_map=schema_map,
        criteria_blocks=criteria_blocks,
        blueprint_labels=blueprint_labels,
    )
    input_mappings = new_input_mappings

    has_shuffled_atoms = False
    hydrated_shuffled_atoms: list[FlattenedAtom] | None = None
    is_matrix_step = any(b.category_id == PromptBlockCategory.MATRIX for b in criteria_blocks_models)
    if is_matrix_step:
        shuffled_atoms = hook_state.global_context_vars.shuffled_atoms
        if shuffled_atoms is None:
            step_logger.error(
                "Matrix step missing 'shuffled_atoms' in global_context_vars.",
                exc_info=True,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.name},
            )
            raise AppException(
                message="Matrix step missing 'shuffled_atoms' in global_context_vars.",
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        if not isinstance(shuffled_atoms, list) or len(shuffled_atoms) == 0:
            msg = f"Strict Fail-Fast Enforced: 'shuffled_atoms' is empty or not a list for step '{step.id}'."
            step_logger.error(
                "[LLMStrategy] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "step_id": step.id},
            )
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        hydrated_shuffled_atoms = shuffled_atoms
        has_shuffled_atoms = True

    alias_engine = AliasEngine()
    prompt_gvars: GlobalContextVarsDTO | None = None
    if isinstance(hook_state.global_context_vars, GlobalContextVarsDTO):
        prompt_gvars = hook_state.global_context_vars
    elif (
        not isinstance(hook_state.global_context_vars, (str, int, float, bool, list))
        and hook_state.global_context_vars is not None
    ):
        prompt_gvars = GlobalContextVarsDTO.model_validate(dict(hook_state.global_context_vars))

    prompt_payload = PromptFactory.build(
        compiler=deps.prompt_compiler,
        role_block=stage1.role_block,
        protocol_block=stage1.protocol_block,
        execution_persona_block=stage1.execution_persona_block,
        criteria_blocks=criteria_blocks,
        target_locale=target_locale,
        effective_mcp_tools=effective_mcp_tools,
        input_mappings=input_mappings,
        llm_context_data=llm_context_data,
        expected_inputs=context.expected_inputs,
        has_shuffled_atoms=has_shuffled_atoms,
        execution_id=context.execution_id,
        alias_engine=alias_engine,
        global_context_vars=prompt_gvars,
    )

    user_payload = prompt_payload.user_payload
    if output_profile:
        exec_params = ["\n<execution_parameters>"]
        if output_profile.tone_instruction:
            tone = output_profile.tone_instruction.strip()
            if tone:
                exec_params.append(f"  <tone_instruction>{tone}</tone_instruction>")
        if output_profile.matrix_synthesis_groups:
            try:
                groups_json = json.dumps(
                    [grp.model_dump(mode="json") for grp in output_profile.matrix_synthesis_groups],
                    ensure_ascii=False,
                )
                exec_params.append(f"  <matrix_synthesis_groups>{groups_json}</matrix_synthesis_groups>")
            except (ValueError, TypeError) as e:
                step_logger.error(
                    "Failed to serialize matrix_synthesis_groups for prompt injection: %s",
                    e,
                    exc_info=True,
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "step_id": step.id},
                )
                raise AppException(
                    ErrorCodes.VALIDATION_FAILED,
                    details={"reason": f"Failed to serialize matrix_synthesis_groups: {e}"},
                ) from e
        exec_params.append("</execution_parameters>")
        if len(exec_params) > 2:
            user_payload += "\n" + "\n".join(exec_params)

    chunks_list: list[Any] = [None]
    if is_matrix_step and hydrated_shuffled_atoms:
        req = ChunkingRequest(
            parent_id=context.workflow_id,
            items=hydrated_shuffled_atoms,
            max_chunk_size=settings_getter().schema_max_evaluations,
        )
        chunks_list = ChunkingService.chunk_payload(req)

    source_doc_ids: list[str] = ["N/A"]
    if alias_engine.source_document_aliases:
        source_doc_ids = alias_engine.source_document_aliases

    source_doc_ctx = await _validate_execution_source_documents(
        execution_id=context.execution_id,
        inputs_payload=inputs_payload,
        deps=deps,
        step_logger=step_logger,
    )

    dynamic_schema: Any | None = None
    if frozen_ctx:
        dynamic_key_set: set[str] = set(input_mappings.keys())
        if context.expected_inputs:
            dynamic_key_set.update(e.input_key for e in context.expected_inputs)
        allowed_dynamic_keys = sorted(dynamic_key_set)
        dynamic_schema = deps.prompt_compiler.build_dynamic_schema(
            schema_name=f"Step_{step.id}_Response",
            criteria=criteria_blocks,
            has_shuffled_atoms=has_shuffled_atoms,
            target_locale=target_locale,
            strictness_level=context.strictness_level,
            source_document_ids=source_doc_ids,
            allowed_dynamic_keys=allowed_dynamic_keys,
        )

    matrix_block = next((b for b in criteria_blocks if isinstance(b, MatrixPromptBlock)), None)
    is_synthesis_step = isinstance(engine, SynthesisEngine)

    return PromptAndSchemaStageResult(
        hook_state=hook_state,
        prompt_payload=prompt_payload,
        user_payload=user_payload,
        criteria_blocks=criteria_blocks,
        matrix_block=matrix_block,
        hydrated_shuffled_atoms=hydrated_shuffled_atoms,
        target_chunks=chunks_list,
        dynamic_schema=dynamic_schema,
        is_synthesis_step=is_synthesis_step,
        source_doc_ctx=source_doc_ctx,
        alias_engine=alias_engine,
        input_mappings=input_mappings,
        schema_map=schema_map,
        blueprint_labels=blueprint_labels,
    )

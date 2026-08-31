"""LLM Node Strategy for DAG-based workflow execution.

Orchestrates AI/LLM step execution including dynamic schema compilation,
chunked map-reduce evaluation, DLQ graceful degradation, and anomaly retry logic.
"""

import asyncio
import inspect
import json
import logging
import time
from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING, Any, cast

from pydantic import BaseModel

from backend_v2.settings import get_settings

if TYPE_CHECKING:
    from backend_v2.services.orchestrator.engines.base import ExecutionEngine

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDependencies,
    HookState,
)
from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.models.chunking import ChunkingRequest
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import (
    MatrixPromptBlock,
    PromptBlock,
    PromptBlockAdapter,
)
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.engine import EngineExecutionRequest, MatrixEvaluationContext
from backend_v2.models.dtos.quote_evidence import SourceDocumentContext
from backend_v2.models.enums import PromptBlockCategory, VirtualSystemStepID
from backend_v2.models.state import StateProjector, TraceEvent
from backend_v2.models.v2_core import (
    ExecutionRecord,
    FrozenContext,
    StepRule,
    Workflow,
)
from backend_v2.models.v2_core import Step as V2Step
from backend_v2.services.orchestrator.chunking_service import ChunkingService
from backend_v2.services.orchestrator.strategies.base import NodeStrategy, StrategyContext, StrategyDependencies
from backend_v2.services.orchestrator.strategies.llm_execution.context_builder import ContextBuilder
from backend_v2.services.orchestrator.strategies.llm_execution.prompt_factory import PromptFactory
from backend_v2.utils.alias_engine import AliasEngine
from backend_v2.utils.llm_debug_logger import write_debug_prompt_log

__all__ = ["LLMNodeStrategy"]

logger = logging.getLogger(__name__)

_SCHEMA_BLOCK_MATRIX = "MATRIX"
_SCHEMA_BLOCK_TEXT = "TEXT"
_SCHEMA_BLOCK_EXTENSION = "EXTENSION"
_SCHEMA_BLOCK_SYSTEM = "SYSTEM"


class LLMNodeStrategy(NodeStrategy):
    """Executes an AI/LLM Step.

    Manages dynamic schema compilation, instruction aggregation, tracing optimization
    for token context explosion, and routes through either a standard structured prediction
    task or an autonomous MCP Tool Loop depending on step configuration.
    """

    def __init__(
        self,
        deps: StrategyDependencies,
        engine: ExecutionEngine | None = None,
    ) -> None:
        """Initialize the LLM strategy with StrategyDependencies and optional engine.

        Args:
            deps: Immutable container holding repositories, compiler, and pools.
            engine: Optional execution engine instance.
        """
        super().__init__(deps=deps)
        self._engine = engine

    async def execute(
        self,
        step: StepRule,
        projector: StateProjector,
        context: StrategyContext,
        frozen_ctx: FrozenContext | None,
        trace: list[TraceEvent] | None,
        semaphore: asyncio.Semaphore,
        running_event: asyncio.Event | None = None,
        progress_callback: Callable[[int, int], Awaitable[None]] | None = None,
    ) -> list[TraceEvent]:
        """Executes the node's workflow sequence matching system rules.

        Args:
            step: Rule defining the workflow execution block configuration.
            projector: Database representation of current structured historical trace.
            context: Strategy configuration parameters (model, metadata, strictness).
            frozen_ctx: Accumulator state matching prompt caches and MCP traces.
            trace: List of chronological events.
            semaphore: Concurrency limiter for model executions.
            running_event: Cancellation trigger for async processes.
            progress_callback: Optional async callback reporting processed and total item progress.

        Returns:
            List containing the computed outputs packed into structured TraceEvents.

        Raises:
            AppException: Triggered upon infrastructure failure, database corruption, or model invalidity.
            ConfigurationError: Triggered upon incorrect configuration schemas.
        """
        inputs_payload = {d.block_id: d.payload for d in projector.snapshot if d.step_id == "inputs"}
        raw_inputs_payload = {d.block_id: d.payload for d in projector.snapshot if d.step_id == "raw_inputs"}

        if running_event:
            running_event.set()

        inputs_unwrapped = inputs_payload["inputs"] if "inputs" in inputs_payload else inputs_payload

        texts: list[str] = []
        if isinstance(inputs_unwrapped, str):
            texts.append(inputs_unwrapped)
        elif not isinstance(inputs_unwrapped, (int, float, bool)) and inputs_unwrapped is not None:
            try:
                for v in inputs_unwrapped.values():
                    if isinstance(v, str):
                        texts.append(v)
            except AttributeError, TypeError:
                pass

        global_source_text = "\n\n".join(texts)
        current_state: dict[str, Any] = {
            "steps": projector.snapshot,
            "inputs": inputs_unwrapped,
            "raw_inputs": raw_inputs_payload,
        }

        pre_events: list[TraceEvent] = []
        post_events: list[TraceEvent] = []

        blueprint_id = step.task_blueprint
        if not blueprint_id:
            logger.error(
                "Step has no task_blueprint configured.",
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "step_id": step.id},
            )
            raise AppException(
                message=f"Step {step.id} has no task_blueprint configured.",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        step_def_raw = await self.workflow_repo.get_step_by_id(blueprint_id)
        step_def = cast(dict[str, Any], step_def_raw)
        if not step_def:
            logger.error(
                f"Configuration error: Step '{blueprint_id}' not found.",
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "step_id": step.id},
            )
            raise AppException(
                message=f"Configuration error: Step '{blueprint_id}' not found.",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        step_obj = V2Step.model_validate(step_def)
        hook_deps = HookDependencies(
            exec_repo=self.exec_repo,
            workflow_repo=self.workflow_repo,
            comp_repo=self.comp_repo,
            prompt_block_repo=self.prompt_block_repo,
            output_profile_repo=self.output_profile_repo,
            identity_repo=self.identity_repo,
            audit_repo=self.audit_repo,
            system_repo=self.system_repo,
        )

        input_keys: set[str] = set()
        if context.expected_inputs:
            for ei in context.expected_inputs:
                input_keys.add(ei.input_key)

        state_data = current_state

        hook_state = HookState(
            execution_id=context.execution_id,
            workflow_id=context.workflow_id,
            step_id=step.id,
            task_blueprint=blueprint_id,
            metadata=context.metadata,
            global_context_vars=GlobalContextVarsDTO(vars=context.global_context_vars),
            inputs=ExecutionInputsDTO(dynamic_inputs=state_data, raw_inputs=raw_inputs_payload),
        )

        hook_state, pre_events = await self.run_pre_hooks(step_obj, step, hook_state, hook_deps)
        if isinstance(hook_state.inputs, ExecutionInputsDTO):
            state_data = dict(hook_state.inputs.dynamic_inputs)
        elif not isinstance(hook_state.inputs, (str, int, float, bool, list)) and hook_state.inputs is not None:
            try:
                state_data = dict(hook_state.inputs)
            except ValueError, TypeError:
                state_data = {}
        else:
            state_data = {}

        # Removed parallel _apply_alias_chunks_and_audit() that created
        # conflicting doc IDs (doc1..docN) and <source ID="..." label="..."> XML wrappers
        # inside the data. AliasEngine + prompt_compiler.build_xml_context() are the
        # Single Source of Truth for all source aliasing (alias_engine_llm_isolation_mandate).

        if isinstance(context.prompt_blocks, list) and context.prompt_blocks:
            block_map = {b.id: b for b in context.prompt_blocks if b.id}
        else:
            all_prompt_blocks_raw = await self.prompt_block_repo.get_all_prompt_blocks()
            all_prompt_blocks: list[PromptBlock] = []
            for raw in all_prompt_blocks_raw:
                try:
                    all_prompt_blocks.append(PromptBlockAdapter.validate_python(raw, strict=False))
                except Exception as e:
                    logger.error(
                        "[LLMStrategy] Malformed PromptBlock in DB — Fail-Fast.",
                        exc_info=True,
                        extra={"error_code": ErrorCodes.VALIDATION_FAILED.name},
                    )
                    raise AppException(
                        message="Malformed PromptBlock in DB",
                        status_code=500,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    ) from e
            block_map = {b.id: b for b in all_prompt_blocks if b.id}

        target_profile = context.metadata.profile_id
        if not target_profile:
            msg = f"Execution metadata missing mandatory 'profile_id' for workflow {context.workflow_id}."
            raise ConfigurationError(msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})

        role_block = None
        if step_obj.role_block_id:
            role_block = block_map[step_obj.role_block_id] if step_obj.role_block_id in block_map else None
            if not role_block:
                raise ConfigurationError(
                    f"Role Block '{step_obj.role_block_id}' not found.",
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )

        protocol_block = None
        if step_obj.extraction_protocol_block_id:
            protocol_block = (
                block_map[step_obj.extraction_protocol_block_id]
                if step_obj.extraction_protocol_block_id in block_map
                else None
            )
            if not protocol_block:
                raise ConfigurationError(
                    f"Extraction Protocol Block '{step_obj.extraction_protocol_block_id}' not found.",
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )

        execution_persona_block = None
        if step_obj.execution_persona_block_id:
            execution_persona_block = (
                block_map[step_obj.execution_persona_block_id]
                if step_obj.execution_persona_block_id in block_map
                else None
            )
            if not execution_persona_block:
                raise ConfigurationError(
                    f"Execution Persona Block '{step_obj.execution_persona_block_id}' not found.",
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )

        criteria_blocks_models: list[PromptBlock] = []
        for m_id in step_obj.criteria_block_ids:
            b = block_map[m_id] if m_id in block_map else None
            if b:
                criteria_blocks_models.append(b)
            else:
                logger.error(
                    f"Criteria PromptBlock '{m_id}' not found.",
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "step_id": step.id},
                )
                raise AppException(
                    message=f"Criteria PromptBlock '{m_id}' not found.",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

        target_locale = context.metadata.target_locale
        if not target_locale:
            msg = f"Execution metadata missing mandatory 'target_locale' for workflow {context.workflow_id}."
            raise ConfigurationError(msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})
        effective_mcp_tools = step_obj.allowed_mcp_tools

        input_mappings = dict(step.input_mappings)

        workflow_def_raw = await self.workflow_repo.get_workflow(context.workflow_id)
        workflow_def = cast(dict[str, Any], workflow_def_raw)

        output_profile = None
        if target_profile:
            profile_data = await self.output_profile_repo.get_output_profile_by_id(target_profile)
            if not profile_data:
                msg = f"OutputProfile '{target_profile}' not found in database."
                logger.error("[LLMStrategy] %s: %s", ErrorCodes.RESOURCE_NOT_FOUND.name, msg)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
                )

            output_profile = OutputProfile.model_validate(profile_data, strict=False)

        schema_map: dict[str, str] = {}
        blueprint_labels: dict[str, str] = {}
        if workflow_def:
            workflow_obj = Workflow.model_validate(workflow_def)

            for s in workflow_obj.steps:
                is_matrix = False
                blueprint_def_raw = await self.workflow_repo.get_step(s.task_blueprint)
                blueprint_def = cast(dict[str, Any], blueprint_def_raw)
                if blueprint_def:
                    if "name" in blueprint_def:
                        blueprint_labels[s.id] = self.compiler.resolve_i18n(blueprint_def["name"], "en")
                    blueprint_obj = V2Step.model_validate(blueprint_def)
                    all_bp_blocks: list[str] = []
                    if blueprint_obj.role_block_id:
                        all_bp_blocks.append(blueprint_obj.role_block_id)
                    if blueprint_obj.extraction_protocol_block_id:
                        all_bp_blocks.append(blueprint_obj.extraction_protocol_block_id)
                    if blueprint_obj.execution_persona_block_id:
                        all_bp_blocks.append(blueprint_obj.execution_persona_block_id)
                    all_bp_blocks.extend(blueprint_obj.criteria_block_ids)

                    for m_id in all_bp_blocks:
                        b = block_map[m_id] if m_id in block_map else None
                        if b:
                            if b.category_id == PromptBlockCategory.MATRIX:
                                is_matrix = True
                                schema_map[m_id] = _SCHEMA_BLOCK_MATRIX
                            else:
                                schema_map[m_id] = _SCHEMA_BLOCK_TEXT

                            if b.output_extensions:
                                for ext in b.output_extensions:
                                    schema_map[ext] = _SCHEMA_BLOCK_EXTENSION

                schema_map[s.id] = _SCHEMA_BLOCK_MATRIX if is_matrix else _SCHEMA_BLOCK_TEXT

            schema_map["_step_metadata"] = _SCHEMA_BLOCK_SYSTEM
            schema_map["_audit_signature"] = _SCHEMA_BLOCK_SYSTEM
            schema_map["inputs"] = _SCHEMA_BLOCK_TEXT
            schema_map["raw_inputs"] = _SCHEMA_BLOCK_TEXT
            schema_map["matrix_reducer"] = _SCHEMA_BLOCK_SYSTEM

        criteria_blocks = sorted(criteria_blocks_models, key=lambda x: str(x.id or ""))

        llm_context_data, new_input_mappings = ContextBuilder.build(
            input_mappings=input_mappings,
            state_data=state_data,
            output_profile=output_profile,
            schema_map=schema_map,
            criteria_blocks=criteria_blocks,
            blueprint_labels=blueprint_labels,
        )
        input_mappings = new_input_mappings

        has_shuffled_atoms = False
        hydrated_shuffled_atoms = None
        is_matrix_step = any(b.category_id == PromptBlockCategory.MATRIX for b in criteria_blocks_models)
        if is_matrix_step:
            try:
                raw_atoms = state_data["shuffled_atoms"]
            except KeyError as e:
                logger.error(
                    "Matrix step missing 'shuffled_atoms' in state data.",
                    exc_info=True,
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.name},
                )
                raise AppException(
                    message="Matrix step missing 'shuffled_atoms' in state data.",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from e
            from pydantic import TypeAdapter

            from backend_v2.models.dtos.engine import FlattenedAtom

            hydrated_shuffled_atoms = TypeAdapter(list[FlattenedAtom]).validate_python(raw_atoms, strict=False)
            if hydrated_shuffled_atoms:
                has_shuffled_atoms = True

        # Tier 4 Fix: AliasEngine is initialized with clean state.
        # prompt_compiler.build_xml_context() will register source doc aliases via .register().
        alias_engine = AliasEngine()

        prompt_payload = PromptFactory.build(
            compiler=self.compiler,
            role_block=role_block,
            protocol_block=protocol_block,
            execution_persona_block=execution_persona_block,
            criteria_blocks=criteria_blocks,
            target_locale=target_locale,
            effective_mcp_tools=effective_mcp_tools,
            input_mappings=input_mappings,
            llm_context_data=llm_context_data,
            expected_inputs=context.expected_inputs,
            has_shuffled_atoms=has_shuffled_atoms,
            execution_id=context.execution_id,
            alias_engine=alias_engine,
            global_context_vars=(
                hook_state.global_context_vars.vars
                if isinstance(hook_state.global_context_vars, GlobalContextVarsDTO)
                else (
                    dict(hook_state.global_context_vars)
                    if not isinstance(hook_state.global_context_vars, (str, int, float, bool, list))
                    and hook_state.global_context_vars is not None
                    else None
                )
            ),
        )

        user_payload = prompt_payload.user_payload
        base_system_prompt = prompt_payload.base_system_prompt

        if get_settings().environment == "development":
            try:
                write_debug_prompt_log(
                    execution_id=context.execution_id,
                    step_id=step.id,
                    role_block=role_block,
                    protocol_block=protocol_block,
                    criteria_blocks=criteria_blocks,
                    base_system_prompt=base_system_prompt,
                    user_payload=user_payload,
                    expected_schema_name=f"Step_{step.id}_Response",
                )
            except (OSError, ValueError, TypeError) as e:
                logger.warning("[LLMStrategy] Failed to write debug prompt log: %s", e)

        if output_profile:
            exec_params = ["\n<execution_parameters>"]
            if output_profile.tone_instruction:
                tone = output_profile.tone_instruction.resolve(target_locale)
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
                    logger.warning("Failed to serialize matrix_synthesis_groups for prompt injection: %s", e)
            exec_params.append("</execution_parameters>")

            if len(exec_params) > 2:
                base_system_prompt += "\n".join(exec_params)

        chunks_list: list[Any] = []

        if is_matrix_step and "shuffled_atoms" in state_data:
            shuffled_atoms = state_data["shuffled_atoms"]

            if not isinstance(shuffled_atoms, list) or len(shuffled_atoms) == 0:
                msg = f"Strict Fail-Fast Enforced: 'shuffled_atoms' is empty or not a list for step '{step.id}'."
                logger.error("[LLMStrategy] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

            req = ChunkingRequest[dict[str, Any]](
                parent_id=context.workflow_id,
                items=shuffled_atoms,
                max_chunk_size=get_settings().schema_max_evaluations,
            )
            chunks_list = ChunkingService.chunk_payload(req)
        else:
            chunks_list = [None]

        # Use the generated aliases directly instead of resolving real IDs
        source_doc_ids = alias_engine.source_document_aliases if alias_engine.source_document_aliases else ["N/A"]

        # Fetch execution record to build SourceDocumentContext for validation context
        execution_record_raw = None
        try:
            res = self.exec_repo.get_execution(context.execution_id)
            if inspect.isawaitable(res):
                execution_record_raw = await res
            else:
                execution_record_raw = res
        except Exception as e:
            logger.error(
                "[LLMStrategy] %s: Failed to fetch execution record '%s'",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                context.execution_id,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.name, "execution_id": context.execution_id},
            )
            raise AppException(
                message=f"Execution record '{context.execution_id}' not found.",
                status_code=404,
                details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            ) from e

        if execution_record_raw:
            try:
                if isinstance(execution_record_raw, ExecutionRecord):
                    exec_obj = execution_record_raw
                else:
                    exec_obj = ExecutionRecord.model_validate(execution_record_raw, strict=False)
                manifest = exec_obj.source_identity_manifest or {}

                source_docs = []
                inputs_dict = inputs_payload["inputs"] if "inputs" in inputs_payload else inputs_payload
                if not isinstance(inputs_dict, (str, int, float, bool, list)) and inputs_dict is not None:
                    try:
                        for k, text_content in inputs_dict.items():
                            if isinstance(text_content, str):
                                display_name = str(manifest[k]) if k in manifest else k
                                doc_ctx = SourceDocumentContext(
                                    opaque_id=k, text_content=text_content, display_name=display_name
                                )
                                source_docs.append(doc_ctx.model_dump(mode="json"))
                    except AttributeError, TypeError:
                        pass
            except Exception as e:
                logger.error(
                    "[LLMStrategy] %s: Failed to construct source documents context from execution record '%s'",
                    ErrorCodes.VALIDATION_FAILED.name,
                    context.execution_id,
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "execution_id": context.execution_id},
                )
                raise AppException(
                    message="Failed to parse execution record for source documents context.",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                ) from e

        dynamic_schema: Any | None = None
        if frozen_ctx:
            allowed_dynamic_keys = [e.input_key for e in context.expected_inputs] if context.expected_inputs else []
            allowed_dynamic_keys.extend(input_mappings.keys())
            allowed_dynamic_keys = list(set(allowed_dynamic_keys))

            # Extensibility for dynamic MCP providers
            mcp_prefixes = ["call_", "mcp_", "search_"]
            for tool_name in step_obj.allowed_mcp_tools:
                mcp_prefixes.append(f"{tool_name}_")
            allowed_mcp_prefixes = list(set(mcp_prefixes))

            global_schema = self.compiler.build_dynamic_schema(
                schema_name=f"Step_{step.id}_Response",
                criteria=criteria_blocks,
                has_shuffled_atoms=has_shuffled_atoms,
                target_locale=target_locale,
                strictness_level=context.strictness_level,
                source_document_ids=source_doc_ids,
                allowed_dynamic_keys=allowed_dynamic_keys,
                allowed_mcp_prefixes=allowed_mcp_prefixes,
            )
            dynamic_schema = global_schema

        strategy_name = context.model_strategy
        if not strategy_name:
            logger.error(
                "Step has no model_strategy defined. Zero fallbacks allowed.",
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "step_id": step.id},
            )
            raise AppException(
                message=f"Step {step.id} has no model_strategy defined (Fail-Fast: No fallbacks allowed).",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )
        bound_client = await LLMClient.from_strategy(strategy_name, self.system_repo, pipeline_name="chunk_worker")

        MAX_RETRIES = get_settings().llm_max_retries
        retry_count = 0
        final_dict: dict[str, Any] = {}
        usage_agg = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
        latency_ms = 0

        while retry_count <= MAX_RETRIES:
            telemetry_start_time = time.time()
            context_char_length = len(user_payload)
            logger.info(
                "Epic 27 Telemetry: Compiling map-reduce for step '%s'. "
                "Context Bounds: %d chars, Chunk count: %d. (Attempt %d)",
                step.id,
                context_char_length,
                len(chunks_list),
                retry_count + 1,
            )

            if self._engine is None:
                msg = "LLMNodeStrategy has no ExecutionEngine configured."
                logger.error("[LLMStrategy] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )

            matrix_block = next((b for b in criteria_blocks if isinstance(b, MatrixPromptBlock)), None)
            matrix_block_id = matrix_block.id if matrix_block else None

            matrix_context = None
            if matrix_block:
                matrix_context = MatrixEvaluationContext(
                    theory_grounding=matrix_block.theory_grounding,
                    matrix_objective=matrix_block.ai_description,
                    allow_contextual_override=matrix_block.allow_contextual_override,
                )

            is_synthesis_step = context.model_strategy == "synthesis"
            dynamic_schema = None

            if is_synthesis_step:
                target_locale = context.metadata.target_locale

                gvars = (
                    hook_state.global_context_vars.vars
                    if isinstance(hook_state.global_context_vars, GlobalContextVarsDTO)
                    else (
                        dict(hook_state.global_context_vars)
                        if not isinstance(hook_state.global_context_vars, (str, int, float, bool, list))
                        and hook_state.global_context_vars is not None
                        else {}
                    )
                )
                blackboard = gvars["__GLOBAL_ATOM_BLACKBOARD__"] if "__GLOBAL_ATOM_BLACKBOARD__" in gvars else {}
                atoms_by_input = (
                    blackboard["atoms_by_input"]
                    if not isinstance(blackboard, (str, int, float, bool, list))
                    and blackboard is not None
                    and "atoms_by_input" in blackboard
                    else {}
                )
                doc_aliases = list(atoms_by_input.keys()) if atoms_by_input else ["N/A"]

                dag_results = {}
                raw_inputs_dict = (
                    hook_state.inputs.raw_inputs if isinstance(hook_state.inputs, ExecutionInputsDTO) else {}
                )
                dynamic_inputs_dict = (
                    hook_state.inputs.dynamic_inputs
                    if isinstance(hook_state.inputs, ExecutionInputsDTO)
                    else (
                        dict(hook_state.inputs)
                        if not isinstance(hook_state.inputs, (str, int, float, bool, list))
                        and hook_state.inputs is not None
                        else {}
                    )
                )
                combined_inputs = list(raw_inputs_dict.values()) + list(dynamic_inputs_dict.values())
                for step_res in combined_inputs:
                    try:
                        if "results" in step_res:
                            for ev in step_res["results"]:
                                if not isinstance(ev, (str, int, float, bool)) and ev is not None:
                                    a_id = (
                                        ev["tda_id"] if "tda_id" in ev else (ev["atom_id"] if "atom_id" in ev else None)
                                    )
                                    if a_id:
                                        dag_results[a_id] = ev
                    except TypeError, KeyError:
                        pass

                dynamic_schema = self.compiler.build_dynamic_schema(
                    schema_name=f"Step_{step.id}_Response",
                    criteria=criteria_blocks,
                    has_shuffled_atoms=False,
                    target_locale=target_locale,
                    strictness_level=context.strictness_level,
                    source_document_ids=doc_aliases,
                    expected_sdui_type=step.expected_sdui_type or "grid",
                    dag_results=dag_results,
                )

                static_instructions = self.compiler.compile_static_instructions(criteria_blocks, target_locale)
                static_msg = {"role": "system", "content": static_instructions}

                engine_request = EngineExecutionRequest(
                    bound_client=bound_client,
                    compiled_schema=dynamic_schema,
                    hydrated_messages=[static_msg],
                    system_prompt="",
                    step=step,
                    context=context,
                    global_source_text=global_source_text,
                    target_locale=target_locale,
                    semaphore=semaphore,
                    running_event=running_event,
                    progress_callback=progress_callback,
                    trace_callback=None,
                    prompt_compiler=self.compiler,
                    shuffled_atoms=hydrated_shuffled_atoms,
                    matrix_block_id=matrix_block_id,
                    matrix_context=matrix_context,
                )
            elif matrix_block is None:
                target_locale = context.metadata.target_locale
                gvars = (
                    hook_state.global_context_vars.vars
                    if isinstance(hook_state.global_context_vars, GlobalContextVarsDTO)
                    else (
                        dict(hook_state.global_context_vars)
                        if not isinstance(hook_state.global_context_vars, (str, int, float, bool, list))
                        and hook_state.global_context_vars is not None
                        else {}
                    )
                )
                blackboard = gvars["__GLOBAL_ATOM_BLACKBOARD__"] if "__GLOBAL_ATOM_BLACKBOARD__" in gvars else {}
                atoms_by_input = (
                    blackboard["atoms_by_input"]
                    if not isinstance(blackboard, (str, int, float, bool, list))
                    and blackboard is not None
                    and "atoms_by_input" in blackboard
                    else {}
                )
                doc_aliases = list(atoms_by_input.keys()) if atoms_by_input else ["N/A"]

                dag_results = {}
                raw_inputs_dict = (
                    hook_state.inputs.raw_inputs if isinstance(hook_state.inputs, ExecutionInputsDTO) else {}
                )
                dynamic_inputs_dict = (
                    hook_state.inputs.dynamic_inputs
                    if isinstance(hook_state.inputs, ExecutionInputsDTO)
                    else (
                        dict(hook_state.inputs)
                        if not isinstance(hook_state.inputs, (str, int, float, bool, list))
                        and hook_state.inputs is not None
                        else {}
                    )
                )
                combined_inputs = list(raw_inputs_dict.values()) + list(dynamic_inputs_dict.values())
                for step_res in combined_inputs:
                    try:
                        if "results" in step_res:
                            for ev in step_res["results"]:
                                if not isinstance(ev, (str, int, float, bool)) and ev is not None:
                                    a_id = (
                                        ev["tda_id"] if "tda_id" in ev else (ev["atom_id"] if "atom_id" in ev else None)
                                    )
                                    if a_id:
                                        dag_results[a_id] = ev
                    except TypeError, KeyError:
                        pass

                dynamic_schema = self.compiler.build_dynamic_schema(
                    schema_name=f"Step_{step.id}_Response",
                    criteria=criteria_blocks,
                    has_shuffled_atoms=False,
                    target_locale=target_locale,
                    strictness_level=context.strictness_level,
                    source_document_ids=doc_aliases,
                    expected_sdui_type=step.expected_sdui_type or "grid",
                    dag_results=dag_results,
                )

                static_instructions = self.compiler.compile_static_instructions(criteria_blocks, target_locale)
                hydrated_messages = [
                    {"role": "system", "content": static_instructions},
                    {"role": "user", "content": user_payload},
                ]

                engine_request = EngineExecutionRequest(
                    bound_client=bound_client,
                    compiled_schema=dynamic_schema,
                    hydrated_messages=hydrated_messages,
                    system_prompt=user_payload,
                    step=step,
                    context=context,
                    global_source_text=global_source_text,
                    target_locale=target_locale,
                    semaphore=semaphore,
                    running_event=running_event,
                    progress_callback=progress_callback,
                    trace_callback=None,
                    prompt_compiler=self.compiler,
                    shuffled_atoms=hydrated_shuffled_atoms,
                    matrix_block_id=matrix_block_id,
                    matrix_context=matrix_context,
                )
            else:
                engine_request = EngineExecutionRequest(
                    bound_client=bound_client,
                    compiled_schema=None,
                    hydrated_messages=None,
                    system_prompt=user_payload,
                    step=step,
                    context=context,
                    global_source_text=global_source_text,
                    target_locale=target_locale,
                    semaphore=semaphore,
                    running_event=running_event,
                    progress_callback=progress_callback,
                    trace_callback=None,
                    prompt_compiler=self.compiler,
                    shuffled_atoms=hydrated_shuffled_atoms,
                    matrix_block_id=matrix_block_id,
                    matrix_context=matrix_context,
                )

            engine_result = await self._engine.execute(engine_request)

            if engine_result.synthesis_output is not None:
                if isinstance(engine_result.synthesis_output, BaseModel):
                    final_dict = engine_result.synthesis_output.model_dump()
                elif isinstance(engine_result.synthesis_output, (str, int, float, bool, list)):
                    final_dict = {"output": engine_result.synthesis_output}
                else:
                    try:
                        final_dict = dict(engine_result.synthesis_output)
                    except ValueError, TypeError:
                        final_dict = {"output": engine_result.synthesis_output}
            else:
                final_dict = {
                    "results": [r.model_dump() for r in engine_result.results],
                    "hydrated_references": {k: v.model_dump() for k, v in engine_result.hydrated_references.items()},
                }

            latency_ms = int((time.time() - telemetry_start_time) * 1000)
            if engine_result.usage is not None:
                usage_agg = engine_result.usage
            else:
                usage_agg = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
            all_prompt_contexts: list[dict[str, Any]] = []
            post_gvars = (
                hook_state.global_context_vars.vars
                if isinstance(hook_state.global_context_vars, GlobalContextVarsDTO)
                else (
                    dict(hook_state.global_context_vars)
                    if not isinstance(hook_state.global_context_vars, (str, int, float, bool, list))
                    and hook_state.global_context_vars is not None
                    else {}
                )
            )
            safe_context: dict[str, Any] = {**post_gvars, "steps": projector.snapshot}

            post_hook_state = hook_state.model_copy(
                update={
                    "global_context_vars": GlobalContextVarsDTO(vars=safe_context),
                    "inputs": ExecutionInputsDTO(
                        dynamic_inputs=final_dict,
                        raw_inputs=final_dict,
                        target_locale=hook_state.inputs.target_locale
                        if isinstance(hook_state.inputs, ExecutionInputsDTO)
                        else None,
                        user_role=hook_state.inputs.user_role
                        if isinstance(hook_state.inputs, ExecutionInputsDTO)
                        else None,
                    ),
                }
            )

            post_hook_state, post_events = await self.run_post_hooks(
                step_obj=step_obj,
                step=step,
                hook_state=post_hook_state,
                hook_deps=hook_deps,
            )
            if isinstance(post_hook_state.inputs, ExecutionInputsDTO):
                final_dict = dict(post_hook_state.inputs.dynamic_inputs)
            elif (
                not isinstance(post_hook_state.inputs, (str, int, float, bool, list))
                and post_hook_state.inputs is not None
            ):
                try:
                    final_dict = dict(post_hook_state.inputs)
                except ValueError, TypeError:
                    final_dict = {}
            else:
                final_dict = {}

            if "llm_anomaly_retry_requested" in final_dict and final_dict["llm_anomaly_retry_requested"]:
                retry_count += 1
                if retry_count > MAX_RETRIES:
                    logger.warning(
                        "[LLMStrategy] Max retries (%d) exceeded for step '%s'. Swallowing anomaly.",
                        MAX_RETRIES,
                        step.id,
                    )
                    final_dict["anomaly_unresolved"] = True
                    final_dict.pop("llm_anomaly_retry_requested", None)
                    break
                else:
                    logger.info(
                        "[LLMStrategy] LLM Anomaly Retry triggered for step '%s'. Attempt %d/%d.",
                        step.id,
                        retry_count,
                        MAX_RETRIES,
                    )

                    exec_record_raw = await self.exec_repo.get_execution(context.execution_id)
                    exec_record = cast(Any, exec_record_raw)
                    if exec_record and step.id in exec_record.step_states:
                        new_state = exec_record.step_states[step.id].model_copy(
                            update={"status": "processing", "message_code": "event_llm_anomaly_retry"}
                        )
                        new_states = {**exec_record.step_states, step.id: new_state}
                        new_states_raw = {k: v.model_dump(mode="json") for k, v in new_states.items()}
                        await self.exec_repo.update_execution(context.execution_id, {"step_states": new_states_raw})
                    continue

            break

        for key in ["profiler_metrics", VirtualSystemStepID.STEP_METADATA.value, "_audit_signature"]:
            if key in state_data:
                final_dict[key] = state_data[key]

        meta = final_dict.setdefault("_step_metadata", {})
        meta["task_blueprint"] = blueprint_id
        meta["model_strategy"] = strategy_name
        if usage_agg.total_tokens > 0 or usage_agg.cost_usd > 0.0:
            if "token_usage" not in meta:
                meta["token_usage"] = usage_agg.model_dump()

        metadata: dict[str, Any] = {
            "latency_ms": latency_ms,
            "chunk_size": len(chunks_list),
            "context_char_length": context_char_length,
            "prompt_contexts": all_prompt_contexts,
        }
        if dynamic_schema is not None:
            metadata["generated_schema"] = dynamic_schema.model_json_schema()

        return (
            pre_events
            + post_events
            + [
                TraceEvent(
                    step_name=step.id,
                    event_type="output",
                    content=final_dict,
                    metadata=metadata,
                )
            ]
        )

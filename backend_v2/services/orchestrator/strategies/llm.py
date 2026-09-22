"""LLM Node Strategy for DAG-based workflow execution.

Orchestrates AI/LLM step execution including dynamic schema compilation,
chunked map-reduce evaluation, DLQ graceful degradation, and anomaly retry logic.
"""

from __future__ import annotations

import asyncio
import inspect
import json
import logging
import time
from collections.abc import Awaitable, Callable, Mapping
from typing import TYPE_CHECKING, Any, cast

from pydantic import BaseModel, JsonValue

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
from backend_v2.models.domain.blackboard import GlobalAtomBlackboard
from backend_v2.models.domain.execution import ExecutionRecord, FrozenContext
from backend_v2.models.domain.inputs import DomainInputValue
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import (
    MatrixPromptBlock,
    PromptBlock,
    PromptBlockAdapter,
)
from backend_v2.models.domain.step import Step as V2Step
from backend_v2.models.domain.step import StepRule
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.atom_result import AtomResultDTO
from backend_v2.models.dtos.engine import EngineExecutionRequest, MatrixEvaluationContext
from backend_v2.models.dtos.hook_delta import StepContextMetadataDTO
from backend_v2.models.dtos.prompt import PromptMappingDTO
from backend_v2.models.dtos.quote_evidence import SourceDocumentContext
from backend_v2.models.dtos.step_output import StepOutputDTO
from backend_v2.models.dtos.trace import ExecutionUpdateDTO
from backend_v2.models.enums import ExecutionStatus, PromptBlockCategory, VirtualSystemStepID
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.llm import LLMMessageDTO
from backend_v2.models.state import StateProjector, TraceEvent
from backend_v2.services.orchestrator.chunking_service import ChunkingService
from backend_v2.services.orchestrator.engines.synthesis_engine import SynthesisEngine
from backend_v2.services.orchestrator.strategies.base import NodeStrategy, StrategyContext, StrategyDependencies
from backend_v2.services.orchestrator.strategies.llm_execution.context_builder import ContextBuilder
from backend_v2.services.orchestrator.strategies.llm_execution.prompt_factory import PromptFactory
from backend_v2.services.orchestrator.strategies.llm_execution.source_document_packer import SourceDocumentPacker
from backend_v2.utils.alias_engine import AliasEngine
from backend_v2.utils.llm_debug_logger import write_debug_prompt_log

__all__ = ["LLMNodeStrategy"]

logger = logging.getLogger(__name__)

_SCHEMA_BLOCK_MATRIX = "MATRIX"
_SCHEMA_BLOCK_TEXT = "TEXT"
_SCHEMA_BLOCK_EXTENSION = "EXTENSION"
_SCHEMA_BLOCK_SYSTEM = "SYSTEM"

type NodeStatePayload = DomainInputValue | ExecutionMetadata | Mapping[str, DomainInputValue] | list[Any] | JsonValue


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

    @staticmethod
    def _dlq_handle_debug_log_error(exc: Exception) -> None:
        """Handle debug prompt logging failures in development gracefully."""
        logger.warning("[LLMStrategy] Failed to write debug prompt log: %s", exc)

    def _extract_step_context_metadata(
        self,
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
            gvars = hook_state.global_context_vars.model_dump(exclude_none=True)
        elif (
            not isinstance(hook_state.global_context_vars, (str, int, float, bool, list))
            and hook_state.global_context_vars is not None
        ):
            gvars = dict(hook_state.global_context_vars)

        blackboard: Any = None
        if context is not None:
            if context.context_variables.global_atom_blackboard:
                blackboard = context.context_variables.global_atom_blackboard
            elif "__GLOBAL_ATOM_BLACKBOARD__" in context.context_variables:
                blackboard = context.context_variables["__GLOBAL_ATOM_BLACKBOARD__"]

        if blackboard is None:
            if (
                isinstance(hook_state.global_context_vars, Mapping)
                and "__GLOBAL_ATOM_BLACKBOARD__" in hook_state.global_context_vars
            ):
                blackboard = hook_state.global_context_vars["__GLOBAL_ATOM_BLACKBOARD__"]
            elif "__GLOBAL_ATOM_BLACKBOARD__" in gvars:
                blackboard = gvars["__GLOBAL_ATOM_BLACKBOARD__"]

        atoms_by_input = {}
        if blackboard is not None:
            if isinstance(blackboard, GlobalAtomBlackboard):
                atoms_by_input = blackboard.atoms_by_input
            elif isinstance(blackboard, Mapping) and "atoms_by_input" in blackboard:
                atoms_by_input = dict(blackboard["atoms_by_input"])

        doc_aliases: list[str] = ["N/A"]
        if atoms_by_input:
            doc_aliases = list(atoms_by_input.keys())

        raw_inputs_dict: Mapping[str, object] = {}
        dynamic_inputs_dict: Mapping[str, object] = {}
        if isinstance(hook_state.inputs, ExecutionInputsDTO):
            raw_inputs_dict = hook_state.inputs.raw_inputs
            dynamic_inputs_dict = hook_state.inputs.dynamic_inputs
        elif isinstance(hook_state.inputs, Mapping):
            dynamic_inputs_dict = dict(hook_state.inputs)

        dag_results: dict[str, AtomResultDTO] = {}
        combined_inputs: list[Any] = list(raw_inputs_dict.values()) + list(dynamic_inputs_dict.values())
        for step_res in combined_inputs:
            if isinstance(step_res, list):
                for item in step_res:
                    if isinstance(item, AtomResultDTO):
                        dag_results[item.tda_id] = item
                    elif isinstance(item, Mapping):
                        a_id = item["tda_id"] if "tda_id" in item else (item["atom_id"] if "atom_id" in item else None)
                        if a_id:
                            if isinstance(item, AtomResultDTO):
                                dag_results[str(a_id)] = item
                            else:
                                item_dict = dict(item)
                                item_dict.pop("atom_id", None)
                                if "status" not in item_dict:
                                    item_dict["status"] = ExecutionStatus.PASSED
                                if "source_quote" not in item_dict and (
                                    "contextual_override" not in item_dict or not item_dict["contextual_override"]
                                ):
                                    item_dict["contextual_override"] = True
                                if "evaluation_reasoning" not in item_dict:
                                    item_dict["evaluation_reasoning"] = "Extracted"
                                if "tda_id" not in item_dict:
                                    item_dict["tda_id"] = str(a_id)
                                dag_results[str(a_id)] = AtomResultDTO.model_validate(item_dict, strict=False)
            elif isinstance(step_res, AtomResultDTO):
                dag_results[step_res.tda_id] = step_res
            elif isinstance(step_res, Mapping) and "results" in step_res and isinstance(step_res["results"], list):
                for ev in step_res["results"]:
                    if isinstance(ev, AtomResultDTO):
                        dag_results[ev.tda_id] = ev
                    elif isinstance(ev, Mapping):
                        extracted_a_id = (
                            ev["tda_id"] if "tda_id" in ev else (ev["atom_id"] if "atom_id" in ev else None)
                        )
                        if extracted_a_id:
                            ev_dict = dict(ev)
                            ev_dict.pop("atom_id", None)
                            if "status" not in ev_dict:
                                ev_dict["status"] = ExecutionStatus.PASSED
                            if "source_quote" not in ev_dict and (
                                "contextual_override" not in ev_dict or not ev_dict["contextual_override"]
                            ):
                                ev_dict["contextual_override"] = True
                            if "evaluation_reasoning" not in ev_dict:
                                ev_dict["evaluation_reasoning"] = "Extracted"
                            if "tda_id" not in ev_dict:
                                ev_dict["tda_id"] = str(extracted_a_id)
                            dag_results[str(extracted_a_id)] = AtomResultDTO.model_validate(ev_dict, strict=False)

        return StepContextMetadataDTO(
            gvars=gvars,
            doc_aliases=doc_aliases,
            dag_results=dag_results,
        )

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

        if running_event:
            running_event.set()

        inputs_unwrapped: object = inputs_payload
        if "inputs" in inputs_payload:
            inputs_unwrapped = inputs_payload["inputs"]

        targets = SourceDocumentPacker.resolve_context_targets(step.input_mappings)
        global_source_text = SourceDocumentPacker.pack(
            inputs_unwrapped,
            context.expected_inputs,
            targets=targets,
            step_outputs=projector.snapshot,
        )
        snapshot_steps: list[StepOutputDTO] = []
        if isinstance(projector.snapshot, list):
            snapshot_steps = list(projector.snapshot)
        current_state: dict[str, DomainInputValue] = {
            "steps": snapshot_steps,
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
        if not step_def_raw:
            logger.error(
                f"Configuration error: Step '{blueprint_id}' not found.",
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "step_id": step.id},
            )
            raise AppException(
                message=f"Configuration error: Step '{blueprint_id}' not found.",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        step_obj = V2Step.model_validate(step_def_raw)
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

        if isinstance(context.global_context_vars, GlobalContextVarsDTO):
            initial_gvars = context.global_context_vars
        elif isinstance(context.global_context_vars, Mapping) and context.global_context_vars:
            known_fields = GlobalContextVarsDTO.model_fields.keys()
            filtered_vars = {k: v for k, v in context.global_context_vars.items() if k in known_fields}
            initial_gvars = GlobalContextVarsDTO.model_validate(filtered_vars)
        else:
            initial_gvars = GlobalContextVarsDTO()

        safe_raw_inputs = {}
        if isinstance(inputs_unwrapped, Mapping):
            safe_raw_inputs = dict(inputs_unwrapped)
        hook_state = HookState(
            execution_id=context.execution_id,
            workflow_id=context.workflow_id,
            step_id=step.id,
            task_blueprint=blueprint_id,
            metadata=context.metadata,
            global_context_vars=initial_gvars,
            inputs=ExecutionInputsDTO(dynamic_inputs=current_state, raw_inputs=safe_raw_inputs),
        )

        hook_state, pre_events = await self.run_pre_hooks(step_obj, step, hook_state, hook_deps)
        state_data: dict[str, NodeStatePayload]
        if isinstance(hook_state.inputs, ExecutionInputsDTO):
            state_data = dict(hook_state.inputs.dynamic_inputs)
            if "inputs" not in state_data and hook_state.inputs.raw_inputs:
                state_data["inputs"] = hook_state.inputs.raw_inputs
        elif isinstance(hook_state.inputs, Mapping):
            state_data = dict(hook_state.inputs)
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

        target_profile = context.output_profile_id
        if not target_profile:
            msg = f"ExecutionContext missing mandatory 'output_profile_id' for workflow {context.workflow_id}."
            raise ConfigurationError(msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})

        role_block = None
        if step_obj.role_block_id:
            if step_obj.role_block_id in block_map:
                role_block = block_map[step_obj.role_block_id]
            else:
                raise ConfigurationError(
                    f"Role Block '{step_obj.role_block_id}' not found.",
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )

        protocol_block = None
        if step_obj.extraction_protocol_block_id:
            if step_obj.extraction_protocol_block_id in block_map:
                protocol_block = block_map[step_obj.extraction_protocol_block_id]
            else:
                raise ConfigurationError(
                    f"Extraction Protocol Block '{step_obj.extraction_protocol_block_id}' not found.",
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )

        execution_persona_block = None
        if step_obj.execution_persona_block_id:
            if step_obj.execution_persona_block_id in block_map:
                execution_persona_block = block_map[step_obj.execution_persona_block_id]
            else:
                raise ConfigurationError(
                    f"Execution Persona Block '{step_obj.execution_persona_block_id}' not found.",
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )

        criteria_blocks_models: list[PromptBlock] = []
        for m_id in step_obj.criteria_block_ids:
            if m_id in block_map:
                criteria_blocks_models.append(block_map[m_id])
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

        target_locale = context.target_locale
        if not target_locale:
            msg = f"ExecutionContext missing mandatory 'target_locale' for workflow {context.workflow_id}."
            raise ConfigurationError(msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})
        effective_mcp_tools = step_obj.allowed_mcp_tools

        input_mappings = PromptMappingDTO(mappings=dict(step.input_mappings))

        workflow_def_raw = await self.workflow_repo.get_workflow(context.workflow_id)

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
        if workflow_def_raw:
            workflow_obj = Workflow.model_validate(workflow_def_raw)

            for s in workflow_obj.steps:
                is_matrix = False
                blueprint_def_raw = await self.workflow_repo.get_step(s.task_blueprint)
                if blueprint_def_raw:
                    if isinstance(blueprint_def_raw, Mapping) and "name" in blueprint_def_raw:
                        blueprint_labels[s.id] = self.compiler.resolve_i18n(blueprint_def_raw["name"], "en")
                    blueprint_obj = V2Step.model_validate(blueprint_def_raw)
                    all_bp_blocks: list[str] = []
                    if blueprint_obj.role_block_id:
                        all_bp_blocks.append(blueprint_obj.role_block_id)
                    if blueprint_obj.extraction_protocol_block_id:
                        all_bp_blocks.append(blueprint_obj.extraction_protocol_block_id)
                    if blueprint_obj.execution_persona_block_id:
                        all_bp_blocks.append(blueprint_obj.execution_persona_block_id)
                    all_bp_blocks.extend(blueprint_obj.criteria_block_ids)

                    for m_id in all_bp_blocks:
                        if m_id in block_map:
                            b = block_map[m_id]
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

        criteria_blocks = sorted(criteria_blocks_models, key=lambda x: str(x.id))

        if "metadata" not in state_data and hook_state.metadata:
            state_data["metadata"] = hook_state.metadata
        if (
            "raw_inputs" not in state_data
            and isinstance(hook_state.inputs, ExecutionInputsDTO)
            and hook_state.inputs.raw_inputs
        ):
            state_data["raw_inputs"] = hook_state.inputs.raw_inputs

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

        prompt_gvars: GlobalContextVarsDTO | None = None
        if isinstance(hook_state.global_context_vars, GlobalContextVarsDTO):
            prompt_gvars = hook_state.global_context_vars
        elif isinstance(hook_state.global_context_vars, Mapping):
            prompt_gvars = GlobalContextVarsDTO.model_validate(dict(hook_state.global_context_vars))

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
            global_context_vars=prompt_gvars,
        )

        user_payload = prompt_payload.user_payload
        base_system_prompt = prompt_payload.base_system_prompt

        if get_settings().environment == "development":
            try:
                await write_debug_prompt_log(
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
                self._dlq_handle_debug_log_error(e)

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
                    logger.error("Failed to serialize matrix_synthesis_groups for prompt injection: %s", e)
                    raise AppException(
                        ErrorCodes.VALIDATION_FAILED,
                        details={"reason": f"Failed to serialize matrix_synthesis_groups: {e}"},
                    ) from e
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

            req = ChunkingRequest(
                parent_id=context.workflow_id,
                items=shuffled_atoms,
                max_chunk_size=get_settings().schema_max_evaluations,
            )
            chunks_list = ChunkingService.chunk_payload(req)
        else:
            chunks_list = [None]

        # Use the generated aliases directly instead of resolving real IDs
        source_doc_ids: list[str] = ["N/A"]
        if alias_engine.source_document_aliases:
            source_doc_ids = alias_engine.source_document_aliases

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
                manifest = exec_obj.source_identity_manifest if exec_obj.source_identity_manifest else {}

                source_docs = []
                inputs_dict: object = inputs_payload
                if "inputs" in inputs_payload:
                    inputs_dict = inputs_payload["inputs"]
                if isinstance(inputs_dict, Mapping):
                    for k, text_content in inputs_dict.items():
                        if isinstance(text_content, str):
                            display_name = k
                            if k in manifest:
                                display_name = str(manifest[k])
                            doc_ctx = SourceDocumentContext(
                                opaque_id=k, text_content=text_content, display_name=display_name
                            )
                            source_docs.append(doc_ctx.model_dump(mode="json"))
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
            allowed_dynamic_keys: list[str] = []
            if context.expected_inputs:
                allowed_dynamic_keys = [e.input_key for e in context.expected_inputs]
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

        cognitive_tier = context.cognitive_tier
        if not cognitive_tier:
            logger.error(
                "Step has no cognitive_tier defined. Zero fallbacks allowed.",
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "step_id": step.id},
            )
            raise AppException(
                message=f"Step {step.id} has no cognitive_tier defined (Fail-Fast: No fallbacks allowed).",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )
        bound_client = await LLMClient.from_tier(
            cognitive_tier,
            self.system_repo,
            provider=context.metadata.provider_override,
            registry_id=context.model_registry_id,
            pipeline_name="chunk_worker",
        )

        MAX_RETRIES = get_settings().llm_max_retries
        retry_count = 0
        final_dict = {}
        usage_agg = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
        latency_ms = 0

        while retry_count <= MAX_RETRIES:
            telemetry_start_time = time.time()
            context_char_length = len(user_payload)
            logger.info(
                "Map-reduce execution telemetry for step '%s'. Context Bounds: %d chars, Chunk count: %d. (Attempt %d)",
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
            matrix_block_id: str | None = None
            if matrix_block is not None:
                matrix_block_id = matrix_block.id

            matrix_context = None
            if matrix_block:
                matrix_context = MatrixEvaluationContext(
                    theory_grounding=matrix_block.theory_grounding,
                    matrix_objective=matrix_block.ai_description,
                    allow_contextual_override=matrix_block.allow_contextual_override,
                )

            is_synthesis_step = isinstance(self._engine, SynthesisEngine)
            dynamic_schema = None

            if is_synthesis_step:
                target_locale = context.target_locale
                step_meta = self._extract_step_context_metadata(hook_state, context)
                doc_aliases = step_meta.doc_aliases
                dag_results = step_meta.dag_results
                expected_sdui_type = "grid"
                if step.expected_sdui_type is not None and step.expected_sdui_type.strip():
                    expected_sdui_type = step.expected_sdui_type

                dynamic_schema = self.compiler.build_dynamic_schema(
                    schema_name=f"Step_{step.id}_Response",
                    criteria=criteria_blocks,
                    has_shuffled_atoms=False,
                    target_locale=target_locale,
                    strictness_level=context.strictness_level,
                    source_document_ids=doc_aliases,
                    expected_sdui_type=expected_sdui_type,
                    dag_results=dag_results,
                )

                static_instructions = self.compiler.compile_static_instructions(criteria_blocks, target_locale)
                static_msg = LLMMessageDTO(role="system", content=static_instructions)

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
                target_locale = context.target_locale
                step_meta = self._extract_step_context_metadata(hook_state, context)
                doc_aliases = step_meta.doc_aliases
                dag_results = step_meta.dag_results
                expected_sdui_type = "grid"
                if step.expected_sdui_type is not None and step.expected_sdui_type.strip():
                    expected_sdui_type = step.expected_sdui_type

                dynamic_schema = self.compiler.build_dynamic_schema(
                    schema_name=f"Step_{step.id}_Response",
                    criteria=criteria_blocks,
                    has_shuffled_atoms=False,
                    target_locale=target_locale,
                    strictness_level=context.strictness_level,
                    source_document_ids=doc_aliases,
                    expected_sdui_type=expected_sdui_type,
                    dag_results=dag_results,
                )

                static_instructions = self.compiler.compile_static_instructions(criteria_blocks, target_locale)
                hydrated_messages = [
                    LLMMessageDTO(role="system", content=static_instructions),
                    LLMMessageDTO(role="user", content=user_payload),
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
                    final_dict = engine_result.synthesis_output.model_dump(exclude_none=True)
                elif isinstance(engine_result.synthesis_output, Mapping):
                    final_dict = {k: v for k, v in engine_result.synthesis_output.items() if v is not None}
                else:
                    final_dict = {"output": engine_result.synthesis_output}
            else:
                final_dict = {
                    "results": engine_result.results,
                    "hydrated_references": engine_result.hydrated_references,
                }

            latency_ms = int((time.time() - telemetry_start_time) * 1000)
            if engine_result.usage is not None:
                usage_agg = engine_result.usage
            else:
                usage_agg = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
            all_prompt_contexts: list[JsonValue] = []
            post_target_locale: str | None = None
            post_user_role: Any | None = None
            if isinstance(hook_state.inputs, ExecutionInputsDTO):
                post_target_locale = hook_state.inputs.target_locale
                post_user_role = hook_state.inputs.user_role

            post_hook_state = hook_state.model_copy(
                update={
                    "global_context_vars": hook_state.global_context_vars,
                    "inputs": ExecutionInputsDTO(
                        dynamic_inputs=final_dict,
                        raw_inputs=final_dict,
                        target_locale=post_target_locale,
                        user_role=post_user_role,
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
            elif isinstance(post_hook_state.inputs, Mapping):
                final_dict = dict(post_hook_state.inputs)
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
                        await self.exec_repo.update_execution(
                            context.execution_id, ExecutionUpdateDTO(step_states=new_states)
                        )
                    continue

            break

        for key in ["profiler_metrics", VirtualSystemStepID.STEP_METADATA.value, "_audit_signature"]:
            if key in state_data:
                final_dict[key] = state_data[key]

        meta_dict = {}
        if "_step_metadata" in final_dict:
            existing_meta = final_dict["_step_metadata"]
            if isinstance(existing_meta, BaseModel):
                meta_dict = existing_meta.model_dump(exclude_none=True)
            elif isinstance(existing_meta, Mapping):
                meta_dict = dict(existing_meta)

        meta_dict["task_blueprint"] = blueprint_id
        if isinstance(self._engine, SynthesisEngine):
            meta_dict["model_strategy"] = "synthesis"
        else:
            meta_dict["model_strategy"] = "prompt"

        if isinstance(step_obj.cognitive_tier, str):
            meta_dict["cognitive_tier"] = step_obj.cognitive_tier
        else:
            meta_dict["cognitive_tier"] = step_obj.cognitive_tier.value
        if bound_client and bound_client.model_name:
            meta_dict["physical_model"] = bound_client.model_name
        if usage_agg.total_tokens > 0 or usage_agg.cost_usd > 0.0:
            if "token_usage" not in meta_dict:
                meta_dict["token_usage"] = usage_agg.model_dump(exclude_none=True)
        final_dict["_step_metadata"] = meta_dict

        metadata = {
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

from backend_v2.settings import get_settings

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

if TYPE_CHECKING:
    from backend_v2.services.orchestrator.engines.base import ExecutionEngine

from backend_v2.core.hook_registry import HookDependencies, HookState
from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.models.chunking import ChunkingRequest
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import PromptBlock
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.quote_evidence import SourceDocumentContext
from backend_v2.models.enums import VirtualSystemStepID
from backend_v2.models.state import StateProjector, TraceEvent
from backend_v2.models.v2_core import (
    ExecutionRecord,
    FrozenContext,
    StepRule,
    Workflow,
)
from backend_v2.models.v2_core import Step as V2Step
from backend_v2.services.orchestrator.chunking_service import ChunkingService
from backend_v2.services.orchestrator.strategies.base import NodeStrategy, StrategyContext
from backend_v2.services.orchestrator.strategies.llm_execution.context_builder import ContextBuilder
from backend_v2.services.orchestrator.strategies.llm_execution.prompt_factory import PromptFactory
from backend_v2.utils.alias_engine import AliasEngine
from backend_v2.utils.llm_debug_logger import write_debug_prompt_log

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
        exec_repo: Any,
        workflow_repo: Any,
        comp_repo: Any,
        prompt_block_repo: Any,
        output_profile_repo: Any,
        identity_repo: Any,
        audit_repo: Any,
        system_repo: Any,
        prompt_compiler: Any,
        engine: ExecutionEngine,
        arq_pool: Any | None = None,
    ) -> None:
        """Initialize the LLM strategy with a mandatory execution engine.

        Args:
            exec_repo: Execution repository.
            workflow_repo: Workflow repository.
            comp_repo: Component repository.
            prompt_block_repo: Prompt block repository.
            output_profile_repo: Output profile repository.
            identity_repo: Identity repository.
            audit_repo: Audit repository.
            system_repo: System repository.
            prompt_compiler: Prompt compiler.
            engine: Mandatory execution engine instance.
            arq_pool: Optional arq pool.
        """
        super().__init__(
            exec_repo,
            workflow_repo,
            comp_repo,
            prompt_block_repo,
            output_profile_repo,
            identity_repo,
            audit_repo,
            system_repo,
            prompt_compiler,
            arq_pool,
        )
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

        inputs_unwrapped = (
            inputs_payload.get("inputs", inputs_payload) if isinstance(inputs_payload, dict) else inputs_payload
        )

        texts: list[str] = []
        if isinstance(inputs_unwrapped, dict):
            for v in inputs_unwrapped.values():
                if isinstance(v, str):
                    texts.append(v)
        elif isinstance(inputs_unwrapped, str):
            texts.append(inputs_unwrapped)

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
            global_context_vars=context.global_context_vars,
            inputs=state_data,
        )

        hook_state, pre_events = await self.run_pre_hooks(step_obj, step, hook_state, hook_deps)
        state_data = hook_state.inputs.copy()

        # Tier 4 Fix: Removed rinnakkainen _apply_alias_chunks_and_audit() that created
        # conflicting doc IDs (doc1..docN) and <source ID="..." label="..."> XML wrappers
        # INSIDE the data. AliasEngine + prompt_compiler.build_xml_context() are the
        # Single Source of Truth for all source aliasing (alias_engine_llm_isolation_mandate).

        all_prompt_blocks_raw = await self.prompt_block_repo.get_all_prompt_blocks()
        print(f"DEBUG: all_prompt_blocks_raw = {all_prompt_blocks_raw}")
        all_prompt_blocks: list[PromptBlock] = []
        for raw in all_prompt_blocks_raw:
            try:
                all_prompt_blocks.append(PromptBlock.model_validate(raw))
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

        if "profile_id" not in context.metadata or not context.metadata["profile_id"]:
            msg = f"Execution metadata missing mandatory 'profile_id' for workflow {context.workflow_id}."
            raise ConfigurationError(msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})
        target_profile = context.metadata["profile_id"]

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

        # Phase 4 Step 3: Wire Best-of-Three ensemble flag
        is_lightweight = any(block.is_lightweight_protocol for block in criteria_blocks_models)
        if hook_state.metadata is None:
            hook_state.metadata = {}

        hook_state.metadata["execution_id"] = context.execution_id

        if is_lightweight:
            hook_state.metadata["is_lightweight_extraction"] = True

        if "target_locale" not in context.metadata or not context.metadata["target_locale"]:
            msg = f"Execution metadata missing mandatory 'target_locale' for workflow {context.workflow_id}."
            raise ConfigurationError(msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})
        target_locale = str(context.metadata["target_locale"])
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
                            if b.category_id == "matrix":
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
        is_matrix_step = any(b.category_id == "matrix" for b in criteria_blocks_models)
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
            except Exception as e:
                logger.warning(f"[LLMStrategy] Failed to write debug prompt log: {e}")

        if output_profile:
            exec_params = ["\n<execution_parameters>"]
            if output_profile.tone_instruction:
                tone = output_profile.tone_instruction.get(target_locale, output_profile.tone_instruction.get("en", ""))
                if tone:
                    exec_params.append(f"  <tone_instruction>{tone}</tone_instruction>")
            if output_profile.layouts:
                try:
                    layouts_json = json.dumps(
                        [layout.model_dump(mode="json") for layout in output_profile.layouts], ensure_ascii=False
                    )
                    exec_params.append(f"  <layouts>{layouts_json}</layouts>")
                except Exception as e:
                    logger.warning(f"Failed to serialize layouts for prompt injection: {e}")
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

        if hook_state.metadata is None:
            hook_state.metadata = {}
        hook_state.metadata["source_document_ids"] = source_doc_ids
        # Phase 2: Export full alias state for chunk_worker to reconstruct unified alias_map
        hook_state.metadata["alias_manifest"] = alias_engine.to_manifest().model_dump(mode="json")
        hook_state.metadata["allowed_dynamic_keys"] = (
            list(step.input_mappings.keys()) if getattr(step, "input_mappings", None) else []
        )

        # Fetch execution record to build SourceDocumentContext for validation context
        execution_record_raw = None
        try:
            res = self.exec_repo.get_execution(context.execution_id)
            if inspect.isawaitable(res):
                execution_record_raw = await res
            else:
                execution_record_raw = res
        except Exception:
            pass

        if execution_record_raw:
            try:
                if isinstance(execution_record_raw, ExecutionRecord):
                    exec_obj = execution_record_raw
                else:
                    exec_obj = ExecutionRecord.model_validate(execution_record_raw, strict=False)
                manifest = exec_obj.source_identity_manifest or {}

                source_docs = []
                inputs_dict = inputs_payload.get("inputs", {})
                if isinstance(inputs_dict, dict):
                    for k, text_content in inputs_dict.items():
                        if isinstance(text_content, str):
                            display_name = str(manifest.get(k, k))
                            doc_ctx = SourceDocumentContext(
                                opaque_id=k, text_content=text_content, display_name=display_name
                            )
                            source_docs.append(doc_ctx.model_dump(mode="json"))

                hook_state.metadata["source_documents"] = source_docs
            except Exception:
                pass

        pass

        if frozen_ctx:
            allowed_dynamic_keys = [e.input_key for e in context.expected_inputs] if context.expected_inputs else []
            if getattr(step, "input_mappings", None):
                allowed_dynamic_keys.extend(step.input_mappings.keys())
            allowed_dynamic_keys = list(set(allowed_dynamic_keys))
            hook_state.metadata["allowed_dynamic_keys"] = allowed_dynamic_keys

            # Extensibility for dynamic MCP providers
            mcp_prefixes = ["call_", "mcp_", "search_"]
            mcp_tools_list = getattr(step, "mcp_tools", None)
            if mcp_tools_list:
                for tool in mcp_tools_list:
                    if isinstance(tool, dict):
                        func = tool.get("function", {})
                        if isinstance(func, dict) and func.get("name"):
                            mcp_prefixes.append(f"{func['name']}_")
                    elif hasattr(tool, "function") and hasattr(tool.function, "name"):
                        mcp_prefixes.append(f"{tool.function.name}_")
            hook_state.metadata["allowed_mcp_prefixes"] = list(set(mcp_prefixes))

            global_schema = self.compiler.build_dynamic_schema(
                schema_name=f"Step_{step.id}_Response",
                criteria=criteria_blocks,
                has_shuffled_atoms=has_shuffled_atoms,
                target_locale=target_locale,
                strictness_level=context.strictness_level,
                source_document_ids=source_doc_ids,
                allowed_dynamic_keys=allowed_dynamic_keys,
                allowed_mcp_prefixes=hook_state.metadata.get("allowed_mcp_prefixes", []),
                expected_sdui_type=getattr(step, "expected_sdui_type", "grid"),
            )
            frozen_ctx.generated_schemas[step.id] = global_schema.model_json_schema()

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

            from backend_v2.models.dtos.engine import EngineExecutionRequest, MatrixEvaluationContext

            matrix_block = next((b for b in criteria_blocks if b.category_id == "matrix"), None)
            matrix_block_id = matrix_block.id if matrix_block else None

            matrix_context = None
            if matrix_block:
                matrix_context = MatrixEvaluationContext(
                    theory_grounding=matrix_block.theory_grounding,
                    matrix_objective=matrix_block.ai_description,
                    allow_contextual_override=matrix_block.allow_contextual_override,
                )

            is_synthesis_step = context.model_strategy == "synthesis"

            if is_synthesis_step:
                target_locale = str(context.metadata.get("target_locale", "en"))

                blackboard = hook_state.global_context_vars.get("__GLOBAL_ATOM_BLACKBOARD__", {})
                doc_aliases = list(blackboard.get("atoms_by_input", {}).keys()) or ["N/A"]

                dag_results = {}
                for step_res in hook_state.inputs.values():
                    if isinstance(step_res, dict) and "evaluations" in step_res:
                        for ev in step_res["evaluations"]:
                            a_id = ev.get("tda_id") or ev.get("atom_id")
                            if a_id:
                                dag_results[a_id] = ev

                dynamic_schema = self.compiler.build_dynamic_schema(
                    schema_name=f"Step_{step.id}_Response",
                    criteria=criteria_blocks,
                    has_shuffled_atoms=False,
                    target_locale=target_locale,
                    strictness_level=context.strictness_level,
                    source_document_ids=doc_aliases,
                    expected_sdui_type=getattr(step, "expected_sdui_type", "grid"),
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

            if is_synthesis_step and engine_result.synthesis_output is not None:
                final_dict = engine_result.synthesis_output
            else:
                final_dict = {
                    "results": [r.model_dump() for r in engine_result.results],
                    "hydrated_references": {k: v.model_dump() for k, v in engine_result.hydrated_references.items()},
                }

            latency_ms = int((time.time() - telemetry_start_time) * 1000)
            usage_agg = TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
            all_prompt_contexts: list[dict[str, Any]] = []
            safe_context: dict[str, Any] = {**hook_state.global_context_vars, "steps": projector.snapshot}

            post_hook_state = hook_state.model_copy(
                update={
                    "global_context_vars": safe_context,
                    "inputs": final_dict,
                }
            )

            post_hook_state, post_events = await self.run_post_hooks(
                step_obj=step_obj,
                step=step,
                hook_state=post_hook_state,
                hook_deps=hook_deps,
            )
            final_dict = post_hook_state.inputs.copy()

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

        if usage_agg.total_tokens > 0 or usage_agg.cost_usd > 0.0:
            meta = final_dict.setdefault("_step_metadata", {})
            meta["token_usage"] = usage_agg.model_dump()
            # Phase 1, Step 1.1: Ensure model_strategy is persisted in trace event metadata for execution fingerprinting
            meta["model_strategy"] = strategy_name

        return (
            pre_events
            + post_events
            + [
                TraceEvent(
                    step_name=step.id,
                    event_type="output",
                    content=final_dict,
                    metadata={
                        "latency_ms": latency_ms,
                        "chunk_size": len(chunks_list),
                        "context_char_length": context_char_length,
                        "prompt_contexts": all_prompt_contexts,
                    },
                )
            ]
        )

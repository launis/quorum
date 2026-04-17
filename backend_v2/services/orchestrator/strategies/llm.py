import logging
from typing import Any

from backend_v2.core.hook_registry import HookDependencies, HookState
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.models.state import StateProjector, TraceEvent
from backend_v2.models.v2_core import FrozenContext, StepRule
from backend_v2.models.v2_core import Step as V2Step
from backend_v2.services.orchestrator.strategies.base import NodeStrategy, StrategyContext

logger = logging.getLogger(__name__)


class LLMNodeStrategy(NodeStrategy):
    """Executes an AI/LLM Step.

    Manages dynamic schema compilation, instruction aggregation, tracing optimization
    for token context explosion, and routes through either a standard structured prediction
    task or an autonomous MCP Tool Loop depending on step configuration.
    """

    async def execute(
        self,
        step: StepRule,
        projector: StateProjector,
        context: StrategyContext,
        frozen_ctx: FrozenContext | None,
        trace: list[TraceEvent] | None,
    ) -> list[TraceEvent]:
        current_state = dict(projector.snapshot)

        blueprint_id = getattr(step, "task_blueprint", None)
        if not blueprint_id:
            logger.error(
                "Step has no task_blueprint configured.",
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "step_id": step.id},
            )
            raise AppException(
                message=f"Step {step.id} has no task_blueprint configured.",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
            )

        step_def = await self.repository.get_step_by_id(blueprint_id)
        if not step_def:
            logger.error(
                f"Configuration error: Step '{blueprint_id}' not found.",
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "step_id": step.id},
            )
            raise AppException(
                message=f"Configuration error: Step '{blueprint_id}' not found.",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
            )

        step_obj = V2Step.model_validate(step_def)
        hook_deps = HookDependencies(repository=self.repository)

        state_data = dict(current_state)
        hook_state = HookState(
            execution_id=context.execution_id,
            workflow_id=context.workflow_id,
            step_id=step.id,
            task_blueprint=blueprint_id,
            metadata=context.metadata,
            inputs=state_data,
        )

        # 1. Pre-Hooks
        hook_state = await self.run_pre_hooks(step_obj, step, hook_state, hook_deps, state_data)
        state_data = dict(hook_state.inputs)

        # 2. Compile LLM Prompts & Schemas
        criteria_blocks = []
        all_prompt_blocks = await self.repository.get_all_prompt_blocks()
        block_map = {b["id"]: b for b in all_prompt_blocks if "id" in b}
        # Enforce Architectual Parity: Fail-Fast if Pipeline Amnesia occurs
        target_profile = context.metadata.get("profile_id")
        if not target_profile:
            from backend_v2.exceptions import ConfigurationError

            msg = f"Execution metadata missing mandatory 'profile_id' for workflow {context.workflow_id}."
            raise ConfigurationError(msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR})

        for m_id in step_obj.prompt_blocks:
            b = block_map.get(m_id)
            if b:
                criteria_blocks.append(b)
            else:
                logger.error(
                    f"PromptBlock '{m_id}' not found.",
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.name, "step_id": step.id},
                )
                raise AppException(
                    message=f"PromptBlock '{m_id}' not found.",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED},
                )

        target_locale = str(context.metadata.get("target_locale", "en"))
        static_instructions = self.compiler.compile_static_instructions(criteria_blocks, target_locale)
        dynamic_instructions = self.compiler.compile_dynamic_instructions(criteria_blocks, target_locale)

        # Epic 12: Generate Thick XML/Markdown rubrics for System Prompt
        xml_rubrics = self.compiler.compile_xml_rubrics(criteria_blocks, target_locale)

        # Epic 20 Phase 7: Strict Blind System Instruction
        blind_instruction = self.compiler.compile_blind_system_instruction(target_locale)

        # Epic 13 M2: Resolve tools and build dynamic instruction
        effective_mcp_tools = step_obj.allowed_mcp_tools
        mcp_instruction = self.compiler.generate_mcp_instruction(effective_mcp_tools)

        system_prompt = "Complete the evaluation according to the provided schema."
        if static_instructions:
            system_prompt += f"\n\n{static_instructions}"
        if blind_instruction:
            system_prompt += f"\n\n{blind_instruction}"
        if xml_rubrics:
            system_prompt += f"\n\n{xml_rubrics}"
        if mcp_instruction:
            system_prompt += f"\n\n{mcp_instruction}"

        # 3. Prevent Token Explosion with recursive trace pruning
        import copy
        llm_context_data = copy.deepcopy(state_data)

        # Epic 23 FinOps: Modify state_data for LLM Context:
        # User Mandate: "atomisoiduista kentistä ei pidä tulla kuin true/false. Matriiseista ja prompteista pitää tulla tekstikentät."
        def _strip_heavy_keys(obj: Any) -> None:
            if isinstance(obj, dict):
                # 1. Remove raw context blocks that the LLM cannot effectively map and just consume tokens
                obj.pop("shuffled_atoms", None)

                # 2. Compress Atomized evaluated fields to strictly true/false booleans!
                if "evaluations" in obj and isinstance(obj["evaluations"], list):
                    bool_only = []
                    for atom in obj["evaluations"]:
                        if isinstance(atom, dict) and "boolean" in atom:
                            bool_only.append(atom["boolean"])
                    if bool_only:
                        obj["evaluations"] = bool_only
                else:
                    # Fallback cleanup for legacy atom items just in case
                    obj.pop("quote", None)
                    obj.pop("reasoning", None)

                for _, val in obj.items():
                    _strip_heavy_keys(val)
            elif isinstance(obj, list):
                for item in obj:
                    _strip_heavy_keys(item)
                    
        _strip_heavy_keys(llm_context_data)

        xml_ctx = self.compiler.build_xml_context(
            input_mappings=step.input_mappings if hasattr(step, "input_mappings") else {},
            state_data=llm_context_data,
            target_locale=target_locale,
            expected_inputs=context.expected_inputs,
        )

        user_payload = xml_ctx
        if dynamic_instructions:
            user_payload += f"\n\n--- RUNTIME AWARENESS ---\n{dynamic_instructions}"

        from backend_v2.models.enums import SystemConcurrency
        from backend_v2.services.orchestrator.chunking_service import ChunkingService
        from backend_v2.models.chunking import ChunkingRequest
        import asyncio
        import json

        # Epic 20 Phase 7: Inject Shuffled Atoms for Blind Evaluation
        has_shuffled_atoms = False
        chunks_list = []
        if "shuffled_atoms" in state_data:
            has_shuffled_atoms = True
            shuffled_atoms = state_data["shuffled_atoms"]

            if not isinstance(shuffled_atoms, list) or len(shuffled_atoms) == 0:
                msg = f"Strict Fail-Fast Enforced: 'shuffled_atoms' is empty or not a list for step '{step.id}'."
                logger.error("[LLMStrategy] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

            req = ChunkingRequest[dict](
                parent_id=context.workflow_id,
                items=shuffled_atoms,
                max_chunk_size=SystemConcurrency.LLM_MAX_CHUNK_SIZE.value,
            )
            chunks_list = ChunkingService.chunk_payload(req)
        else:
            chunks_list = [None]  # Dummy to execute single non-chunk payload

        has_search = any("search_result" in v for v in state_data.values() if isinstance(v, dict))

        dynamic_schema = self.compiler.build_dynamic_schema(
            schema_name=f"Step_{step.id}_Response",
            criteria=criteria_blocks,
            has_search_result=has_search,
            has_shuffled_atoms=has_shuffled_atoms,
            target_locale=target_locale,
        )

        if frozen_ctx:
            frozen_ctx.generated_schemas[step.id] = dynamic_schema.model_json_schema()

        # 4. Invoke LLM Model (Tool Loop vs Direct Output)
        strategy_name = context.model_strategy
        if not strategy_name:
            logger.error(
                "Step has no model_strategy defined. Zero fallbacks allowed.",
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name, "step_id": step.id},
            )
            raise AppException(
                message=f"Step {step.id} has no model_strategy defined (Fail-Fast: No fallbacks allowed).",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
            )
        bound_client = await LLMClient.from_strategy(strategy_name, self.repository)

        from backend_v2.services.mcp.mcp_tool_loop import execute_tool_loop

        sem = asyncio.Semaphore(SystemConcurrency.MAX_CONCURRENT_LLM_STEPS.value)

        async def process_chunk(chunk: Any) -> tuple[dict[str, Any], dict[str, Any], list[Any]]:
            async with sem:
                local_payload = user_payload
                if chunk is not None:
                    atoms_json = json.dumps(chunk.items, ensure_ascii=False, indent=2)
                    local_payload += f"\n\n<BLIND_ATOMS_TO_EVALUATE>\n{atoms_json}\n</BLIND_ATOMS_TO_EVALUATE>\n"

                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": local_payload},
                ]

                chunk_final: dict[str, Any] = {}
                chunk_usage: dict[str, Any] = {}
                chunk_traces: list[Any] = []

                if effective_mcp_tools:
                    try:
                        loop_res = await execute_tool_loop(
                            llm_client=bound_client,
                            messages=messages,
                            response_model=dynamic_schema,
                            allowed_tools=effective_mcp_tools,
                            step_name=step.id,
                            mock_identity=step.id,
                            target_language=target_locale,
                            synthesis_instructions=state_data.get("synthesis_instructions"),
                        )
                        chunk_final = dict(loop_res.result_data)
                        chunk_usage = dict(loop_res.usage) if loop_res.usage else {}
                        if loop_res.audit_traces:
                            chunk_traces.extend(loop_res.audit_traces)
                    except Exception as e:
                        logger.error(
                            "Execution of MCP tool loop failed.",
                            extra={
                                "error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.name,
                                "step_id": step.id,
                                "detail": str(e),
                            },
                            exc_info=True,
                        )
                        if isinstance(e, AppException):
                            raise
                        raise AppException(
                            message=f"MCP Tool Loop Execution failed: {str(e)}",
                            status_code=500,
                            details={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL},
                        ) from e
                else:
                    try:
                        result, usage = await bound_client.run_structured_task(
                            messages=messages,
                            response_model=dynamic_schema,
                            mock_identity=step.id,
                        )
                        chunk_final = dict(result.model_dump(mode="json"))
                        chunk_usage = dict(usage) if usage else {}
                    except Exception as e:
                        logger.error(
                            "Execution of structured LLM task failed.",
                            extra={
                                "error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.name,
                                "step_id": step.id,
                                "detail": str(e),
                            },
                            exc_info=True,
                        )
                        if isinstance(e, AppException):
                            raise
                        raise AppException(
                            message=f"Structured LLM execution failed: {str(e)}",
                            status_code=500,
                            details={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL},
                        ) from e
                
                return chunk_final, chunk_usage, chunk_traces

        tasks = []
        async with asyncio.TaskGroup() as tg:
            for c in chunks_list:
                tasks.append(tg.create_task(process_chunk(c)))

        final_dict: dict[str, Any] = {}
        usage_dict: dict[str, Any] = {}

        for t in tasks:
            c_final, c_usage, c_traces = t.result()

            if not final_dict:
                final_dict = c_final
            else:
                if "evaluations" in c_final and "evaluations" in final_dict:
                    final_dict["evaluations"].extend(c_final["evaluations"])
                if "reasoning_trace" in c_final and "reasoning_trace" in final_dict:
                    final_dict["reasoning_trace"] += f"\n\n[Chunk]: {c_final['reasoning_trace']}"
                if "evaluation_notes" in c_final and "evaluation_notes" in final_dict:
                    final_dict["evaluation_notes"] += f"\n\n[Chunk]: {c_final['evaluation_notes']}"

            for k, v in c_usage.items():
                usage_dict[k] = usage_dict.get(k, 0) + v

            if frozen_ctx and c_traces:
                existing_hashes = {f"{a.tool_id}::{a.query}" for a in frozen_ctx.mcp_tool_audit}
                for t_trace in c_traces:
                    thash = f"{t_trace.tool_id}::{t_trace.query}"
                    if thash not in existing_hashes:
                        frozen_ctx.mcp_tool_audit.append(t_trace)
                        existing_hashes.add(thash)

        # 5. Post-Hooks
        safe_context = {
            k: v.model_dump(mode="json") if hasattr(v, "model_dump") else v for k, v in dict(projector.snapshot).items()
        }

        final_dict = await self.run_post_hooks(
            step_obj=step_obj,
            step=step,
            hook_state=hook_state,
            hook_deps=hook_deps,
            final_dict=final_dict,
            global_context_vars=safe_context,
        )

        # 6. Metadata Merging
        for key in ["profiler_metrics", "step_metadata", "_audit_signature"]:
            if key in state_data:
                final_dict[key] = state_data[key]

        if usage_dict:
            if "_step_metadata" not in final_dict:
                final_dict["_step_metadata"] = {}
            final_dict["_step_metadata"]["token_usage"] = usage_dict

        return [
            TraceEvent(
                step_name=step.id,
                event_type="output",
                content=final_dict,
            )
        ]

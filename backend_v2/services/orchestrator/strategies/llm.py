import asyncio
import copy
import hashlib
import json
import logging
import time
from typing import Any

import litellm
from pydantic import RootModel

from backend_v2.core.hook_registry import HookDependencies, HookState
from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes, TokenLimitExceededError
from backend_v2.llm.client import LLMClient
from backend_v2.models.chunking import ChunkingRequest
from backend_v2.models.enums import EvaluationMandate, SystemConcurrency
from backend_v2.models.state import StateProjector, TraceEvent
from backend_v2.models.v2_core import FrozenContext, StepRule
from backend_v2.models.v2_core import Step as V2Step
from backend_v2.models.view.sdui import AnySduiBlock
from backend_v2.services.mcp.mcp_tool_loop import execute_tool_loop
from backend_v2.services.orchestrator.chunking_service import ChunkingService
from backend_v2.services.orchestrator.context_router import ContextRouter
from backend_v2.services.orchestrator.strategies.base import NodeStrategy, StrategyContext
from backend_v2.utils.dict_utils import resolve_dot_notation

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
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
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
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
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
            global_context_vars={},
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
            msg = f"Execution metadata missing mandatory 'profile_id' for workflow {context.workflow_id}."
            raise ConfigurationError(msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value})

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
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

        target_locale = str(context.metadata.get("target_locale", "en"))
        static_instructions = self.compiler.compile_static_instructions(criteria_blocks, target_locale)
        dynamic_instructions = self.compiler.compile_dynamic_instructions(criteria_blocks, target_locale)

        # Epic 20 Phase 7: Strict Blind System Instruction
        blind_instruction = self.compiler.compile_blind_system_instruction(target_locale)

        # Epic 13 M2: Resolve tools and build dynamic instruction
        effective_mcp_tools = step_obj.allowed_mcp_tools
        mcp_instruction = self.compiler.generate_mcp_instruction(effective_mcp_tools)

        base_system_prompt = "Complete the evaluation according to the provided schema."
        if static_instructions:
            base_system_prompt += f"\n\n{static_instructions}"
        if blind_instruction:
            base_system_prompt += f"\n\n{blind_instruction}"
        if mcp_instruction:
            base_system_prompt += f"\n\n{mcp_instruction}"

        # 3. Prevent Token Explosion with recursive trace pruning
        # Epic 27 Phase 1: Input Pruning - Restrict context to explicitly mapped data keys
        llm_context_data: dict[str, Any] = {}
        input_mappings = step.input_mappings if hasattr(step, "input_mappings") and step.input_mappings else {}
        input_mappings = dict(input_mappings)  # Ensure mutability

        MAX_SAFE_TOKENS = 100000
        new_input_mappings = {}

        for _logical_name, path in input_mappings.items():
            if not isinstance(path, str):
                continue

            clean_path = path[1:] if path.startswith("$") else path

            try:
                resolved_value = resolve_dot_notation(state_data, clean_path)

                # Task 3: ContextRouter integration for trace data
                if clean_path.startswith("steps."):
                    if isinstance(resolved_value, dict) and "normalized_score" in resolved_value:
                        try:
                            output_profile = getattr(context, "output_profile", None)
                            pruned = ContextRouter.route_and_prune(resolved_value, output_profile)
                            resolved_value = f"<matrix_data>\n{pruned.model_dump_json()}\n</matrix_data>"
                        except Exception as e:
                            logger.warning("ContextRouter trace pruning failed: %s", e)

                val_str = str(resolved_value)
                # Task 2: Rigorous token checks
                try:
                    tokens = litellm.token_counter(model="gpt-4o", text=val_str)
                    if tokens > MAX_SAFE_TOKENS:
                        msg = f"Mapping '{_logical_name}' exceeded token limit ({tokens} > {MAX_SAFE_TOKENS})."
                        raise TokenLimitExceededError(message=msg)
                except TokenLimitExceededError:
                    raise
                except Exception as e:
                    logger.warning("Token counting failed for %s: %s", _logical_name, e)

                # Map back to llm_context_data in its original path structure so _extract_value_from_state works
                parts = clean_path.split(".")
                if clean_path.startswith("steps."):
                    parts = clean_path[len("steps.") :].split(".")

                curr = llm_context_data
                for i, part in enumerate(parts):
                    if i == len(parts) - 1:
                        curr[part] = copy.deepcopy(resolved_value)
                    else:
                        if part not in curr:
                            curr[part] = {}
                        curr = curr[part]

                new_input_mappings[_logical_name] = path
            except Exception as e:
                if isinstance(e, TokenLimitExceededError):
                    raise
                logger.warning("Failed to resolve input mapping %s: %s", path, e)

        input_mappings = new_input_mappings

        # Epic 23 FinOps: Modify state_data for LLM Context:
        # User Mandate: "atomisoiduista kentistä ei pidä tulla kuin true/false.
        # Matriiseista ja prompteista pitää tulla tekstikentät."
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
            input_mappings=input_mappings,
            state_data=llm_context_data,
            target_locale=target_locale,
            expected_inputs=context.expected_inputs,
        )

        user_payload = xml_ctx
        if dynamic_instructions:
            user_payload += f"\n\n--- RUNTIME AWARENESS ---\n{dynamic_instructions}"

        # Epic 20 Phase 7: Inject Shuffled Atoms for Blind Evaluation
        has_shuffled_atoms = False
        chunks_list: list[Any] = []
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

            req = ChunkingRequest[dict[str, Any]](
                parent_id=context.workflow_id,
                items=shuffled_atoms,
                max_chunk_size=SystemConcurrency.LLM_MAX_CHUNK_SIZE.value,
            )
            chunks_list = ChunkingService.chunk_payload(req)
        else:
            chunks_list = [None]  # Dummy to execute single non-chunk payload

        has_search = any("search_result" in v for v in state_data.values() if isinstance(v, dict))

        # Epic 27 Phase 2: Dynamic Chunk Rubrics
        atom_to_block_ids: dict[str, set[str]] = {}
        for block in criteria_blocks:
            if block.get("category_id") == "matrix" and block.get("scales"):
                b_id = block.get("id")
                if not b_id:
                    continue
                for scale in block.get("scales", []):
                    scale_atoms: list[str] = []
                    for claim in scale.get("claims", []):
                        mandate = EvaluationMandate.FAIL_FAST_NO_EVIDENCE.value
                        micro_atoms = claim.get("micro_atoms")
                        if micro_atoms and len(micro_atoms) > 0:
                            scale_atoms.extend([f"{ma.strip()}{mandate}" for ma in micro_atoms])
                        else:
                            msg = f"PromptBlock '{b_id}' claim is missing mandatory 'micro_atoms' during runtime."
                            logger.error("[%s] %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                            raise AppException(
                                message=msg,
                                status_code=500,
                                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                            )

                        for text in scale_atoms:
                            aid = hashlib.md5(text.encode("utf-8")).hexdigest()
                            if aid not in atom_to_block_ids:
                                atom_to_block_ids[aid] = set()
                            atom_to_block_ids[aid].add(b_id)

        # Save standard global schema trace if frozen_ctx is provided
        if frozen_ctx:
            global_schema = self.compiler.build_dynamic_schema(
                schema_name=f"Step_{step.id}_Response",
                criteria=criteria_blocks,
                has_search_result=has_search,
                has_shuffled_atoms=has_shuffled_atoms,
                target_locale=target_locale,
            )
            frozen_ctx.generated_schemas[step.id] = global_schema.model_json_schema()

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
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )
        bound_client = await LLMClient.from_strategy(strategy_name, self.repository)

        sem = asyncio.Semaphore(SystemConcurrency.MAX_CONCURRENT_LLM_STEPS.value)

        async def process_chunk(chunk: Any) -> tuple[dict[str, Any], dict[str, Any], list[Any]]:
            async with sem:
                local_payload = user_payload
                chunk_criteria = list(criteria_blocks)

                if chunk is not None:
                    atoms_json = json.dumps(chunk.items, ensure_ascii=False, indent=2)
                    local_payload += f"\n\n<BLIND_ATOMS_TO_EVALUATE>\n{atoms_json}\n</BLIND_ATOMS_TO_EVALUATE>\n"

                    # Apply Chunk context subsetting
                    if has_shuffled_atoms:
                        chunk_matrix_ids = set()
                        for item in chunk.items:
                            aid = item.get("atom_id") if isinstance(item, dict) else getattr(item, "atom_id", None)
                            if aid and aid in atom_to_block_ids:
                                chunk_matrix_ids.update(atom_to_block_ids[aid])

                        chunk_criteria = [
                            b
                            for b in criteria_blocks
                            if b.get("category_id") != "matrix" or b.get("id") in chunk_matrix_ids
                        ]

                # Dynamically build system prompt and schema for this chunk
                local_xml_rubrics = self.compiler.compile_xml_rubrics(chunk_criteria, target_locale)

                local_system_prompt = base_system_prompt
                if local_xml_rubrics:
                    local_system_prompt += f"\n\n{local_xml_rubrics}"

                local_dynamic_schema = self.compiler.build_dynamic_schema(
                    schema_name=f"Step_{step.id}_Response",
                    criteria=chunk_criteria,
                    has_search_result=has_search,
                    has_shuffled_atoms=has_shuffled_atoms,
                    target_locale=target_locale,
                )

                # Epic 27 Context Segregation: Provider-Agnostic Prompt Caching
                # To activate native Prompt Caching on Vertex(Gemini)/OpenAI/Anthropic,
                # the identical massive context MUST come first.
                messages = [
                    {"role": "system", "content": f"System Context & Reference Data:\n\n{local_payload}"},
                    {"role": "user", "content": local_system_prompt},
                ]

                chunk_final: dict[str, Any] = {}
                chunk_usage: dict[str, Any] = {}
                chunk_traces: list[Any] = []

                if effective_mcp_tools:
                    try:
                        loop_res = await execute_tool_loop(
                            llm_client=bound_client,
                            messages=messages,
                            response_model=local_dynamic_schema,
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
                            details={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.value},
                        ) from e
                else:
                    try:
                        if getattr(context, "output_profile", None) is not None:

                            class SduiResponseList(RootModel[list[AnySduiBlock]]):
                                pass

                            result, usage = await bound_client.run_structured_task(
                                messages=messages,
                                response_model=SduiResponseList,
                                mock_identity=step.id,
                                max_retries=3,
                            )
                            chunk_final = {"blocks": result.model_dump(mode="json")}
                        else:
                            result, usage = await bound_client.run_structured_task(
                                messages=messages,
                                response_model=local_dynamic_schema,
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
                            details={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL.value},
                        ) from e

                return chunk_final, chunk_usage, chunk_traces

        # Epic 27 Phase 5: Map-Reduce Telemetry Tracking
        telemetry_start_time = time.time()
        context_char_length = len(user_payload)
        logger.info(
            "Epic 27 Telemetry: Compiling map-reduce for step '%s'. Context Bounds: %d chars, Chunk count: %d.",
            step.id,
            context_char_length,
            len(chunks_list),
        )

        tasks = []
        async with asyncio.TaskGroup() as tg:
            for c in chunks_list:
                tasks.append(tg.create_task(process_chunk(c)))

        latency_ms = int((time.time() - telemetry_start_time) * 1000)

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

                # Epic 27: Zero-Compromise XAI Aggregation
                # Preserve matrix XAI extensions generated in subsequent map-reduce chunks.
                for k in c_final.keys():
                    if k in ["evaluations", "reasoning_trace", "evaluation_notes"]:
                        continue

                    if k.startswith("matrix_") or k.startswith("blk_"):
                        if k not in final_dict:
                            final_dict[k] = c_final[k]
                        else:
                            if isinstance(c_final[k], dict) and isinstance(final_dict[k], dict):
                                for s_key, s_val in c_final[k].items():
                                    if s_key not in final_dict[k]:
                                        final_dict[k][s_key] = s_val
                                    else:
                                        if isinstance(s_val, str) and isinstance(final_dict[k][s_key], str):
                                            final_dict[k][s_key] += f" {s_val}"

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
                metadata={
                    "latency_ms": latency_ms,
                    "chunk_size": len(chunks_list),
                    "context_char_length": context_char_length,
                },
            )
        ]

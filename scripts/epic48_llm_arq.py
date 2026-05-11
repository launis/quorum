import os

llm_path = "backend_v2/services/orchestrator/strategies/llm.py"
with open(llm_path, "r", encoding="utf-8") as f:
    code = f.read()

# 1. Add imports
if "from backend_v2.services.orchestrator.matrix_reducer import MatrixReducer" not in code:
    code = code.replace(
        "from backend_v2.services.orchestrator.strategies.llm_execution.prompt_factory import PromptFactory",
        "from backend_v2.services.orchestrator.strategies.llm_execution.prompt_factory import PromptFactory\nfrom backend_v2.services.orchestrator.matrix_reducer import MatrixReducer\nimport json"
    )

# 2. Replace the task group with Arq enqueue
old_taskgroup = """            tasks = []
            async with asyncio.TaskGroup() as tg:
                for c in chunks_list:
                    syn_instr = state_data["synthesis_instructions"] if "synthesis_instructions" in state_data else None
                    tasks.append(
                        tg.create_task(
                            ChunkWorker.process_chunk(
                                chunk=c,
                                sem=sem,
                                compiler=self.compiler,
                                criteria_blocks=criteria_blocks,
                                user_payload=user_payload,
                                base_system_prompt=base_system_prompt,
                                has_search=has_search,
                                has_shuffled_atoms=has_shuffled_atoms,
                                atom_to_block_ids=atom_to_block_ids,
                                effective_mcp_tools=effective_mcp_tools,
                                bound_client=bound_client,
                                step_id=step.id,
                                target_locale=target_locale,
                                synthesis_instructions=syn_instr,
                                output_profile=None,
                                strictness_level=context.strictness_level,
                            )
                        )
                    )"""

new_arq = """            syn_instr = state_data["synthesis_instructions"] if "synthesis_instructions" in state_data else None
            
            # Map Phase: Distribute to Arq Workers
            redis = self.arq_pool
            hkey = f"exec:{context.execution_id}:step:{step.id}"
            
            # Reset Redis accumulator state just in case of retry
            if redis:
                await redis.delete(hkey)
            
            if redis:
                for i, c in enumerate(chunks_list):
                    # In real production, file_path would be passed instead of reading the whole text
                    # Here we pass user_payload as the payload due to mock limitations
                    await redis.enqueue_job(
                        "evaluate_chunk_job",
                        context.execution_id,
                        step.id,
                        i,
                        len(chunks_list),
                        None,  # file_path
                        c.items,
                        [b.model_dump() for b in criteria_blocks],
                        base_system_prompt,
                        has_search,
                        has_shuffled_atoms,
                        atom_to_block_ids,
                        effective_mcp_tools,
                        target_locale,
                        syn_instr,
                        context.strictness_level
                    )
            
                # Wait Phase: Poll Redis for Completion (Synchronous Block)
                while True:
                    completed = await redis.hget(hkey, "completed")
                    if int(completed or 0) == len(chunks_list):
                        break
                    await asyncio.sleep(1)
            else:
                # Fallback to TaskGroup if Redis is not configured (e.g. tests)
                tasks = []
                async with asyncio.TaskGroup() as tg:
                    for c in chunks_list:
                        tasks.append(
                            tg.create_task(
                                ChunkWorker.process_chunk(
                                    chunk=c,
                                    sem=sem,
                                    compiler=self.compiler,
                                    criteria_blocks=criteria_blocks,
                                    user_payload=user_payload,
                                    base_system_prompt=base_system_prompt,
                                    has_search=has_search,
                                    has_shuffled_atoms=has_shuffled_atoms,
                                    atom_to_block_ids=atom_to_block_ids,
                                    effective_mcp_tools=effective_mcp_tools,
                                    bound_client=bound_client,
                                    step_id=step.id,
                                    target_locale=target_locale,
                                    synthesis_instructions=syn_instr,
                                    output_profile=None,
                                    strictness_level=context.strictness_level,
                                )
                            )
                        )"""

if "Map Phase: Distribute to Arq Workers" not in code:
    code = code.replace(old_taskgroup, new_arq)

# 3. Replace Accumulator loop to handle both Arq results and TaskGroup results
old_accum = """            for t in tasks:
                c_final, c_usage, c_traces = t.result()

                accumulator.add(c_final)

                if c_usage is not None:
                    usage_agg = usage_agg + c_usage

                if frozen_ctx and c_traces:
                    existing_hashes = {f"{a.tool_id}::{a.query}" for a in frozen_ctx.mcp_tool_audit}
                    for t_trace in c_traces:
                        thash = f"{t_trace.tool_id}::{t_trace.query}"
                        if thash not in existing_hashes:
                            frozen_ctx.mcp_tool_audit.append(t_trace)
                            existing_hashes.add(thash)"""

new_accum = """            # Reduce Phase: Pull chunks from Redis or Tasks
            from backend_v2.models.state import TraceEvent
            
            if redis:
                all_chunks = await redis.hgetall(hkey)
                for i in range(len(chunks_list)):
                    chunk_data_str = all_chunks.get(f"chunk_{i}".encode("utf-8"), b"{}")
                    chunk_data = json.loads(chunk_data_str)
                    
                    c_final = chunk_data.get("final", {})
                    c_usage_dict = chunk_data.get("usage")
                    c_traces_dict = chunk_data.get("traces", [])
                    
                    accumulator.add(c_final)
                    
                    if c_usage_dict:
                        usage_agg = usage_agg + TokenUsage.model_validate(c_usage_dict)
                        
                    if frozen_ctx and c_traces_dict:
                        existing_hashes = {f"{a.tool_id}::{a.query}" for a in frozen_ctx.mcp_tool_audit}
                        for tr_dict in c_traces_dict:
                            t_trace = TraceEvent.model_validate(tr_dict)
                            thash = f"{t_trace.tool_id}::{t_trace.query}"
                            if thash not in existing_hashes:
                                frozen_ctx.mcp_tool_audit.append(t_trace)
                                existing_hashes.add(thash)
            else:
                for t in tasks:
                    c_final, c_usage, c_traces = t.result()

                    accumulator.add(c_final)

                    if c_usage is not None:
                        usage_agg = usage_agg + c_usage

                    if frozen_ctx and c_traces:
                        existing_hashes = {f"{a.tool_id}::{a.query}" for a in frozen_ctx.mcp_tool_audit}
                        for t_trace in c_traces:
                            thash = f"{t_trace.tool_id}::{t_trace.query}"
                            if thash not in existing_hashes:
                                frozen_ctx.mcp_tool_audit.append(t_trace)
                                existing_hashes.add(thash)"""

if "Reduce Phase: Pull chunks from Redis" not in code:
    code = code.replace(old_accum, new_accum)

with open(llm_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Updated llm.py for Map-Reduce polling")

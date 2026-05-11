import os
import re

WORKER_ADDITIONS = """
from backend_v2.services.orchestrator.strategies.llm_execution.chunk_worker import ChunkWorker
from backend_v2.utils.redis_patcher import ASYNC_ACCUMULATOR_LUA
import json

async def evaluate_chunk_job(
    ctx: Any,
    execution_id: str,
    step_id: str,
    chunk_index: int,
    total_chunks: int,
    file_path: str | None,
    chunk_items: list[Any],
    criteria_blocks_dump: list[dict[str, Any]],
    base_system_prompt: str,
    has_search: bool,
    has_shuffled_atoms: bool,
    atom_to_block_ids: dict[str, list[str]],
    effective_mcp_tools: list[str],
    target_locale: str,
    synthesis_instructions: dict[str, Any] | None,
    strictness_level: int
) -> None:
    \"\"\"Asynchronous Arq worker job to evaluate a single text chunk.\"\"\"
    logger.info(f"[Job] evaluate_chunk_job started for {execution_id}:{step_id} chunk {chunk_index}")
    
    # 1. Fetch raw PDF if file_path is provided to leverage OS Page Cache
    user_payload = ""
    if file_path:
        storage = get_storage_driver()
        # Mock reading file for now, typically returns parsed text
        try:
            content = await storage.read_file(file_path)
            user_payload = content.decode("utf-8") if isinstance(content, bytes) else str(content)
        except Exception as e:
            logger.error(f"Failed to fetch file_path {file_path}: {e}")
            user_payload = f"Error reading file: {e}"

    # Reconstruct primitives into objects
    compiler = PromptCompiler()
    criteria_blocks = [PromptBlock.model_validate(cb) for cb in criteria_blocks_dump]
    
    # Mock a chunk object matching what ChunkWorker expects
    class DummyChunk:
        def __init__(self, items):
            self.items = items
            
    chunk_obj = DummyChunk(chunk_items)
    atom_mapping = {k: set(v) for k, v in atom_to_block_ids.items()}
    
    llm_client = LLMClient()
    sem = asyncio.Semaphore(1)
    
    # Run chunk processing
    c_final, c_usage, c_traces = await ChunkWorker.process_chunk(
        chunk=chunk_obj,
        sem=sem,
        compiler=compiler,
        criteria_blocks=criteria_blocks,
        user_payload=user_payload,
        base_system_prompt=base_system_prompt,
        has_search=has_search,
        has_shuffled_atoms=has_shuffled_atoms,
        atom_to_block_ids=atom_mapping,
        effective_mcp_tools=effective_mcp_tools,
        bound_client=llm_client,
        step_id=step_id,
        target_locale=target_locale,
        synthesis_instructions=synthesis_instructions,
        output_profile=None,
        strictness_level=strictness_level,
    )
    
    # 2. Redis Lua Script to update State without Race Conditions
    redis = ctx.get("redis")
    if not redis:
        logger.warning("Redis not found in context. Chunk state cannot be accumulated.")
        return
        
    hkey = f"exec:{execution_id}:step:{step_id}"
    
    payload_dict = {
        "final": c_final,
        "usage": c_usage.model_dump() if c_usage else None,
        "traces": [t.model_dump() for t in c_traces] if c_traces else []
    }
    
    payload_str = json.dumps(payload_dict)
    
    # Execute atomic Lua script
    is_done = await redis.eval(
        ASYNC_ACCUMULATOR_LUA,
        1,  # Number of keys
        hkey,
        str(total_chunks),
        payload_str,
        str(chunk_index)
    )
    
    if is_done == 1:
        logger.info(f"Chunk {chunk_index} finished. All {total_chunks} chunks completed for {step_id}.")
        # The main orchestrator loop polling Redis will now pick this up and execute MatrixReducer
"""

worker_path = "backend_v2/worker.py"
with open(worker_path, "r", encoding="utf-8") as f:
    worker_code = f.read()

if "evaluate_chunk_job" not in worker_code:
    # Insert before execute_workflow_job
    worker_code = worker_code.replace(
        "async def execute_workflow_job(",
        f"{WORKER_ADDITIONS}\n\nasync def execute_workflow_job("
    )
    # Add to functions list
    worker_code = worker_code.replace(
        "functions = [health_check, execute_workflow_job, generate_pdf_job, render_profile_job]",
        "functions = [health_check, evaluate_chunk_job, execute_workflow_job, generate_pdf_job, render_profile_job]"
    )
    with open(worker_path, "w", encoding="utf-8") as f:
        f.write(worker_code)
    print("Added evaluate_chunk_job to worker.py")
else:
    print("evaluate_chunk_job already in worker.py")

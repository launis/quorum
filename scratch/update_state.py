import json
import re

def update_state():
    log_path = r"c:\src\quorum\backend_debug.log"
    state_path = r"c:\src\quorum\data\files\executions\exe_f7934ceda15347079d5fbfda54153f04\monitor_state.json"
    
    # Load existing state
    with open(state_path, "r", encoding="utf-8") as f:
        state = json.load(f)
        
    # Read the log and gather all values
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        log_content = f.read()
        
    # Count LiteLLM completions
    completions = len(re.findall(r"completion\(\) model=", log_content))
    
    # Count validation failures
    validation_failures = len(re.findall(r"LLM Schema Validation Failed|Schema Validation Failed|Validation Failed", log_content, re.IGNORECASE))
    
    # Count PII redactions
    pii_redacts = sum(int(x) for x in re.findall(r"PII detected and redacted\.\s*Threat count:\s*(\d+)", log_content))
    
    # Sum queue wait times
    queue_waits = sum(float(x) for x in re.findall(r"acquired semaphore lock in\s*(\d+\.?\d*)\s*ms", log_content))
    
    # Sum exec times
    exec_times = sum(float(x) for x in re.findall(r"\[LLM Exec\].*?completed in\s*(\d+\.?\d*)\s*ms", log_content))
    
    # Update cumulative values, taking the max of existing vs parsed to prevent regression
    state["total_llm_calls"] = max(state.get("total_llm_calls", 0), completions)
    state["self_healing_attempts"] = max(state.get("self_healing_attempts", 0), validation_failures)
    state["pii_redacted_count"] = max(state.get("pii_redacted_count", 0), pii_redacts)
    state["total_queue_wait_ms"] = max(state.get("total_queue_wait_ms", 0.0), queue_waits)
    state["total_llm_exec_ms"] = max(state.get("total_llm_exec_ms", 0.0), exec_times)
    
    # Now let's see if we have new completed steps.
    # A step is completed when all its chunks succeed and we run ScoringHook on its matrix block.
    # In backend_debug.log, let's find if there are any new [Chunk Success] lines.
    # E.g. [Chunk Success] Step sr_87f408aeee64462f | Prompt tokens: ...
    # Wait, we saw that sr_87f408aeee64462f has completed 2 calls out of 3, so it is not in [Chunk Success] yet.
    # But wait, are there any other completed steps?
    # Let's search log for "[Chunk Success]" and print them.
    chunk_successes = re.findall(
        r"\[Chunk Success\] Step ([a-zA-Z0-9_]+) \| Prompt tokens: (\d+) \| Completion tokens: (\d+) \| Cached: (\d+) \| Cost: \$(\d+\.\d+)",
        log_content
    )
    
    # Also find step durations.
    # We can match step start (Compiling map-reduce for step '...') and finish (3-Tier Score '...' or ScoringHook finished)
    # Let's find each step's start and end timestamps.
    lines = log_content.splitlines()
    step_start_times = {}
    step_end_times = {}
    
    for line in lines:
        t_match = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line)
        if not t_match:
            continue
        t_str = t_match.group(1)
        
        m = re.search(r"Compiling map-reduce for step '([a-zA-Z0-9_]+)'", line)
        if m:
            step_start_times[m.group(1)] = t_str
            
        m = re.search(r"Triggered for step '([a-zA-Z0-9_]+)'", line)
        if m:
            step_start_times[m.group(1)] = t_str
            
        # Scoring completed for matrix block
        m = re.search(r"3-Tier Score '([a-zA-Z0-9_]+)'", line)
        if m:
            blk_id = m.group(1)
            # Find the step associated with this block
            # In the log: AtomFlatteningHook Triggered for step 's_id' followed by Flattening Matrix: 'blk_id'
            # Let's do a search backward from this line for Triggered for step
            
    # Associate block with step
    current_step = None
    block_to_step = {}
    for line in lines:
        m = re.search(r"Triggered for step '([a-zA-Z0-9_]+)'", line)
        if m:
            current_step = m.group(1)
        m = re.search(r"Flattening Matrix: '([a-zA-Z0-9_]+)'", line)
        if m and current_step:
            block_to_step[m.group(1)] = current_step
        m = re.search(r"3-Tier Score '([a-zA-Z0-9_]+)'", line)
        if m:
            blk_id = m.group(1)
            if blk_id in block_to_step:
                s_id = block_to_step[blk_id]
                # timestamp of the 3-Tier Score line
                t_match = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line)
                if t_match:
                    step_end_times[s_id] = t_match.group(1)
                    
    # Calculate durations and update state["completed_steps"]
    from datetime import datetime
    for s_id, start_t in step_start_times.items():
        if s_id in step_end_times and s_id not in state["completed_steps"]:
            start_dt = datetime.strptime(start_t, "%Y-%m-%d %H:%M:%S")
            end_dt = datetime.strptime(step_end_times[s_id], "%Y-%m-%d %H:%M:%S")
            duration_ms = (end_dt - start_dt).total_seconds() * 1000.0
            
            # Find tokens/cost for this step from chunk success logs
            prompt_tokens = 0
            completion_tokens = 0
            cached_tokens = 0
            cost = 0.0
            
            for succ in chunk_successes:
                if succ[0] == s_id:
                    prompt_tokens += int(succ[1])
                    completion_tokens += int(succ[2])
                    cached_tokens += int(succ[3])
                    cost += float(succ[4])
                    
            state["completed_steps"][s_id] = {
                "duration_ms": duration_ms,
                "status": "SUCCESS",
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "cached_tokens": cached_tokens,
                "cost": round(cost, 4)
            }
            
    # Recalculate totals from completed steps
    total_cost = 0.0
    total_prompt = 0
    total_completion = 0
    total_cached = 0
    
    for s_id, data in state["completed_steps"].items():
        if "cost" in data:
            total_cost += data["cost"]
            total_prompt += data["prompt_tokens"]
            total_completion += data["completion_tokens"]
            total_cached += data["cached_tokens"]
            
    state["total_llm_cost"] = round(total_cost, 4)
    state["total_prompt_tokens"] = total_prompt
    state["total_completion_tokens"] = total_completion
    state["total_cached_tokens"] = total_cached
    
    # Save back
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        
    print("State updated successfully!")
    print(json.dumps(state, indent=2))

if __name__ == "__main__":
    update_state()

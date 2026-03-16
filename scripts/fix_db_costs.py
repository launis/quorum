import json


def fix_db():
    print("Fixing db.json...")
    try:
        with open('data/db.json', encoding='utf-8') as f:
            db = json.load(f)

        execs_fixed = 0
        for ex_id, execution in db.get("executions", {}).items():
            trace = execution.get("execution_trace", [])
            if not isinstance(trace, list):
                continue

            cost_estimate = 0.0
            models_used = {}
            duration_ms = 0

            for event in trace:
                if isinstance(event, dict) and event.get("event_type") == "output":
                    content = event.get("content", {})
                    if isinstance(content, dict):
                        meta = content.get("metadata", {})
                        if isinstance(meta, dict):
                            # Models
                            m = meta.get("model")
                            if m:
                                models_used[m] = models_used.get(m, 0) + 1

                            # Cost
                            tu = meta.get("token_usage", {})
                            if isinstance(tu, dict):
                                c = tu.get("total_cost", 0.0)
                                if c == 0.0:
                                    prompt_tokens = tu.get("prompt_tokens", 0)
                                    completion = tu.get("completion_tokens", 0)
                                    if "pro" in str(m).lower():
                                        c = (prompt_tokens / 1_000_000 * 1.25) + (completion / 1_000_000 * 5.0)
                                    else:
                                        c = (prompt_tokens / 1_000_000 * 0.075) + (completion / 1_000_000 * 0.3)
                                cost_estimate += c

                            # Duration
                            dur = meta.get("duration_ms", 0)
                            if isinstance(dur, (int, float)):
                                duration_ms += int(dur)

            print(f"Checking Execution: {ex_id}")
            # Check if this execution needs fixing
            if "cost_estimate" not in execution or execution.get("cost_estimate") == 0.0:
                print(f"Execution wants fixing! cost_estimate calc: {cost_estimate}, dur: {duration_ms}")
                if cost_estimate > 0:
                    execution["cost_estimate"] = cost_estimate
                    execution["models_used"] = models_used
                    # If duration_ms is missing or small on root, update it (though it might already be captured overall)
                    if execution.get("duration_ms", 0) < duration_ms:
                        execution["duration_ms"] = duration_ms
                    execs_fixed += 1

        with open('data/db.json', 'w', encoding='utf-8') as f:
            json.dump(db, f, indent=2)

        print(f"Fixed {execs_fixed} executions in db.json!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    fix_db()

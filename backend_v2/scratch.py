import json

try:
    with open("data/db_v2.json", encoding="utf-8") as f:
        db = json.load(f)
    executions = db.get("executions", {})
    exe_id = "exe_7330f7fdf4eb402f9e6fa919f168299c"
    exe = executions.get(exe_id)
    if exe:
        print("Execution found!")
        for trace in exe.get("execution_trace", []):
            if trace.get("event_type") == "step_completed":
                res = trace.get("result", {})
                print(
                    f"Step: {trace.get('step_id')} - Score: {res.get('score')} "
                    f"- Reasoning: {str(res.get('reasoning'))[:200]}"
                )

        print("Syntheses:")
        for k, v in exe.get("profile_syntheses", {}).items():
            print(f"Synthesis {k}: {str(v)[:500]}")
    else:
        print("Execution not found in local db.")
except Exception as e:
    print("Error:", e)

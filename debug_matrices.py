import json
from pprint import pprint

with open(r"c:\src\quorum\data\db_v2.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Find the execution that failed
executions = data.get("executions", {})
print(f"Total executions: {len(executions)}")

# Sort by completion date or just get the latest
latest_exec = sorted(executions.values(), key=lambda x: x.get("completed_at") or x.get("started_at", ""), reverse=True)[0]

print(f"Execution ID: {latest_exec['id']}")
print(f"Status: {latest_exec['status']}")

# Iterate over traces and check the payload
for trace in latest_exec.get("execution_trace", []):
    if trace.get("event_type") == "output":
        step_id = trace.get("step_name")
        content = trace.get("content", {})
        print(f"\n--- STEP: {step_id} ---")
        if "_evaluative_matrices" in content:
            print("_evaluative_matrices FOUND:")
            pprint(content["_evaluative_matrices"])
        else:
            print("NO _evaluative_matrices")
            print("Keys in payload:", list(content.keys()))

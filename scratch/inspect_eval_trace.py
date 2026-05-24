import json
import os

trace_path = "data/files/executions/exe_3fd8226676154108a50a644f621ad7fe/execution_trace.json"

with open(trace_path, "r", encoding="utf-8") as f:
    steps = json.load(f)

print(f"Loaded {len(steps)} steps.")

for idx, step in enumerate(steps):
    step_name = step.get("step_name")
    event_type = step.get("event_type")
    content = step.get("content", {})
    print(f"Step {idx}: name={step_name}, type={event_type}")
    
    if isinstance(content, dict) and "evaluations" in content:
        evals = content["evaluations"]
        print(f"  Found 'evaluations' list with {len(evals)} items.")
        if evals:
            first_eval = evals[0]
            print("  First evaluation item keys and values:")
            for k, v in first_eval.items():
                print(f"    - {k}: {v}")
            break

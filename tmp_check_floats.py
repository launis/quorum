import json

with open("c:/src/quorum/data/db_v2.json", "r", encoding="utf-8") as f:
    db = json.load(f)

# Get the last execution
executions = list(db["executions"].values())
last_exec = executions[-1]

print("--- RAW MATRIX VALUES FROM DB ---")
results = last_exec.get("results", {})
for step_id, step_data in results.items():
    if not isinstance(step_data, dict):
        continue
    
    # Check both the root of step_data and potentially nested outputs
    for k, v in step_data.items():
        if k.startswith("matrix"):
            print(f"{step_id} -> {k} = {v} (Type: {type(v).__name__})")
            
        elif isinstance(v, dict):
            for sub_k, sub_v in v.items():
                if sub_k.startswith("matrix"):
                     print(f"{step_id} -> {sub_k} = {sub_v} (Type: {type(sub_v).__name__})")

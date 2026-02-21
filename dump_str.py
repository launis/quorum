import json

with open("data/db.json", "r", encoding="utf-8") as f:
    data = json.load(f)

executions = data.get("executions", {})
latest_id = list(executions.keys())[-1]
latest_exec = executions[latest_id]

print(f"ID: {latest_id}")
print(f"Top-level keys: {list(latest_exec.keys())}")
if "results" in latest_exec:
    print(f"results keys: {list(latest_exec['results'].keys())}")
    for k, v in latest_exec['results'].items():
        if isinstance(v, dict):
            print(f"  results[{k}] keys: {list(v.keys())}")
        else:
            print(f"  results[{k}]: type {type(v)}")

import pprint
print("\nFirst 500 chars of latest exec:")
pprint.pprint(latest_exec, depth=3, compact=True)

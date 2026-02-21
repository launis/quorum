import json

def find_keys(obj, target_keys, path=""):
    found = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            current_path = f"{path}.{k}" if path else k
            if any(tk in k.lower() for tk in target_keys):
                found.append((current_path, v))
            found.extend(find_keys(v, target_keys, current_path))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            current_path = f"{path}[{i}]"
            found.extend(find_keys(v, target_keys, current_path))
    return found

with open("data/db.json", "r", encoding="utf-8") as f:
    data = json.load(f)

executions = data.get("executions", {})
if not executions:
    print("No executions found.")
    exit(0)

latest_id = list(executions.keys())[-1]
latest_exec = executions[latest_id]
print(f"Scanning Execution ID: {latest_id}")

targets = ["usage", "token", "cost"]
results = find_keys(latest_exec, targets)

for path, value in results:
    # Print path and a snippet of the value
    val_str = str(value)
    if len(val_str) > 100:
        val_str = val_str[:100] + "..."
    print(f"{path}: {val_str}")

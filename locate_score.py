
import json

db_path = r"c:\src\quorum\data\db.json"
exec_key = "14"

def find_in_dict(d, path=""):
    for k, v in d.items():
        curr_path = f"{path}.{k}"
        if isinstance(v, dict):
            find_in_dict(v, curr_path)
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    find_in_dict(item, f"{curr_path}[{i}]")
                elif "83.3" in str(item):
                    print(f"Found at {curr_path}[{i}]: {item}")
        elif "83.3" in str(v):
            print(f"Found at {curr_path}: {v}")

try:
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    execution = data.get("executions", {}).get(exec_key)
    find_in_dict(execution)

except Exception as e:
    print(f"Error: {e}")

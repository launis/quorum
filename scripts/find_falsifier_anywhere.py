import json
import os

DB_PATH = os.path.join("data", "db.json")

def find_falsifier(obj, path=""):
    if isinstance(obj, dict):
        if obj.get("id") == "step_falsifier":
            task_key = obj.get("task_key", "UNKNOWN")
            agent_class = obj.get("metadata", {}).get("agent_class", "N/A")
            print(f"FOUND at path: {path} | task_key: {task_key} | agent_class: {agent_class}")
        
        for k, v in obj.items():
            new_path = f"{path}.{k}" if path else k
            find_falsifier(v, new_path)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            new_path = f"{path}[{i}]"
            find_falsifier(item, new_path)


FILES_TO_CHECK = [
    os.path.join("data", "db.json"),
    os.path.join("backend", "seed", "seed_data.json")
]

def main():
    for db_path in FILES_TO_CHECK:
        if not os.path.exists(db_path):
            print(f"File not found: {db_path}")
            continue

        print(f"\nSearching for 'step_falsifier' in {db_path}...")
        try:
            with open(db_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error reading {db_path}: {e}")
            continue
        
        find_falsifier(data)

if __name__ == "__main__":
    main()

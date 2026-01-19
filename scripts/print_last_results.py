import json
import sys
import os

DB_PATH = 'c:/src/quorum/data/db.json'

def main():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found at {DB_PATH}")
        return

    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        target_table = None
        # Look for 'executions' key directly
        if "executions" in data:
            target_table = data["executions"]
        # Fallback: Look inside _default if TinyDB formatted without named tables
        elif "_default" in data:
            # Check a sample item to see if it looks like an execution
            sample_key = next(iter(data["_default"]))
            sample_item = data["_default"][sample_key]
            if "results" in sample_item or "status" in sample_item:
                 target_table = data["_default"]
        
        if not target_table:
            print(f"Could not locate executions table. Available keys: {list(data.keys())}")
            return

        # Sort keys to find the last one. Keys are usually strings "1", "2".
        sorted_keys = sorted(target_table.keys(), key=lambda x: int(x) if x.isdigit() else float('inf'))
        
        if not sorted_keys:
            print("No executions found in the table.")
            return

        last_key = sorted_keys[-1]
        last_execution = target_table[last_key]
        
        print(f"ID: {last_execution.get('id', 'N/A')} (Key: {last_key})")
        
        results = last_execution.get("results", {})
        print(json.dumps(results, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"Error processing database: {e}")

if __name__ == "__main__":
    main()

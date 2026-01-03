
import json

DB_PATH = "c:/Users/risto/OneDrive/quorum/data/db.json"

def inspect_exec():
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        executions = data.get('executions', {})
        if not executions:
            print("No executions.")
            return

        if isinstance(executions, list):
            vals = executions
        else:
            vals = list(executions.values())
        
        last_exec = vals[-1]
        
        print(f"Total executions: {len(vals)}")
        print(f"Last Execution Status: {last_exec.get('status')}")
        print(f"Error: {last_exec.get('error')}")
        
        result = last_exec.get('result', {})
        keys = list(result.keys())
        print(f"Result Key Count: {len(keys)}")
        print("Keys:", json.dumps(keys))
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_exec()

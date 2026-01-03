
import json

DB_PATH = "c:/Users/risto/OneDrive/quorum/data/db.json"

def inspect_exec_state():
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        executions = data.get('executions', {})
        if not executions: return
        
        if isinstance(executions, list):
            last_exec = executions[-1]
        else:
            vals = list(executions.values())
            last_exec = vals[-1]
            
        print(f"Steps List: {last_exec.get('steps')}")
        print(f"Current Step Index: {last_exec.get('current_step_index')}")
        print(f"Result Keys: {list(last_exec.get('result', {}).keys())}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_exec_state()


import json

DB_PATH = "c:/Users/risto/OneDrive/quorum/data/db.json"

def list_result_keys():
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        executions = data.get('executions', {})
        if not executions: return

        if isinstance(executions, list):
            last_exec = executions[-1]
        else:
            keys = sorted(list(executions.keys()), key=lambda x: int(x) if x.isdigit() else x)
            last_exec = executions[keys[-1]]

        result = last_exec.get('result', {})
        print(f"Execution ID: {last_exec.get('id')}")
        print(f"Workflow ID: {last_exec.get('workflow_id')}")
        print(f"Result Keys found: {list(result.keys())}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_result_keys()

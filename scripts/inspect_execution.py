
import json
import sys
import os
# Adjust path to include project root
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.models.state import WorkflowState
from pydantic import ValidationError

def inspect_execution(execution_id):
    db_path = os.path.join(os.path.dirname(__file__), '../data/db.json')
    
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Database not found at {db_path}")
        return

    # TinyDB Structure: {"_default": {"1": {...}}} if generic, OR
    # {"executions": {"1": {...}}} if table specific.
    # Wrapper uses `db.table(self._name)`, so top level key is usually `_default` unless `default_table_name` changed?
    # No, TinyDB by default uses `_default` table. BUT `TinyDBTable` uses `db.table(self._name)`.
    # So the top level keys in `db.json` should be the table names (e.g. `executions`, `workflows`, etc).
    # And inside that, it is `{"doc_id": record}`.
    
    executions_table = data.get('executions', {})
    
    target_record = None
    
    print(f"Searching in 'executions' table with {len(executions_table)} records...")
    
    for key, record in executions_table.items():
        if isinstance(record, dict) and record.get('id') == execution_id:
            target_record = record
            print(f"Found record at key: {key}")
            break
            
    if not target_record:
        print(f"Execution {execution_id} not found in 'executions' table.")
        # Fallback search entire DB
        # for table_name, table_data in data.items():
        #     if isinstance(table_data, dict):
        #         for k, v in table_data.items():
        #             if isinstance(v, dict) and v.get('id') == execution_id:
        #                 print(f"Found in table '{table_name}' key '{k}'")
        #                 target_record = v
        #                 break
        if not target_record:
            return

    results = target_record.get('results')
    
    if not results:
        print("Results field is missing or empty.")
        return
        
    print(f"Results Type: {type(results)}")
    
    if isinstance(results, dict):
        print("Attempting to inflate WorkflowState...")
        try:
            # Pydantic V2
            ws = WorkflowState.model_validate(results)
            print("SUCCESS: Inflated WorkflowState correctly.")
        except ValidationError as e:
            print("FAILURE: Pydantic Validation Error:")
            print(e)
        except Exception as e:
             print(f"FAILURE: Other Error: {e}")
    else:
        print("Results is not a dict.")

if __name__ == "__main__":
    inspect_execution("a7723aa4-aa16-4377-a50a-ac9a90dc2c5e") # Use the failed ID

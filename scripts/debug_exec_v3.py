
import json
import sys

db_path = "c:/src/quorum/data/db.json"
exec_id = "ff5f84fb-ed55-4648-9c63-fbfa405dd96e"

output_file_path = "c:/src/quorum/step_guard_full_output.json"

try:
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    target_exec = None
    
    # Locate execution
    if "executions" in data:
        executions = data["executions"]
        if isinstance(executions, dict):
             for key, record in executions.items():
                if record.get("id") == exec_id or record.get("execution_id") == exec_id:
                    target_exec = record
                    break
    elif "_default" in data: 
        for key, record in data["_default"].items():
             if record.get("id") == exec_id or record.get("execution_id") == exec_id:
                target_exec = record
                break
    
    if not target_exec:
        print(f"Execution {exec_id} not found.")
        sys.exit(1)
        
    print(f"Found execution: {target_exec.get('id')}")
    
    results = target_exec.get("results", {})
    
    print("\n--- STEP NAMES FOUND ---")
    
    step_guard_res = None
    
    iter_items = []
    if isinstance(results, list):
        iter_items = results
    elif isinstance(results, dict):
        iter_items = results.values()
        
    for res in iter_items:
        if isinstance(res, str):
            try:
                res = json.loads(res)
            except:
                continue
        
        # Check various possible keys for step name
        s_name = res.get("step_name") or res.get("name") or res.get("id")
        print(f"Found step: {s_name}")
        
        if s_name == "step_guard":
            step_guard_res = res
            
    if step_guard_res:
        print("\nSUCCESS: Found step_guard!")
        with open(output_file_path, "w", encoding="utf-8") as out_f:
            json.dump(step_guard_res, out_f, indent=2)
        print(f"Saved full output to {output_file_path}")
        
        # Analyze inputs
        inputs = step_guard_res.get("input_data")
        print(f"\nInputs keys: {inputs.keys() if isinstance(inputs, dict) else inputs}")
    else:
        print("\nFAILURE: step_guard not found.")

except Exception as e:
    print(f"Error: {e}")

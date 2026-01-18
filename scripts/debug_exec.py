
import json
import sys

db_path = "c:/src/quorum/data/db.json"
exec_id = "ff5f84fb-ed55-4648-9c63-fbfa405dd96e"

try:
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    target_exec = None
    
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
    
    results = target_exec.get("results", [])
    print(f"Results type: {type(results)}")

    step_guard_result = None
    
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
                
        if res.get("step_name") == "step_guard":
            step_guard_result = res
            break
            
    if step_guard_result:
        print("\n--- STEP_GUARD INPUT ---")
        print(json.dumps(step_guard_result.get("input_data"), indent=2))
        print("\n--- STEP_GUARD OUTPUT ---")
        # Save output to a file for better inspection
        output_data = step_guard_result.get("output_data")
        print(json.dumps(output_data, indent=2))
        
        with open("c:/src/quorum/step_guard_output.json", "w", encoding="utf-8") as f:
            json.dump(step_guard_result, f, indent=2)
        print("\nFull step_guard result saved to c:/src/quorum/step_guard_output.json")
        
    else:
        print("step_guard result not found in execution.")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

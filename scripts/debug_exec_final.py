
import json
import sys

db_path = "c:/src/quorum/data/db.json"
exec_id = "ff5f84fb-ed55-4648-9c63-fbfa405dd96e"
out_path = "c:/src/quorum/guard_result.json"

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
        
    results = target_exec.get("results", {})
    
    iter_items = []
    if isinstance(results, list):
        iter_items = results
    elif isinstance(results, dict):
        iter_items = results.values()
        
    found = False
    for res in iter_items:
        if isinstance(res, str):
            try:
                res = json.loads(res)
            except:
                continue
        
        # Check metadata.agentti
        meta = res.get("metadata", {})
        agentti = meta.get("agentti")
        
        if agentti == "GuardAgent":
            found = True
            print("FOUND GuardAgent result!")
            
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(res, f, indent=2)
            print(f"Saved to {out_path}")
            
            # Print input data summary
            inp = res.get("input_data")
            print("\n--- INPUT DATA ---")
            if isinstance(inp, dict):
                print(json.dumps(inp, indent=2))
            else:
                print(str(inp))
            
            print("\n--- OUTPUT DATA ---")
            outp = res.get("output_data") or res.get("data")
            if isinstance(outp, dict):
                 print(json.dumps(outp, indent=2))
            else:
                 print(str(outp))
            
            break
            
    if not found:
        print("GuardAgent result not found.")

except Exception as e:
    print(f"Error: {e}")

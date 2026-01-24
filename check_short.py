
import json

db_path = r"c:\src\quorum\data\db.json"
target_id_partial = "7f12c342"

try:
    with open(db_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    executions = data.get("executions", {})
    count = 0 
    for eid, details in executions.items():
        if target_id_partial in details.get("id", ""):
            count += 1
            res = details.get("results", {}).get("step_results", {})
            
            ov = res.get("step_overseer")
            ar = res.get("step_archivist")
            
            print(f"ID: {details.get('id')}")
            print(f"Over: {'DONE' if ov else 'MISSING'}")
            print(f"Arch: {'DONE' if ar else 'MISSING'}")
            
    if count == 0:
        print("No match.")

except Exception as e:
    print(f"ERR: {e}")

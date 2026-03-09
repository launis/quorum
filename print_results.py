import json

def main():
    with open('c:/src/quorum/data/db_v2.json', 'r', encoding='utf-8') as f:
        db = json.load(f)
        
    execs = db.get("executions", {})
    if not execs:
        print("No executions found.")
        return
        
    last_id = list(execs.keys())[-1]
    last_exec = execs[last_id]
    
    print(f"Execution ID: {last_id}")
    print(f"Status: {last_exec.get('status')}")
    print(f"Duration: {last_exec.get('duration_ms', 0) / 1000} seconds")
    print(f"Models Used: {last_exec.get('models_used')}")
    print("-" * 40)
    
    results = last_exec.get("results", {})
    for step_id, step_res in results.items():
        print(f"STEP: {step_id}")
        
        # If it's a prompt-block evaluation, it might be a dictionary with matrix keys
        if isinstance(step_res, dict):
            for key, val in step_res.items():
                if isinstance(val, dict):
                    # Usually looks like {"score": 3, "justification": "..."}
                    score = val.get("score")
                    just = val.get("justification") or val.get(f"{key}_justification")
                    if score is not None:
                        print(f"  Matrix: {key}\n   => Score: {score}")
                        if just:
                            print(f"   => Justification: {just}")
                        continue
                print(f"  {key}: {val}")
        elif isinstance(step_res, list):
            print(f"  [List result length: {len(step_res)}]")
            for item in step_res[:2]: # preview first 2
                print(f"  - {item}")
        else:
            print(f"  {step_res}")
            
        print("-" * 40)

if __name__ == "__main__":
    main()

import json
import glob
import os

def check_trace(path):
    print(f"\n=================== Checking trace: {path} ===================")
    if not os.path.exists(path):
        print("Path does not exist.")
        return
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Total events/steps in trace: {len(data)}")
    
    step_names = [step.get("step_name") for step in data]
    print("Steps in this trace:", step_names)
    
    found_variance = False
    for step in data:
        content_str = json.dumps(step.get("content", {}))
        if "variance" in content_str.lower():
            print(f"Found 'variance' in step content of '{step.get('step_name')}'!")
            found_variance = True
            
        gvars = step.get("global_context_vars", {})
        if gvars and isinstance(gvars, dict):
            gvars_str = json.dumps(gvars)
            if "variance" in gvars_str.lower():
                print(f"Found 'variance' in global_context_vars of '{step.get('step_name')}'!")
                found_variance = True
                
    if not found_variance:
        print("No variance found in this trace.")

if __name__ == "__main__":
    for d in glob.glob("data/files/executions/exe_*"):
        path = os.path.join(d, "execution_trace.json")
        check_trace(path)

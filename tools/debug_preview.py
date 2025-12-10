import os
import sys
import traceback

# Add current directory to path so we can import backend
sys.path.append(os.getcwd())

from backend.core.engine import WorkflowEngine

def debug():
    try:
        print("Initializing WorkflowEngine...", flush=True)
        # Assuming run from root (c:\Users\risto\OneDrive\quorum)
        db_path = os.path.join(os.getcwd(), 'data', 'db.json')
        print(f"DB Path: {db_path}", flush=True)
        
        engine = WorkflowEngine(db_path)
        
        print("Calling preview_step_prompt('step_1') for User Prompt Check...", flush=True)
        result1 = engine.preview_step_prompt("step_1")
        print("Step 1 User Prompt:", result1.get('user_prompt', 'MISSING')[:100] + "...", flush=True)

        print("Calling preview_step_prompt('step_2') for User Prompt Check...", flush=True)
        result2 = engine.preview_step_prompt("step_2")
        print("Step 2 User Prompt:", result2.get('user_prompt', 'MISSING')[:100] + "...", flush=True)

        for i in range(3, 10):
            step_id = f"step_{i}"
            print(f"Calling preview_step_prompt('{step_id}') for User Prompt Check...", flush=True)
            res = engine.preview_step_prompt(step_id)
            print(f"Step {i} User Prompt:", res.get('user_prompt', 'MISSING')[:100] + "...", flush=True)
        

        
    except Exception:
        traceback.print_exc(file=sys.stdout)
        sys.stdout.flush()

if __name__ == "__main__":
    debug()

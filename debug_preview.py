import os
import sys
import traceback

# Add current directory to path so we can import backend
sys.path.append(os.getcwd())

from backend.engine import WorkflowEngine

def debug():
    try:
        print("Initializing WorkflowEngine...", flush=True)
        # Assuming run from root (c:\Users\risto\OneDrive\quorum)
        db_path = os.path.join(os.getcwd(), 'data', 'db.json')
        print(f"DB Path: {db_path}", flush=True)
        
        engine = WorkflowEngine(db_path)
        
        print("Calling preview_step_prompt('STEP_1_GUARD')...", flush=True)
        result = engine.preview_step_prompt("STEP_1_GUARD")
        
        print("Result:", flush=True)
        print(result, flush=True)
        
    except Exception:
        traceback.print_exc(file=sys.stdout)
        sys.stdout.flush()

if __name__ == "__main__":
    debug()

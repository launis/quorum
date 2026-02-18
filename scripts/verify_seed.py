
import json

SEED_PATH = r"c:\src\quorum\backend\seed\seed_data.json"

def verify_seed():
    print("--- VERIFYING SEED DATA ---")
    try:
        with open(SEED_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check required keys
        required = ["knowledge_base", "components", "dimensions", "workflows", "steps", "system_config", "users", "organizations"]
        forbidden = ["execution_records", "workflow_executions"]
        
        all_good = True
        
        for r in required:
            if r in data:
                count = len(data[r]) if isinstance(data[r], (list, dict)) else 1
                if isinstance(data[r], dict): count = len(data[r].keys())
                print(f"[PASS] Found '{r}': {count} items")
                
                if r == "knowledge_base" and count < 100:
                    print(f"[WARN] 'knowledge_base' seems too small ({count}). Expected ~466.")
                    all_good = False
            else:
                print(f"[FAIL] Missing '{r}'")
                all_good = False
                
        for f in forbidden:
            if f in data:
                print(f"[FAIL] Found forbidden key '{f}'")
                all_good = False
            else:
                print(f"[PASS] Forbidden key '{f}' absent")
                
        if all_good:
            print("\nVERIFICATION PASSED: Seed data is valid.")
        else:
            print("\nVERIFICATION FAILED: Issues detected.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_seed()

import json
import os

DB_PATH = r"c:\Users\risto\OneDrive\quorum\backend\database\db_mock.json"

def main():
    if not os.path.exists(DB_PATH):
        print("DB not found")
        return

    with open(DB_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    executions = data.get("executions", {})
    if not executions:
        print("No executions")
        return

    # Sort executions by start_time
    sorted_executions = sorted(
        executions.values(),
        key=lambda x: x.get("start_time", ""),
        reverse=True
    )
    latest = sorted_executions[0]
    print(f"Latest ID: {latest.get('execution_id')}")
    print(f"Status: {latest.get('status')}")
    print(f"Failed Step: {latest.get('failed_step')}")
    print(f"Error: {latest.get('error')}")
    
    result = latest.get("result", {})
    
    print(f"\nKeys in 'latest': {list(latest.keys())}")
    print(f"Keys in 'latest[result]': {list(result.keys())}")
    
    step_coach = result.get("step_coach") or latest.get("step_coach")
    
    if step_coach:
        print("\nFOUND step_coach")
        if isinstance(step_coach, dict):
            print("Keys:", list(step_coach.keys()))
            items = step_coach.get('kehityskohteet_konkreettisesti')
            print("Kehityskohteet count:", len(items) if items else 0)
            if items:
                 print("First Item:", items[0] if isinstance(items, list) and len(items) > 0 else items)
        else:
            print(f"Step Coach Data (Type {type(step_coach)}): {step_coach}")
            
    else:
        print("\nMISSING step_coach")

if __name__ == "__main__":
    main()

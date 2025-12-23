
import json
from backend.database.wrapper import TinyDBClient # Use direct client
from backend.database.repository import TinyDBRepository

def inspect_latest_execution():
    client = TinyDBClient("backend/database/db_mock.json") # Positional argument
    repo = TinyDBRepository(client)
    
    # Get all executions directly from table to sort by timestamp if needed, 
    # but repository might not expose 'get_all'. We'll use a known ID if possible or peek into table.
    # Since we just ran test_engine.py, let's try to find that specific one or just list the last inserted.
    
    print("Reading DB...")
    table = client.table("executions")
    all_execs = table.all()
    
    if not all_execs:
        print("No executions found.")
        return

    # Sort by start_time (assuming ISO string)
    latest = sorted(all_execs, key=lambda x: x.get('start_time', ''), reverse=True)[0]
    
    print(f"\nLast Execution ID: {latest['execution_id']}")
    
    result = latest.get('result', {})
    if not result:
        print("No result stored yet.")
        return

    print("\n--- TOP LEVEL KEYS ---")
    print(list(result.keys()))
    
    if "Raw_Steps" in result:
        print("\n--- RAW STEPS KEYS (Filtered) ---")
        print(list(result["Raw_Steps"].keys()))
        
        # Check depth / nulls for a sample
        if "step_judge" in result["Raw_Steps"]:
             print("\n--- SAMPLE: step_judge (No Nulls Check) ---")
             print(json.dumps(result["Raw_Steps"]["step_judge"], indent=2, ensure_ascii=False)[:500] + "...")
    else:
        print("\nWARNING: Raw_Steps missing!")

if __name__ == "__main__":
    inspect_latest_execution()

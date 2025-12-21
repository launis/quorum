import os
os.environ['DB_PATH'] = r'c:\Users\risto\OneDrive\quorum\data\db.json'
import sys
sys.path.append(os.getcwd())
from backend.database.wrapper import get_db_client
from backend.database.repository import TinyDBRepository

try:
    db = get_db_client()
    repo = TinyDBRepository(db)
    
    print("--- STEPS IN DB ---")
    steps = repo.get_all_steps()
    step_ids = []
    for s in steps:
        print(f"ID: '{s.get('id')}' | Comp: '{s.get('component')}'")
        step_ids.append(s.get('id'))
        
    print("\n--- WORKFLOW MAPPING ---")
    wfs = repo.get_all_workflows()
    if wfs:
        for w in wfs:
            print(f"WF ID: {w.get('id')}")
            m = w.get('default_model_mapping', {})
            print(f"Mapping Keys: {list(m.keys())}")
            
            # Check intersection
            common = set(step_ids).intersection(set(m.keys()))
            print(f"Matching Keys Count: {len(common)} / {len(step_ids)}")
            if len(common) < len(step_ids):
                print("MISMATCH DETECTED!")
    else:
        print("No Workflows")

except Exception as e:
    print(f"Error: {e}")

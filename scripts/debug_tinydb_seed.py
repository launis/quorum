from tinydb import TinyDB, Query
import json
import os

DB_PATH = 'data/db.json'
TEST_ID = 'debug_workflow_123'

def debug_tinydb():
    print(f"--- Debugging TinyDB Persistence at {DB_PATH} ---")
    
    # 1. State Before
    if os.path.exists(DB_PATH):
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            raw = f.read()
            print(f"File Size Before: {len(raw)} bytes")
            # print(f"Raw Content Head: {raw[:200]}")

    # 2. Mimic Seeder Logic
    try:
        db = TinyDB(DB_PATH, encoding="utf-8")
        # db.drop_tables() # skip drop to see if we can append
        
        table = db.table("workflows")
        print(f"Current rows in table: {len(table.all())}")
        
        test_wf = {
            "id": TEST_ID,
            "name": "Debug Workflow",
            "description": "Test entry"
        }
        
        print("Upserting test workflow...")
        table.upsert(test_wf, Query().id == TEST_ID)
        
        # 3. Verify Immediately via Instance
        after_all = table.all()
        print(f"Rows in table instance after upsert: {len(after_all)}")
        found = table.search(Query().id == TEST_ID)
        print(f"Found via instance: {len(found)}")
        
        db.close()
        
    except Exception as e:
        print(f"CRITICAL ERROR during TinyDB ops: {e}")

    # 4. Verify via Raw File Read
    print("--- Verifying via Raw JSON Read ---")
    try:
        with open(DB_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            table_data = data.get('workflows', {})
            print(f"Keys in JSON root: {list(data.keys())}")
            print(f"Type of 'workflows': {type(table_data)}")
            if isinstance(table_data, dict):
                print(f"Count (dict keys): {len(table_data)}")
            elif isinstance(table_data, list):
                print(f"Count (list items): {len(table_data)}")
            
            # Check for our ID
            is_present = str(TEST_ID) in str(data)
            print(f"Is '{TEST_ID}' present in raw file text? {is_present}")
            
    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    debug_tinydb()

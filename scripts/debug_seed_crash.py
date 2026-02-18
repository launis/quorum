
import json
import os
import sys
import traceback
from tinydb import TinyDB, Query

SEED_PATH = r"c:\src\quorum\backend\seed\seed_data.json"
DB_PATH = r"c:\src\quorum\data\db.json"

def debug_seed():
    print("--- DEBUG SEED ---")
    try:
        if not os.path.exists(SEED_PATH):
            print(f"Seed file not found: {SEED_PATH}")
            return

        with open(SEED_PATH, encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Loaded seed data. Keys: {list(data.keys())}")
        
        # Test Workflow Loop
        print("\nTesting Workflows...")
        workflows = data.get("workflows", [])
        print(f"Workflow count: {len(workflows)}")
        for idx, wf in enumerate(workflows):
            try:
                wf_id = wf.get("id")
                # Simulate Query access
                q = Query().id == wf_id
                print(f"  [{idx}] ID: {wf_id} - Query OK")
            except Exception as e:
                print(f"  [{idx}] FAILED: {e}")
                traceback.print_exc()

        # Test KB Loop
        print("\nTesting Knowledge Base...")
        kb = data.get("knowledge_base", [])
        print(f"KB count: {len(kb)}")
        for idx, item in enumerate(kb[:5]):
            try:
                i_id = item.get("id")
                q = Query().id == i_id
                print(f"  [{idx}] ID: {i_id} - Query OK")
            except Exception as e:
                print(f"  [{idx}] FAILED: {e}")
                traceback.print_exc()

        # Test TinyDB Write
        print("\nTesting TinyDB Write...")
        db = TinyDB(DB_PATH, encoding="utf-8")
        wf_table = db.table("workflows")
        
        # Try upserting first workflow
        if workflows:
            print("Upserting first workflow...")
            wf = workflows[0]
            wf_table.upsert(wf, Query().id == wf["id"])
            print("Upsert OK")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_seed()

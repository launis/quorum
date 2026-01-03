
import json
from tinydb import TinyDB, Query

DB_FILE = "data/db.json"

def verify_db():
    print(f"Opening database {DB_FILE}...")
    db = TinyDB(DB_FILE)
    
    # Check system_config
    sys_table = db.table('system_config')
    Config = Query()
    res = sys_table.search(Config.id == 'TASK_GUARD')
    
    if res:
        print(f"✅ Found TASK_GUARD in system_config.")
        content = res[0].get('content', '')
        print(f"Content length: {len(content)}")
        print(f"Snippet: {content[:200]}")
        
        if "ÄLÄ KOSKAAN KOPIOI" in content:
            print("✅ PATCH VERIFIED: 'ÄLÄ KOSKAAN KOPIOI' is present.")
        else:
            print("❌ PATCH FAILED: 'ÄLÄ KOSKAAN KOPIOI' NOT found.")
    else:
        print("❌ TASK_GUARD not found in system_config table.")
        
        # Check components table
        comp_table = db.table('components')
        res2 = comp_table.search(Config.id == 'TASK_GUARD')
        if res2:
             print(f"⚠️ Found TASK_GUARD in 'components' table instead.")
             content = res2[0].get('content', '')
             if "ÄLÄ KOSKAAN KOPIOI" in content:
                print("✅ PATCH VERIFIED (in components table).")
             else:
                print("❌ PATCH FAILED (in components table).")

if __name__ == "__main__":
    verify_db()

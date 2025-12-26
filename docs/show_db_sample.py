from tinydb import TinyDB
import sys
import os

def show_sample():
    db_path = r'c:\Users\risto\OneDrive\quorum\data\db.json'
    if not os.path.exists(db_path):
        print(f"Error: DB not found at {db_path}")
        return

    db = TinyDB(db_path)
    kb = db.table('knowledge_base')
    
    items = kb.all()
    refs = [i for i in items if i.get('type') == 'reference']
    claims = [i for i in items if i.get('type') == 'claim']
    
    print(f"--- DATABASE REPORT ---")
    print(f"Path: {db_path}")
    print(f"Total Items: {len(items)}")
    print(f"References: {len(refs)}")
    print(f"Claims: {len(claims)}")
    print("\n--- SAMPLE REFERENCES (Short -> Full) ---")
    for r in refs[:5]:
        print(f"[{r.get('term') or 'N/A'}] -> {r.get('definition')[:100]}...")
        
    print("\n--- SAMPLE CLAIMS ---")
    for c in claims[:5]:
        print(f"Claim: {c.get('term')[:100]}...")
        print(f"Source: {c.get('definition')}")
        print("-" * 20)

if __name__ == "__main__":
    show_sample()

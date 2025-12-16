from tinydb import TinyDB, Query
import os

DB_PATH = os.path.join("data", "db.json")

def check():
    if not os.path.exists(DB_PATH):
        print(f"Database file not found at {DB_PATH}")
        return

    db = TinyDB(DB_PATH)
    kb = db.table('knowledge_base')
    items = kb.all()
    
    concepts = [i for i in items if i.get('type') == 'concept']
    refs = [i for i in items if i.get('type') == 'reference']
    
    print(f"Total Items: {len(items)}")
    print(f"Concepts: {len(concepts)}")
    print(f"References: {len(refs)}")
    
    if len(items) > 0:
        print("Sample Item:", items[0].get('term'))

if __name__ == "__main__":
    check()

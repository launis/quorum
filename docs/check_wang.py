from tinydb import TinyDB
import os

def check_wang():
    p = r'c:\Users\risto\OneDrive\quorum\data\db.json'
    db = TinyDB(p)
    kb = db.table('knowledge_base')
    items = kb.all()
    
    concepts = [i for i in items if i.get('type') == 'concept']
    print(f"Loaded {len(concepts)} concepts from db.json")
    
    found_wang = False
    for c in concepts:
        defn = c.get('definition', '')
        if 'Wang' in defn:
            print(f"\nMATCH: Concept '{c.get('term')}'")
            print(f"Definition Snippet: ...{defn[:150]}...")
            found_wang = True

    if not found_wang:
        print("Wang NOT found in any concept definition.")
        
    found_kahn = False
    for c in concepts:
        defn = c.get('definition', '')
        if 'Kahneman' in defn:
             print(f"\nMATCH: Concept '{c.get('term')}'")
             found_kahn = True
             
    if not found_kahn:
        print("Kahneman NOT found in any concept definition.")

if __name__ == "__main__":
    check_wang()

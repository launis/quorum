from tinydb import TinyDB

def check_vinouma_concepts():
    db_path = r'c:\Users\risto\OneDrive\quorum\data\db.json'
    db = TinyDB(db_path)
    kb = db.table('knowledge_base')
    items = kb.all()
    
    concepts = [i for i in items if i.get('type') == 'concept']
    print(f"Scanning {len(concepts)} concepts...")
    
    found_any = False
    for c in concepts:
        term = c.get('term', '').lower()
        defn = c.get('definition', '').lower()
        if 'vinouma' in term or 'bias' in term:
            print(f"Concept: {c.get('term')}")
            print(f"Def: {c.get('definition')[:100]}...")
            found_any = True
            
    if not found_any:
        print("No concepts with 'vinouma' or 'bias' found.")

if __name__ == "__main__":
    check_vinouma_concepts()

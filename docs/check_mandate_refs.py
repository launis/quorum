from tinydb import TinyDB

def check_mandate_refs():
    db_path = r'c:\Users\risto\OneDrive\quorum\data\db.json'
    db = TinyDB(db_path)
    kb = db.table('knowledge_base')
    items = kb.all()
    refs = [i for i in items if i.get('type') == 'reference']
    
    targets = ['Wang', 'Kahneman', 'Saito', 'Talboy', 'Perez', 'Dufner', 'Tversky']
    found_map = {t: False for t in targets}
    
    print(f"Scanning {len(refs)} references for Mandate authors...")
    
    for r in refs:
        cit = r.get('citation', '').lower()
        short = r.get('short_citation', '').lower()
        for t in targets:
            if t.lower() in cit or t.lower() in short:
                print(f"[FOUND] {t} -> {r.get('short_citation')} | {r.get('citation')[:50]}...")
                found_map[t] = True
                
    print("\nMissing:")
    for t, found in found_map.items():
        if not found:
            print(f"- {t}")

if __name__ == "__main__":
    check_mandate_refs()

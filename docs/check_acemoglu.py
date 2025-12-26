from tinydb import TinyDB

def check_acemoglu():
    p = r'c:\Users\risto\OneDrive\quorum\data\db.json'
    db = TinyDB(p)
    kb = db.table('knowledge_base')
    items = kb.all()
    
    refs = [i for i in items if i.get('type') == 'reference']
    print(f"Scanning {len(refs)} references for 'Acemoglu'...")
    
    found = False
    for r in refs:
        cit = r.get('citation', '')
        short = r.get('short_citation', '')
        # Check specific metadata too just in case
        meta_short = r.get('metadata', {}).get('short_citation', '')
        
        if 'Acemoglu' in cit or 'Acemoglu' in str(short):
             print("\nMATCH FOUND:")
             print(f"  Full Citation: {cit}")
             print(f"  Short Citation: '{short}'")
             print(f"  Meta Short: '{meta_short}'")
             print(f"  ID: {r.get('id')}")
             found = True
             
    if not found:
        print("Acemoglu not found in references.")

if __name__ == "__main__":
    check_acemoglu()

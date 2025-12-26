from tinydb import TinyDB
import os

def check_db_content():
    paths = [
        r'c:\Users\risto\OneDrive\quorum\data\db.json',
        r'c:\Users\risto\OneDrive\quorum\data\db_mock.json'
    ]
    
    targets = ['Wang', 'Kahneman', 'Saito', 'Talboy', 'Perez', 'Dufner', '2023', '2011']
    concepts_to_find = ['auktoriteettivinouma', 'vahvistusvinouma', 'monisanaisuusvinouma', 'myötäilyvinouma', 'bias', 'vinouma']
    
    for p in paths:
        if not os.path.exists(p):
            print(f"Skipping {p} (Not found)")
            continue
            
        print(f"\n--- Checking DB: {os.path.basename(p)} ---")
        try:
            db = TinyDB(p)
            kb = db.table('knowledge_base')
            items = kb.all()
            print(f"Total Items: {len(items)}")
            
            concepts = [i for i in items if i.get('type') == 'concept']
            print(f"Concepts found: {len(concepts)}")
            
            # 1. Search for Concepts
            found_concepts = []
            for c in concepts:
                term = c.get('term', '').lower()
                defn = c.get('definition', '')
                
                # Check if concept matches target list
                match = any(t in term for t in concepts_to_find)
                if match:
                    found_concepts.append(c)
                    
            print(f"Relevant Concepts Found: {len(found_concepts)}")
            
            for c in found_concepts:
                term = c.get('term')
                defn = c.get('definition')
                print(f"  > Concept: '{term}'")
                
                # Check refs in definition
                found_refs = []
                for t in targets:
                    if t in defn:
                        found_refs.append(t)
                
                if found_refs:
                    print(f"    Definition mentions: {found_refs}")
                    # print(f"    Def snippet: {defn[:100]}...")
                else:
                    print(f"    Definition mentions: NONE")

        except Exception as e:
            print(f"Error reading {p}: {e}")

if __name__ == "__main__":
    check_db_content()

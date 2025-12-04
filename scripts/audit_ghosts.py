import json
from pathlib import Path

def audit_db():
    path = Path("data/db_mock.json")
    print(f"Auditing {path}...")
    
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    components = data.get('components', {})
    # TinyDB stores as dict of dicts: {"1": {...}, "2": {...}}
    
    count = 0
    bad_count = 0
    
    print(f"{'INTERNAL_ID':<12} | {'ID':<20} | {'NAME':<30} | {'TYPE'}")
    print("-" * 80)
    
    for internal_id, comp in components.items():
        c_id = comp.get('id')
        c_name = comp.get('name')
        c_type = comp.get('type')
        
        display_id = str(c_id) if c_id is not None else "NONE"
        display_name = str(c_name) if c_name is not None else "NONE"
        
        if c_id is None and c_name is None:
            print(f"{internal_id:<12} | {display_id:<20} | {display_name:<30} | {c_type}  <-- GHOST!")
            bad_count += 1
        elif c_id is None:
             print(f"{internal_id:<12} | {display_id:<20} | {display_name:<30} | {c_type}  (Missing ID)")
        else:
            # print(f"{internal_id:<12} | {display_id:<20} | {display_name:<30} | {c_type}")
            pass
            
        count += 1
        
    print("-" * 80)
    print(f"Total components: {count}")
    print(f"Ghost components (No ID & No Name): {bad_count}")

if __name__ == "__main__":
    audit_db()

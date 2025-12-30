import json

SEED_FILE = "backend/database/seed_data.json"

def find_orphans():
    try:
        with open(SEED_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # 1. Get all Defined Component IDs
        defined_ids = set()
        for c in data.get('components', []):
            defined_ids.add(c['id'])
            
        # 2. Get all Referenced IDs in Steps
        referenced_ids = set()
        steps = data.get('steps', [])
        for step in steps:
            prompts = step.get('execution_config', {}).get('llm_prompts', [])
            for p in prompts:
                referenced_ids.add(p)
                
        # 3. Find Orphans (Defined but not Referenced)
        orphans = defined_ids - referenced_ids
        
        # 4. Check for referenced but undefined (Broken Links)
        broken = referenced_ids - defined_ids
        
        print(f"Total Defined: {len(defined_ids)}")
        print(f"Total Referenced: {len(referenced_ids)}")
        
        if orphans:
            print("\n--- ORPHAN COMPONENTS (Unused) ---")
            for o in sorted(orphans):
                print(f"- {o}")
        else:
            print("\nNo orphan components found.")
            
        if broken:
            print("\n--- BROKEN LINKS (Referenced but Missing) ---")
            for b in sorted(broken):
                print(f"- {b}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_orphans()

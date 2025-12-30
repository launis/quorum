import json

SEED_FILE = r"c:\Users\risto\OneDrive\quorum\data\seed_data.json"

def fix_missing_ids():
    with open(SEED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    components = data.get('components', [])
    fixed_count = 0
    
    for comp in components:
        if 'id' not in comp:
            # Use name as ID if available, otherwise generate one or skip
            if 'name' in comp:
                comp['id'] = comp['name']
                print(f"Fixed component: Added id='{comp['name']}'")
                fixed_count += 1
            else:
                print("WARNING: Component missing both id and name, cannot fix automatically.")
                print(comp)

    if fixed_count > 0:
        with open(SEED_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved seed_data.json with {fixed_count} fixes.")
    else:
        print("No fixes needed.")

if __name__ == "__main__":
    fix_missing_ids()

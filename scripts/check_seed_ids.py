import json

SEED_FILE = r"c:\Users\risto\OneDrive\quorum\data\seed_data.json"

def check_ids():
    with open(SEED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    components = data.get('components', [])
    print(f"Checking {len(components)} components...")
    
    for i, comp in enumerate(components):
        if 'id' not in comp:
            print(f"ERROR: Component at index {i} is missing 'id'!")
            print(json.dumps(comp, indent=2, ensure_ascii=False))
        else:
            # print(f"OK: {comp['id']}")
            pass

    print("Check complete.")

if __name__ == "__main__":
    check_ids()

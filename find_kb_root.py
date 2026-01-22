import json

def find_kb(path, label):
    print(f"--- {label} ({path}) ---")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Root Keys: {list(data.keys())}")
        
        # Check Root "2"
        if "2" in data:
            print(f"Root '2' Found. ID: {data['2'].get('id')}, Type: {data['2'].get('type')}")
        
        # Check inside components
        if 'components' in data:
            comps = data['components']
            if isinstance(comps, dict):
                if '2' in comps:
                    print(f"Components['2'] Found. ID: {comps['2'].get('id')}")
            elif isinstance(comps, list):
                for c in comps:
                    if c.get('id') == 'knowledge_base':
                        print("Found KB in Components List.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_kb('c:/src/quorum/data/db.json', 'DB')
    find_kb('c:/src/quorum/backend/seed/seed_data.json', 'SEED')

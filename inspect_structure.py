import json

def inspect_structure(path, label):
    print(f"--- {label} Structure ({path}) ---")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Root keys: {list(data.keys())}")
        
        for key in ['workflows', 'components', 'system_config']:
            if key in data:
                val = data[key]
                print(f"  {key}: Type={type(val)}")
                if isinstance(val, dict):
                    print(f"    Keys (first 5): {list(val.keys())[:5]}")
                    first_k = list(val.keys())[0] if val else None
                    if first_k:
                        print(f"    Item[{first_k}] ID: {val[first_k].get('id', 'N/A')}")
                elif isinstance(val, list):
                    print(f"    Length: {len(val)}")
                    if val:
                        print(f"    Item[0] ID: {val[0].get('id', 'N/A')}")
            else:
                print(f"  {key}: NOT FOUND")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_structure('c:/src/quorum/data/db.json', 'DB')
    print("")
    inspect_structure('c:/src/quorum/backend/seed/seed_data.json', 'SEED')

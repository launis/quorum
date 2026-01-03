
import json

SEED_FILE = "backend/database/seed_data.json"

def debug_seed_structure():
    print(f"Reading seed data from {SEED_FILE}...")
    with open(SEED_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Root keys: {list(data.keys())}")
    
    # Check inside system_config
    if 'system_config' in data:
        print(f"system_config count: {len(data['system_config'])}")
        found = False
        for item in data['system_config']:
            if item.get('id') == 'TASK_GUARD':
                print("✅ Found TASK_GUARD in system_config!")
                print(f"Content length: {len(item.get('content', ''))}")
                found = True
                break
        if not found:
            print("❌ TASK_GUARD NOT found in system_config.")
            
            # Check other lists just in case
            for key in data.keys():
                if isinstance(data[key], list):
                    for item in data[key]:
                        if isinstance(item, dict) and item.get('id') == 'TASK_GUARD':
                            print(f"✅ Found TASK_GUARD in root key: '{key}'")

if __name__ == "__main__":
    debug_seed_structure()

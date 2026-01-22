import json

def check_sc_kb():
    path = 'c:/src/quorum/backend/seed/seed_data.json'
    print(f"Checking {path}")
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    sc = data.get('system_config', [])
    print(f"System Config Items: {len(sc)}")
    
    found = False
    for i, item in enumerate(sc):
        print(f"Item [{i}] ID: {item.get('id')}, Type: {item.get('type')}")
        if item.get('id') == 'knowledge_base' or item.get('type') == 'knowledge_base':
            found = True
            print("FOUND KB in System Config!")
            
    if not found:
        print("KB NOT FOUND in System Config.")

if __name__ == "__main__":
    check_sc_kb()


import json

file_path = r'c:\Users\risto\OneDrive\quorum\data\db.json'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    system_config = data.get('system_config', {})
    print("System Config Keys:", system_config.keys())
    
    # Iterate to find knowledge base or similar
    for key, val in system_config.items():
        print(f"\n--- Config Item {key} ---")
        print(f"Type: {val.get('type')}")
        if val.get('type') == 'knowledge_base':
            print("Knowledge Base Found!")
            print(json.dumps(val, indent=2))

except Exception as e:
    print(f"Error: {e}")

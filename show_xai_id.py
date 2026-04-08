import json

try:
    with open('c:\\src\\quorum\\OMAT_AJOTIEDOT.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print("--- OMAT AJOTIEDOT ROOT KEYS ---")
    for key in data.keys():
        val = data[key]
        if isinstance(val, dict):
            print(f"- {key} (dict, {len(val)} keys)")
        elif isinstance(val, list):
            print(f"- {key} (list, {len(val)} items)")
        else:
            if key != 'raw_inputs':
                print(f"- {key}: {val}")
            
except Exception as e:
    print(f"Virhe: {e}")

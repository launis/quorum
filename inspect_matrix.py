
import json
import sys

try:
    with open(r'c:\src\quorum\data\db.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    components = data.get('components', {})
    
    print("--- matrix_standard_v1 ---")
    m1 = None
    # Component ID might be key or inside value
    if 'matrix_standard_v1' in components:
        m1 = components['matrix_standard_v1']
    else:
        # Search values
        for k, v in components.items():
            if v.get('id') == 'matrix_standard_v1':
                m1 = v
                break
    print(json.dumps(m1, indent=2))

    print("\n--- matrix_cognitive_v2 ---")
    m2 = None
    if 'matrix_cognitive_v2' in components:
        m2 = components['matrix_cognitive_v2']
    else:
        for k, v in components.items():
            if v.get('id') == 'matrix_cognitive_v2':
                m2 = v
                break
    print(json.dumps(m2, indent=2))

except Exception as e:
    print(e)

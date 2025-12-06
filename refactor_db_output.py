
import json
import os

path = r'c:\Users\risto\OneDrive\quorum\data\db_mock.json'

try:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    updated = False
    
    # 1. Create the new component
    if 'components' not in data:
        data['components'] = {}
        
    # Find a new ID
    new_id = str(max([int(k) for k in data['components'].keys()] + [0]) + 1)
    
    # Check if it already exists (idempotency)
    existing_component_id = None
    for k, v in data['components'].items():
        if v.get('id') == "STANDARD_REPORT_OUTPUT":
            existing_component_id = v.get('id')
            print(f"Component STANDARD_REPORT_OUTPUT already exists with key {k}")
            break
            
    if not existing_component_id:
        data['components'][new_id] = {
            "id": "STANDARD_REPORT_OUTPUT",
            "type": "output_config",
            "name": "Standard Report Output Fields",
            "content": ["executive_summary", "final_verdict", "confidence_score", "detailed_analysis", "pisteet"]
        }
        print(f"Created new component STANDARD_REPORT_OUTPUT with key {new_id}")
        updated = True
    
    # 2. Update steps 8 and 9
    steps_to_update = ['8', '9'] # IDs in 'steps' dict are usually '1', '2'... let's check keys
    
    for step_key in steps_to_update:
        if step_key in data.get('steps', {}):
            step = data['steps'][step_key]
            # Remove old list if present
            if 'hoist_fields' in step:
                del step['hoist_fields']
                
            # Add reference
            step['output_config_component'] = "STANDARD_REPORT_OUTPUT"
            print(f"Updated step {step_key} to use output_config_component")
            updated = True
            
    if updated:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Successfully saved updated configuration to {path}")
    else:
        print("No changes needed or configuration already up to date.")

except Exception as e:
    print(f"Error updating db_mock.json: {e}")

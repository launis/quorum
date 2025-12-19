import json
import os
import sys

# Define pathts
MOCK_DB_PATH = os.path.join("backend", "database", "db_mock.json")
PROD_DB_PATH = os.path.join("backend", "database", "db.json")

def check_db(path, name):
    print(f"--- Checking {name} ({path}) ---")
    if not os.path.exists(path):
        print(f"FILE NOT FOUND: {path}")
        return

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check standard TinyDB structure: "_default": { "1": {...} }
        # Or custom structure? repository.py uses explicit tables.
        # usually TinyDB: { "steps": { "1": {...} }, "workflows": ... }
        
        steps_table = data.get('steps', {})
        found = False
        step_details = None
        
        for key, item in steps_table.items():
            # Item might be wrapped in TinyDB format? usually key is strings "1", "2"
            # item is the object.
            if item.get('id') == 'step_interaction':
                found = True
                step_details = item
                break
                
        if found:
            print(f"✅ FOUND 'step_interaction' in {name}")
            print(f"   Name: {step_details.get('name')}")
            print(f"   Component: {step_details.get('component')}")
            exec_config = step_details.get('execution_config', {})
            prompts = exec_config.get('llm_prompts', [])
            print(f"   Prompts: {prompts}")
            
            # Check prompt existence
            components_table = data.get('components', {})
            found_prompt = False
            for k, c in components_table.items():
                if c.get('id') == 'instruction_interaction':
                    found_prompt = True
                    break
            
            if found_prompt:
                print(f"✅ [SUCCESS] {name}: Found 'step_interaction' and 'instruction_interaction'")
            else:
                print(f"❌ [FAILURE] {name}: Found step but MISSING prompt")
                
        else:
            print(f"❌ [FAILURE] {name}: 'step_interaction' NOT FOUND in steps")

    except Exception as e:
        print(f"ERROR reading {name}: {e}")

if __name__ == "__main__":
    check_db(MOCK_DB_PATH, "MOCK DB")
    print("\n")
    check_db(PROD_DB_PATH, "PROD DB")

import json
import os

SEED_FILE = "backend/database/seed_data.json"

def collect_garbage():
    try:
        with open(SEED_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        components = data.get('components', [])
        steps = data.get('steps', [])
        
        # 1. Identify Referenced IDs
        referenced_ids = set()
        for step in steps:
            prompts = step.get('execution_config', {}).get('llm_prompts', [])
            for p in prompts:
                referenced_ids.add(p)
                
        # 2. Filter Components
        kept_components = []
        removed_count = 0
        removed_ids = []
        
        for comp in components:
            if comp['id'] in referenced_ids:
                kept_components.append(comp)
            else:
                removed_count += 1
                removed_ids.append(comp['id'])
                
        data['components'] = kept_components
        
        # 3. Save
        with open(SEED_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        print(f"Garbage Collection Complete.")
        print(f"Removed {removed_count} orphan components.")
        if removed_ids:
            print(f"Deleted IDs: {removed_ids}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    collect_garbage()

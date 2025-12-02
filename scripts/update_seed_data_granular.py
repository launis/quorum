import json
import os

SEED_DATA_PATH = 'data/seed_data.json'
GRANULAR_COMPONENTS_PATH = 'data/granular_components.json'

def update_seed_data():
    with open(SEED_DATA_PATH, 'r', encoding='utf-8') as f:
        seed_data = json.load(f)
    
    with open(GRANULAR_COMPONENTS_PATH, 'r', encoding='utf-8') as f:
        granular_components = json.load(f)
    
    # 1. Update Components List
    # Remove old MANDATES and GLOBAL_RULES
    seed_data['components'] = [
        c for c in seed_data['components'] 
        if c.get('id', c.get('name')) not in ['MANDATES', 'GLOBAL_RULES', 'MASTER_INSTRUCTIONS']
    ]
    
    # Insert new granular components at the beginning (or where appropriate)
    # We'll insert them at index 0 to ensure they are present.
    # Reverse to keep order when inserting at 0
    for comp in reversed(granular_components):
        seed_data['components'].insert(0, comp)
        
    # 2. Update Steps llm_prompts
    granular_ids = [c['id'] for c in granular_components]
    
    for step in seed_data['steps']:
        if 'execution_config' in step and 'llm_prompts' in step['execution_config']:
            prompts = step['execution_config']['llm_prompts']
            new_prompts = []
            for p in prompts:
                if p in ['MANDATES', 'GLOBAL_RULES', 'MASTER_INSTRUCTIONS']:
                    # Replace with granular list if not already added
                    # Check if we already added the granular block to avoid duplicates if multiple placeholders were present
                    if not any(gid in new_prompts for gid in granular_ids):
                         new_prompts.extend(granular_ids)
                else:
                    new_prompts.append(p)
            step['execution_config']['llm_prompts'] = new_prompts

    print(f"Inserted {len(granular_components)} granular components.")
    
    with open(SEED_DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(seed_data, f, indent=2, ensure_ascii=False)
    
    print(f"Updated {SEED_DATA_PATH} with granular components.")

if __name__ == "__main__":
    update_seed_data()

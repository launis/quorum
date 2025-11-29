import json
import os
from tinydb import TinyDB, Query

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'db.json')
SEED_DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'seed_data.json')

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def get_valid_models():
    if not GOOGLE_API_KEY:
        print("Warning: GOOGLE_API_KEY not found. Skipping model validation.")
        return []
    
    genai.configure(api_key=GOOGLE_API_KEY)
    models = []
    try:
        print("Fetching available Gemini models...")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                models.append(m.name.replace("models/", ""))
        return models
    except Exception as e:
        print(f"Warning: Failed to list models: {e}")
        return []

def seed_database():
    print(f"Seeding database from {SEED_DATA_PATH} to {DB_PATH}...")
    
    db = TinyDB(DB_PATH)
    db.drop_tables() # Clear everything to ensure clean state
    
    components_table = db.table('components')
    steps_table = db.table('steps')
    workflows_table = db.table('workflows')
    
    with open(SEED_DATA_PATH, 'r', encoding='utf-8') as f:
        seed_data = json.load(f)

    # Validate and fix models in workflows
    valid_models = get_valid_models()
    if valid_models:
        print(f"Available models: {valid_models}")
        if 'workflows' in seed_data:
            for wf in seed_data['workflows']:
                mapping = wf.get('default_model_mapping', {})
                for step_id, model_name in mapping.items():
                    if model_name not in valid_models:
                        # Try to find a better fallback? For now, just take the first one or try to match 'flash'/'pro'
                        fallback = valid_models[0]
                        # Simple heuristic: if 'flash' in missing model, try to find 'flash' in valid models
                        if 'flash' in model_name:
                            for vm in valid_models:
                                if 'flash' in vm:
                                    fallback = vm
                                    break
                        elif 'pro' in model_name:
                            for vm in valid_models:
                                if 'pro' in vm:
                                    fallback = vm
                                    break
                        
                        print(f"Warning: Model '{model_name}' for {step_id} not found. Replacing with '{fallback}'")
                        mapping[step_id] = fallback
        
    # Seed Components
    Component = Query()
    for component in seed_data.get('components', []):
        components_table.upsert(component, Component.id == component['id'])
        print(f"Upserted component: {component['id']}")
        
    # Seed Steps
    Step = Query()
    for step in seed_data.get('steps', []):
        steps_table.upsert(step, Step.id == step['id'])
        print(f"Upserted step: {step['id']}")
        
    # Seed Workflows
    Workflow = Query()
    for workflow in seed_data.get('workflows', []):
        workflows_table.upsert(workflow, Workflow.id == workflow['id'])
        print(f"Upserted workflow: {workflow['id']}")
        
    print("Database seeding completed.")

if __name__ == "__main__":
    seed_database()

import json
import os
import sys
from tinydb import TinyDB, Query

# Add project root to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.database.client import UTF8JSONStorage
from backend.config import DB_PATH

# Paths
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
# DB_PATH imported from config
SEED_DATA_PATH = os.path.join(DATA_DIR, 'seed_data.json')

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

def seed_database(target_db_path=None):
    db_path_to_use = target_db_path if target_db_path else DB_PATH
    print(f"Seeding database from {SEED_DATA_PATH} to {db_path_to_use}...")
    
    if not os.path.exists(SEED_DATA_PATH):
        print(f"Error: Seed data file not found at {SEED_DATA_PATH}")
        return

    # Load Seed Data Structure
    with open(SEED_DATA_PATH, 'r', encoding='utf-8') as f:
        try:
            seed_data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error decoding seed data: {e}")
            return

    db = TinyDB(db_path_to_use, storage=UTF8JSONStorage)
    db.drop_tables()
    
    components_table = db.table('components')
    steps_table = db.table('steps')
    workflows_table = db.table('workflows')

    # Seed Components
    Component = Query()
    for component in seed_data.get('components', []):
        # Determine ID (prompts have 'id', code components have 'name')
        comp_id = component.get('id') or component.get('name')
        
        if not comp_id:
            print(f"Warning: Component missing both 'id' and 'name': {component}")
            continue

        # Upsert based on the determined ID
        if 'id' in component:
            components_table.upsert(component, Component.id == comp_id)
        else:
            components_table.upsert(component, Component.name == comp_id)
            
        print(f"Upserted component: {comp_id}")

    # Seed Steps
    Step = Query()
    for step in seed_data.get('steps', []):
        steps_table.upsert(step, Step.id == step['id'])
        print(f"Upserted step: {step['id']}")

    # Validate and fix models in workflows
    valid_models = get_valid_models()
    if valid_models:
        print(f"Available models: {valid_models}")
        if 'workflows' in seed_data:
            for wf in seed_data['workflows']:
                mapping = wf.get('default_model_mapping', {})
                for step_id, model_name in mapping.items():
                    if model_name not in valid_models:
                        fallback = valid_models[0]
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

    # Seed Workflows
    Workflow = Query()
    for workflow in seed_data.get('workflows', []):
        workflows_table.upsert(workflow, Workflow.id == workflow['id'])
        print(f"Upserted workflow: {workflow['id']}")
        
    print("Database seeding completed.")

if __name__ == "__main__":
    seed_database()

import json
import os
from tinydb import Query
from src.database.client import DatabaseClient
import config

import google.generativeai as genai

def get_valid_models():
    if not config.GOOGLE_API_KEY:
        print("Warning: GOOGLE_API_KEY not found. Skipping model validation.")
        return []
    
    genai.configure(api_key=config.GOOGLE_API_KEY)
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

def initialize_database():
    """
    Initializes the database with seed data.
    """
    seed_file = config.SEED_DATA_PATH
    if not os.path.exists(seed_file):
        print(f"Seed file {seed_file} not found. Skipping initialization.")
        return

    print(f"Initializing database from {seed_file}...")
    client = DatabaseClient()
    
    with open(seed_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Validate and fix models in workflows
    valid_models = get_valid_models()
    if valid_models:
        print(f"Available models: {valid_models}")
        if 'workflows' in data:
            for wf in data['workflows']:
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

    # 1. Seed Components (Prompts & Hooks)
    components_table = client.get_table('components')
    if 'components' in data:
        for comp in data['components']:
            components_table.upsert(comp, Query().id == comp['id'])
    
    # 2. Seed Steps
    steps_table = client.get_table('steps')
    if 'steps' in data:
        for step in data['steps']:
            steps_table.upsert(step, Query().id == step['id'])

    # 3. Seed Workflows
    workflows_table = client.get_table('workflows')
    if 'workflows' in data:
        for wf in data['workflows']:
            workflows_table.upsert(wf, Query().id == wf['id'])

    print("Database initialization complete.")

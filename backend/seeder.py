import json
import os
import sys
from tinydb import TinyDB, Query
from jinja2 import Environment, FileSystemLoader

# Add project root to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.database.client import UTF8JSONStorage

# Paths
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
DB_PATH = os.path.join(DATA_DIR, 'db.json')
SEED_DATA_PATH = os.path.join(DATA_DIR, 'seed_data.json')
FRAGMENTS_DIR = os.path.join(DATA_DIR, 'fragments')
TEMPLATES_DIR = os.path.join(DATA_DIR, 'templates')

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

def load_fragments():
    fragments = {}
    if not os.path.exists(FRAGMENTS_DIR):
        print(f"Warning: Fragments directory not found at {FRAGMENTS_DIR}")
        return fragments
        
    for filename in os.listdir(FRAGMENTS_DIR):
        if filename.endswith('.json'):
            key = filename.replace('.json', '')
            with open(os.path.join(FRAGMENTS_DIR, filename), 'r', encoding='utf-8') as f:
                fragments[key] = json.load(f)
    return fragments

def seed_database():
    print(f"Seeding database from {SEED_DATA_PATH} to {DB_PATH} using SSOT fragments...")
    
    # Load Fragments
    context = load_fragments()
    print(f"Loaded fragments: {list(context.keys())}")

    # Setup Jinja2
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    
    # Load Seed Data Structure
    with open(SEED_DATA_PATH, 'r', encoding='utf-8') as f:
        seed_data = json.load(f)

    db = TinyDB(DB_PATH, storage=UTF8JSONStorage)
    db.drop_tables()
    
    components_table = db.table('components')
    steps_table = db.table('steps')
    workflows_table = db.table('workflows')

    # Template Mapping
    template_map = {
        "MASTER_INSTRUCTIONS": "master_instructions.j2",
        "BARS_MATRIX": "bars_matrix.j2",
        "PROMPT_GUARD": "prompt_guard.j2",
        "PROMPT_ANALYST": "prompt_analyst.j2",
        "PROMPT_LOGICIAN": "prompt_logician.j2",
        "PROMPT_FALSIFIER": "prompt_falsifier.j2",
        "PROMPT_CAUSAL": "prompt_causal.j2",
        "PROMPT_PERFORMATIVITY": "prompt_performativity.j2",
        "PROMPT_FACT_CHECKER": "prompt_fact_checker.j2",
        "PROMPT_JUDGE": "prompt_judge.j2",
        "PROMPT_XAI": "prompt_xai.j2"
    }

    # Seed Components with Dynamic Rendering
    Component = Query()
    for component in seed_data.get('components', []):
        # Determine ID (prompts have 'id', code components have 'name')
        comp_id = component.get('id') or component.get('name')
        
        if not comp_id:
            print(f"Warning: Component missing both 'id' and 'name': {component}")
            continue

        if comp_id in template_map:
            template_name = template_map[comp_id]
            try:
                template = env.get_template(template_name)
                rendered_content = template.render(**context)
                component['content'] = rendered_content
                print(f"Rendered component {comp_id} using {template_name}")
            except Exception as e:
                print(f"Error rendering {comp_id}: {e}")
        
        # Upsert based on the determined ID (which might be 'id' or 'name' in the DB)
        # Note: The DB schema might expect 'id' for all components or we query by whatever field is present.
        # Let's standardize: if it has 'id', query by 'id'. If 'name', query by 'name'.
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

import json
import os
import sys
from tinydb import TinyDB, Query

# Paths (mirroring seeder.py)
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
DB_PATH = os.path.join(DATA_DIR, 'db.json')
SEED_DATA_PATH = os.path.join(DATA_DIR, 'seed_data.json')
FRAGMENTS_DIR = os.path.join(DATA_DIR, 'fragments')
TEMPLATES_DIR = os.path.join(DATA_DIR, 'templates')

# Template Mapping (mirroring seeder.py)
TEMPLATE_MAP = {
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

def export_db_to_files():
    """
    Exports the current state of the database back to the file system.
    1. Components -> templates/*.j2 (WARNING: Overwrites dynamic templates with static content)
    2. Workflows -> seed_data.json
    """
    print("Starting export from DB to files...")
    
    db = TinyDB(DB_PATH, encoding='utf-8')
    components_table = db.table('components')
    workflows_table = db.table('workflows')
    steps_table = db.table('steps')

    # 1. Export Components to Templates
    for comp in components_table.all():
        comp_id = comp.get('id') or comp.get('name')
        if comp_id in TEMPLATE_MAP:
            template_filename = TEMPLATE_MAP[comp_id]
            file_path = os.path.join(TEMPLATES_DIR, template_filename)
            
            content = comp.get('content', '')
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"Exported {comp_id} to {template_filename}")
            except Exception as e:
                print(f"Error exporting {comp_id}: {e}")

    # 2. Export Workflows and Steps to seed_data.json
    # We need to reconstruct the seed_data.json structure
    # Note: We are NOT exporting fragments here, as they are not currently stored as distinct entities in the DB 
    # (they are rendered into components).
    
    try:
        # Read existing seed_data to preserve other fields if any
        if os.path.exists(SEED_DATA_PATH):
            with open(SEED_DATA_PATH, 'r', encoding='utf-8') as f:
                seed_data = json.load(f)
        else:
            seed_data = {"components": [], "steps": [], "workflows": []}

        # Update workflows
        seed_data['workflows'] = workflows_table.all()
        
        # Update steps
        seed_data['steps'] = steps_table.all()
        
        # Update components list in seed_data (metadata only, content is in templates usually, 
        # but seed_data might have inline content for non-template components)
        # For this MVP, we will just update the components list from DB.
        seed_data['components'] = components_table.all()
        
        # Remove 'content' from components in seed_data if it maps to a template?
        # seeder.py logic:
        # if comp_id in template_map: render template -> component['content']
        # So seed_data.json usually DOES NOT contain the content for templated items.
        # If we write the content back to seed_data.json, seeder.py will overwrite it with the template render anyway.
        # So it's safe to write it, but redundant.
        # However, for NON-templated components (if any), we MUST write the content.
        
        with open(SEED_DATA_PATH, 'w', encoding='utf-8') as f:
            json.dump(seed_data, f, indent=2, ensure_ascii=False)
        print(f"Exported workflows and steps to {SEED_DATA_PATH}")
        
    except Exception as e:
        print(f"Error exporting seed data: {e}")
        raise e

    return {"status": "success", "message": "Configuration exported to files."}

if __name__ == "__main__":
    export_db_to_files()

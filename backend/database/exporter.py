import json
import os
import sys
from tinydb import TinyDB, Query
# from backend.config import DB_PATH # Removed

# Paths (mirroring seeder.py)
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
# DB_PATH imported from config
SEED_DATA_PATH = os.path.join(DATA_DIR, 'seed_data.json')

def export_db_to_files(source_db_path=None):
    """
    Exports the current state of the database back to `seed_data.json`.
    """
    from backend.settings import get_settings
    settings = get_settings()
    
    db_path_to_use = source_db_path if source_db_path else settings.start_db_path
    print(f"Starting export from DB ({db_path_to_use}) to files...")
    
    db = TinyDB(db_path_to_use, encoding='utf-8')
    components_table = db.table('components')
    workflows_table = db.table('workflows')
    steps_table = db.table('steps')

    # 2. Export Workflows and Steps to seed_data.json
    # We need to reconstruct the seed_data.json structure
    # Note: We are NOT exporting fragments here, as they are not currently stored as distinct entities in the DB 
    # (they are rendered into components).
    
    try:
        # Read existing seed_data to preserve other fields if any
        if os.path.exists(settings.seed_data_path):
            with open(settings.seed_data_path, 'r', encoding='utf-8') as f:
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
        
        with open(settings.seed_data_path, 'w', encoding='utf-8') as f:
            json.dump(seed_data, f, indent=2, ensure_ascii=False)
        print(f"Exported workflows and steps to {settings.seed_data_path}")
        
    except Exception as e:
        print(f"Error exporting seed data: {e}")
        raise e

    return {"status": "success", "message": "Configuration exported to files."}

if __name__ == "__main__":
    export_db_to_files()

import json
import os
from typing import Optional
from tinydb import TinyDB, Query
from backend.config import DB_PATH, SEED_DATA_PATH

def seed_database(target_db_path: Optional[str] = None):
    """
    Seeds the TinyDB database with initial data from seed_data.json.
    
    Args:
        target_db_path (Optional[str]): Path to the database file. Defaults to DB_PATH from config.
    """
    db_path_to_use = target_db_path if target_db_path else DB_PATH
    print(f"[Seeder] Seeding database at: {db_path_to_use}")
    print(f"[Seeder] Using seed data from: {SEED_DATA_PATH}")

    if not os.path.exists(SEED_DATA_PATH):
        print(f"[Seeder] Error: Seed data file not found at {SEED_DATA_PATH}")
        return

    # 1. Load Seed Data
    try:
        with open(SEED_DATA_PATH, 'r', encoding='utf-8') as f:
            seed_data = json.load(f)
    except Exception as e:
        print(f"[Seeder] Error loading seed data: {e}")
        return

    # 2. Initialize Database
    try:
        db = TinyDB(db_path_to_use, encoding='utf-8')
        db.drop_tables()
        print("[Seeder] Cleared existing tables.")
    except Exception as e:
        print(f"[Seeder] Error initializing database: {e}")
        return

    # 3. Seed Tables
    components_table = db.table('components')
    steps_table = db.table('steps')
    workflows_table = db.table('workflows')
    banned_phrases_table = db.table('banned_phrases')

    # Seed Components
    Component = Query()
    components_count = 0
    for component in seed_data.get('components', []):
        try:
            comp_id = component.get('id') or component.get('name')
            if not comp_id:
                print(f"[Seeder] Warning: Component missing 'id' or 'name': {component}")
                continue
            
            # Ensure ID is consistent
            if 'id' in component:
                components_table.upsert(component, Component.id == comp_id)
            else:
                components_table.upsert(component, Component.name == comp_id)
            components_count += 1
        except Exception as e:
            print(f"[Seeder] Failed to upsert component {component}: {e}")
    print(f"[Seeder] Upserted {components_count} components.")

    # Seed Steps
    Step = Query()
    steps_count = 0
    for step in seed_data.get('steps', []):
        try:
            steps_table.upsert(step, Step.id == step['id'])
            steps_count += 1
        except Exception as e:
            print(f"[Seeder] Failed to upsert step {step.get('id')}: {e}")
    print(f"[Seeder] Upserted {steps_count} steps.")

    # Seed Workflows
    Workflow = Query()
    workflows_count = 0
    for workflow in seed_data.get('workflows', []):
        try:
            workflows_table.upsert(workflow, Workflow.id == workflow['id'])
            workflows_count += 1
        except Exception as e:
            print(f"[Seeder] Failed to upsert workflow {workflow.get('id')}: {e}")
    print(f"[Seeder] Upserted {workflows_count} workflows.")
    
    # Seed Banned Phrases (Optional)
    if 'banned_phrases' in seed_data:
        Phrase = Query()
        phrases_count = 0
        for item in seed_data['banned_phrases']:
            try:
                banned_phrases_table.upsert(item, Phrase.phrase == item['phrase'])
                phrases_count += 1
            except Exception as e:
                print(f"[Seeder] Failed to upsert banned phrase: {e}")
        print(f"[Seeder] Upserted {phrases_count} banned phrases.")

    print("[Seeder] Database seeding completed successfully.")

if __name__ == "__main__":
    seed_database()

import json
import os
from tinydb import Query
from src.database.client import DatabaseClient
import config

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

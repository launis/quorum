import os
import sys

# Set environment variable to force Mock DB usage
os.environ["USE_MOCK_DB"] = "True"

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.engine import WorkflowEngine
from backend.config import get_db_path, DATA_DIR
import json

def seed_mock_db():
    print("Seeding MOCK Database...")
    
    # Ensure we are targeting the mock DB file
    # (WorkflowEngine should pick this up via env var)
    engine = WorkflowEngine(get_db_path())
    print(f"Target DB Path: {engine.db_path}")
    
    seed_file = os.path.join(DATA_DIR, "seed_data.json")
    if not os.path.exists(seed_file):
        print(f"Error: Seed file not found at {seed_file}")
        return

    with open(seed_file, 'r', encoding='utf-8') as f:
        seed_data = json.load(f)

    # Clear existing tables
    engine.db.drop_tables()
    
    # Insert data
    if 'components' in seed_data:
        engine.components_table.insert_multiple(seed_data['components'])
        print(f"Inserted {len(seed_data['components'])} components.")
        
    if 'workflows' in seed_data:
        engine.workflows_table.insert_multiple(seed_data['workflows'])
        print(f"Inserted {len(seed_data['workflows'])} workflows.")
        
    if 'steps' in seed_data:
        engine.steps_table.insert_multiple(seed_data['steps'])
        print(f"Inserted {len(seed_data['steps'])} steps.")
        
    if 'prompts' in seed_data:
        engine.prompts_table.insert_multiple(seed_data['prompts'])
        print(f"Inserted {len(seed_data['prompts'])} prompts.")

    print("Mock Database seeded successfully.")

if __name__ == "__main__":
    seed_mock_db()

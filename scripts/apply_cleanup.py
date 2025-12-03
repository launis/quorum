import sys
import os

# Add project root to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.seeder import seed_database

# Paths
PROD_DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'db.json')
MOCK_DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'db_mock.json')

if __name__ == "__main__":
    print(f"Seeding PROD DB at: {PROD_DB_PATH}")
    seed_database(target_db_path=PROD_DB_PATH)
    
    print(f"Seeding MOCK DB at: {MOCK_DB_PATH}")
    seed_database(target_db_path=MOCK_DB_PATH)

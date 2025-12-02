import sys
import os

# Add project root to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.seeder import seed_database

# Path to mock DB
MOCK_DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'db_mock.json')

if __name__ == "__main__":
    print(f"Force seeding mock database at: {MOCK_DB_PATH}")
    seed_database(target_db_path=MOCK_DB_PATH)

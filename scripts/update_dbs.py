import sys
import os

# Add project root to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from backend.seeder import seed_database
from scripts.clean_seed import clean_seed_data

def main():
    print("--- Cleaning Seed Data ---")
    clean_seed_data()
    
    print("\n--- Seeding Production DB (data/db.json) ---")
    seed_database(target_db_path="data/db.json")
    
    print("\n--- Seeding Mock DB (data/db_mock.json) ---")
    seed_database(target_db_path="data/db_mock.json")
    
    print("\n--- All Done ---")

if __name__ == "__main__":
    main()

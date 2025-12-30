from backend.database.seeder import seed_database
import os

def deploy():
    # 1. Seed Production (run_locally.bat)
    prod_db = os.path.join("backend", "database", "db_prod.json")
    print(f"\n--- SEEDING PRODUCTION ({prod_db}) ---")
    seed_database(target_db_path=prod_db)
    
    # 2. Seed Test/Mock (run_mock_locally.bat)
    mock_db = os.path.join("backend", "database", "db_mock.json")
    print(f"\n--- SEEDING TEST/MOCK ({mock_db}) ---")
    seed_database(target_db_path=mock_db)
    
    print("\nDEPLOYMENT COMPLETE: Both environments updated.")

if __name__ == "__main__":
    deploy()

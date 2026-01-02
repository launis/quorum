
import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from backend.database.seeder import seed_database

TARGET_DB = str(PROJECT_ROOT / "data" / "db.json")

def main():
    print(f"Forcing seed to: {TARGET_DB}")
    # Ensure directory exists
    os.makedirs(os.path.dirname(TARGET_DB), exist_ok=True)
    
    seed_database(target_db_path=TARGET_DB)
    print("Seed complete.")

if __name__ == "__main__":
    main()

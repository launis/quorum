
import os
import sys
import shutil
import time

# Ensure backend modules can be imported
sys.path.append(os.getcwd())

from backend.database.seeder import seed_database
from backend.settings import get_settings

def reset_db():
    print("⚠️  STARTING EMERGENCY DB RESET ⚠️")
    
    # 1. Force Configuration for Local Prod DB
    os.environ["USE_MOCK_DB"] = "false"
    os.environ["STORAGE_BACKEND"] = "LOCAL"
    os.environ["USE_MOCK_LLM"] = "true" # Bypass credential check
    
    settings = get_settings()
    db_path = settings.start_db_path # Should resolve to data/db.json
    
    print(f"Target Database: {db_path}")
    
    # 2. Check and Rename Corrupt File
    if os.path.exists(db_path):
        corrupt_path = db_path + ".corrupt"
        print(f"Attempting to move corrupted file to: {corrupt_path}")
        try:
            if os.path.exists(corrupt_path):
                os.remove(corrupt_path) # clear old backup
            os.rename(db_path, corrupt_path)
            print("✅ File moved successfully.")
        except OSError as e:
            print(f"❌ ERROR: Could not move file. Is the server still running?")
            print(f"Details: {e}")
            print("\n!!! ACTION REQUIRED !!!")
            print("Please STOP the running 'run_locally.bat' process (Ctrl+C) and try running this script again.")
            return

    # 3. Re-Seed
    print("🌱 Re-seeding database from seed_data.json...")
    try:
        # Run synchronous seeder
        seed_database()
        print("✅ Database successfully re-seeded!")
        print("You can now restart the server.")
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    reset_db()

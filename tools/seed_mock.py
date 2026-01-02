
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set Mock env vars BEFORE importing seeder options or running logic
os.environ["USE_MOCK_DB"] = "true"
os.environ["USE_MOCK_LLM"] = "true"
os.environ["STORAGE_BACKEND"] = "LOCAL"

from backend.database.seeder import seed_database

print("Seeding Mock Database (data/db_mock.json)...")
# target_db_path is optional usually, but let's be explicit if seeder allows, 
# typically seeder logic picks path based on env vars.
seed_database()
print("Done.")

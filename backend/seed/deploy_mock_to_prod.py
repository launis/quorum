import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.database.exporter import export_db_to_files
from backend.seed.seeder import seed_database
from backend.settings import get_settings


def deploy_mock_to_prod():
    settings = get_settings()

    print("--- DEPLOYING MOCK CONFIGIGURATION TO PRODUCTION ---")
    print(f"1. Mock DB: {settings.mock_db_path}")
    print(f"2. Seed File: {settings.seed_data_path}")
    print(f"3. Prod DB: {settings.prod_db_path}")

    # 1. Export Mock -> Seed (Excludes Executions by design of exporter)
    print("\n[Step 1] Exporting Mock DB to seed_data.json...")
    export_db_to_files(source_db_path=settings.mock_db_path)

    # 2. Seed Prod <- Seed
    print("\n[Step 2] Seeding Production DB from seed_data.json...")
    # NOTE: seed_database usually clears the tables first.
    # If we want to preserve Prod executions, we must be careful.
    # backend/database/seeder.py usually clears components/steps/workflows but LEAVES executions?
    # Let's verify seeder logic below.
    seed_database(target_db_path=settings.prod_db_path)

    print("\n[SUCCESS] Configuration deployed successfully.")


if __name__ == "__main__":
    deploy_mock_to_prod()

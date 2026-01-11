"""Seed Firestore Data Script."""

import os
import sys
from pathlib import Path


def main():
    """Sets up environment for Firestore seeding and runs the backend.database.seeder module."""
    print("==========================================")
    print("  SEED FIRESTORE DATABASE (Python Script) ")
    print("==========================================")

    # 1. Define Project Root
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent

    # 2. Add Project Root to Sys Path to allow imports
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # 3. Set Environment Variables
    os.environ["USE_MOCK_DB"] = "false"
    os.environ["USE_MOCK_LLM"] = "true"
    os.environ["STORAGE_BACKEND"] = "FIRESTORE"
    # Assumes service-account.json is in project root
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(project_root / "service-account.json")
    os.environ["PYTHONIOENCODING"] = "utf-8"

    print(f"\n[INFO] Root Path: {project_root}")
    print("[INFO] Backend: FIRESTORE")
    print(f"[INFO] Credential: {os.environ['GOOGLE_APPLICATION_CREDENTIALS']}")
    print("\n[WARNING] This will WIPE and RE-POPULATE the Firestore database.")
    print("[ACTION] Importing backend.seed.seeder...\n")

    try:
        from backend.seed.seeder import seed_database

        seed_database()

        print("\n[SUCCESS] Firestore populated successfully!")

    except ImportError as e:
        print(f"\n[ERROR] Could not import backend: {e}")
        print("Ensure you are running with 'uv run' or in the virtual environment.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

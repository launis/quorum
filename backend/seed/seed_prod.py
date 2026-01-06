import os
import subprocess
import sys
from pathlib import Path


def main():
    """Sets up environment to seed PROD DB (data/db.json) from seed_data.json.
    WARNING: ALL EXISTING DATA IN data/db.json WILL BE LOST.
    """
    print("=======================================")
    print("  SEED PROD DB (Python Script)         ")
    print("=======================================")

    # 1. Define Project Root
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent

    # 2. Add Project Root to Sys Path to allow imports
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # 3. Set Environment Variables
    os.environ["USE_MOCK_DB"] = "false"
    os.environ["USE_MOCK_LLM"] = "true"  # Bypass LLM check
    os.environ["STORAGE_BACKEND"] = "LOCAL"
    os.environ["PYTHONIOENCODING"] = "utf-8"

    print(f"\n[INFO] Root Path: {project_root}")
    print("[INFO] Target: PROD DB (data/db.json)")
    print("[WARNING] This will WIPE and RE-POPULATE the local production database.")
    print("[ACTION] Importing backend.seed.seeder...\n")

    try:
        from backend.seed.seeder import seed_database
        import asyncio
        asyncio.run(seed_database())
        
        print("\n[SUCCESS] Prod DB populated successfully!")

    except ImportError as e:
        print(f"\n[ERROR] Could not import backend: {e}")
        print("Ensure you are running with 'uv run' or in the virtual environment.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

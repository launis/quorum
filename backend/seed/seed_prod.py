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
    # backend/seed -> backend -> root
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent

    # 2. Set Environment Variables
    env = os.environ.copy()
    # Force Prod DB mode so we target data/db.json
    env["USE_MOCK_DB"] = "false"
    env["USE_MOCK_LLM"] = "true"  # Bypass LLM check
    env["STORAGE_BACKEND"] = "LOCAL"
    env["PYTHONIOENCODING"] = "utf-8"

    print(f"\n[INFO] Root Path: {project_root}")
    print("[INFO] Target: PROD DB (data/db.json)")
    print("[WARNING] This will WIPE and RE-POPULATE the local production database.")
    print("[ACTION] Running backend.seed.seeder...\n")

    # 3. Run the Module
    try:
        subprocess.run([sys.executable, "-m", "backend.seed.seeder"], cwd=project_root, env=env, check=True)
        print("\n[SUCCESS] Prod DB populated successfully!")

    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Seeding failed with exit code {e.returncode}.")
        sys.exit(e.returncode)
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

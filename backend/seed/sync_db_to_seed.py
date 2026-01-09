import os
import subprocess
import sys
from pathlib import Path


def main():
    """Sets up environment to reads PROD DB (data/db.json) and sync it to seed_data.json."""
    print("=======================================")
    print("  SYNC PROD DB TO SEED (Python Script) ")
    print("=======================================")

    # 1. Define Project Root
    # backend/seed -> backend -> root
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent

    # 2. Set Environment Variables
    env = os.environ.copy()
    # Force Prod DB mode so Settings picks up data/db.json
    env["USE_MOCK_DB"] = "false"
    env["USE_MOCK_LLM"] = "true"  # Bypass LLM check
    env["STORAGE_BACKEND"] = "LOCAL"
    env["PYTHONIOENCODING"] = "utf-8"

    print(f"\n[INFO] Root Path: {project_root}")
    print("[INFO] Source: PROD DB (data/db.json)")
    print("[INFO] Target: SEED FILE (backend/seed/seed_data.json)")
    print("[ACTION] Running backend.seed.syncer...\n")

    # 3. Run the Module
    try:
        subprocess.run([sys.executable, "-m", "backend.seed.syncer"], cwd=project_root, env=env, check=True)
        print("\n[SUCCESS] Sync completed!")

    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Sync failed with exit code {e.returncode}.")
        sys.exit(e.returncode)
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

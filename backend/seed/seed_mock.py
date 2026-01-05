import os
import subprocess
import sys
from pathlib import Path


def main():
    """Sets up environment for Mock DB seeding and runs the backend.seed.seeder module.
    """
    print("======================================")
    print("  SEED MOCK DATABASE (Python Script)  ")
    print("======================================")

    # 1. Define Project Root
    # This script is in backend/seed/, so root is two levels up (../../)
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent

    # 2. Set Environment Variables
    env = os.environ.copy()
    env["USE_MOCK_DB"] = "true"
    env["USE_MOCK_LLM"] = "true"
    env["STORAGE_BACKEND"] = "LOCAL"
    env["PYTHONIOENCODING"] = "utf-8"

    print(f"\n[INFO] Root Path: {project_root}")
    print("[INFO] Backend: LOCAL (MOCK)")
    print("[ACTION] Running backend.seed.seeder...\n")

    # 3. Run the Module
    try:
        subprocess.run([sys.executable, "-m", "backend.seed.seeder"], cwd=project_root, env=env, check=True)
        print("\n[SUCCESS] Mock DB populated successfully!")

    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Seeding failed with exit code {e.returncode}.")
        sys.exit(e.returncode)
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

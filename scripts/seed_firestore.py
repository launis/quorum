import os
import sys
import subprocess
from pathlib import Path

def main():
    """
    Sets up environment for Firestore seeding and runs the backend.database.seeder module.
    """
    print("==========================================")
    print("  SEED FIRESTORE DATABASE (Python Script) ")
    print("==========================================")
    
    # 1. Define Project Root
    # This script is in scripts/, so root is one level up (../)
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent
    
    # 2. Set Environment Variables
    # These override whatever is currently set in the shell for this subprocess
    env = os.environ.copy()
    env["USE_MOCK_DB"] = "false"
    env["STORAGE_BACKEND"] = "FIRESTORE"
    # Assumes service-account.json is in project root
    env["GOOGLE_APPLICATION_CREDENTIALS"] = str(project_root / "service-account.json")
    env["PYTHONIOENCODING"] = "utf-8"

    print(f"\n[INFO] Root Path: {project_root}")
    print(f"[INFO] Backend: FIRESTORE")
    print(f"[INFO] Credential: {env['GOOGLE_APPLICATION_CREDENTIALS']}")
    print(f"\n[WARNING] This will WIPE and RE-POPULATE the Firestore database.")
    print(f"[ACTION] Running backend.database.seeder...\n")

    # 3. Run the Module
    try:
        # We run the module using sys.executable to ensure we use the same Python interpreter
        # cwd=project_root ensures imports like 'backend.foo' work correctly
        subprocess.run(
            [sys.executable, "-m", "backend.database.seeder"],
            cwd=project_root,
            env=env,
            check=True
        )
        print("\n[SUCCESS] Firestore populated successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Seeding failed with exit code {e.returncode}.")
        sys.exit(e.returncode)
    except Exception as e:
        print(f"\n[ERROR] An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

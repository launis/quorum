import argparse
import json
import logging
import os
import sys
from pathlib import Path

# Add project root to path to allow backend imports
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.seed.seeder import _seed_firestore, _seed_tinydb

SEED_PATH = os.path.join(project_root, "backend", "seed", "seed_data.json")
LOCAL_DB_PATH = os.path.join(project_root, "data", "db.json")
MOCK_DB_PATH = os.path.join(project_root, "backend", "database", "db_mock.json")

# Configure Logging to File
logging.basicConfig(
    filename="seed.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filemode="w",
    encoding="utf-8",
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger("").addHandler(console)


def seed(target):
    print(f"--- SEEDING TARGET: {target.upper()} ---")

    if not os.path.exists(SEED_PATH):
        print(f"CRITICAL: Seed file not found at {SEED_PATH}")
        sys.exit(1)

    # Load Data
    with open(SEED_PATH, encoding="utf-8") as f:
        data = json.load(f)

    print(f"[Seed] Loaded {len(data.get('workflows', []))} workflows.")

    if target == "local":
        if os.path.exists(LOCAL_DB_PATH):
            os.remove(LOCAL_DB_PATH)
            print(f"[Seed] Removed existing {LOCAL_DB_PATH}")
        _seed_tinydb(LOCAL_DB_PATH, data)
        print(f"[SUCCESS] Seeded Local DB (Prod-like) at {LOCAL_DB_PATH}")

    elif target == "mock":
        if os.path.exists(MOCK_DB_PATH):
            os.remove(MOCK_DB_PATH)
            print(f"[Seed] Removed existing {MOCK_DB_PATH}")
        _seed_tinydb(MOCK_DB_PATH, data)
        print(f"[SUCCESS] Seeded Mock DB (Test) at {MOCK_DB_PATH}")

    elif target == "firestore":
        print("[Seed] Connecting to Firestore...")
        # Ensure we don't accidentally check env vars inside _seed_firestore unless needed
        _seed_firestore(data)
        print("[SUCCESS] Seeded Cloud Firestore.")


def main():
    parser = argparse.ArgumentParser(description="Unified Database Seeder")
    parser.add_argument(
        "targets",
        nargs="+",
        choices=["local", "mock", "firestore", "all"],
        help="Target environment(s). 'local'=data/db.json, 'mock'=data/db_mock.json",
    )

    args = parser.parse_args()

    targets = set(args.targets)
    if "all" in targets:
        targets = {"local", "mock", "firestore"}

    for t in targets:
        try:
            seed(t)
        except Exception as e:
            print(f"[ERROR] Failed to seed {t}: {e}")
            sys.exit(1)

    print("\n✅ All requested targets completed successfully.")


if __name__ == "__main__":
    main()

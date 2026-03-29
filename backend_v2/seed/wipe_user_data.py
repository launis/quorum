import json
import os
import shutil
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "db_v2.json")
BACKUP_DIR = os.path.join(os.path.dirname(__file__), "backups")


def wipe_dynamic_data() -> None:
    """Wipes all user-generated dynamic data (Workflows and Executions) from the V3 database.
    This creates a clean slate for the V3 Event Sourced Engine while preserving seeded system_config.
    """
    print("WARNING: This will permanently wipe all Workflows and Executions from db_v2.json!")
    confirmation = input("Are you sure you want to proceed? (y/N): ")
    if confirmation.lower() != "y":
        print("Aborted.")
        return

    # 1. Create a timestamped backup first
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"db_v2_backup_before_wipe_{timestamp}.json")
    shutil.copy(DB_PATH, backup_path)
    print(f"[Backup] Database backed up to {backup_path}")

    # 2. Open and mutate the DB
    with open(DB_PATH, encoding="utf-8") as f:
        data = json.load(f)

    # 3. Wipe target dynamic tables
    workflows_count = len(data.get("workflows", {}))
    executions_count = len(data.get("executions", {}))

    data["workflows"] = {}
    data["executions"] = {}

    # 4. Save the DB
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("[Scrubber] Clean slate achieved!")
    print(f" - Wiped {workflows_count} Workflows.")
    print(f" - Wiped {executions_count} Executions.")
    print("Please restart any running V3 Backend processes to ensure fresh state propagation.")


if __name__ == "__main__":
    wipe_dynamic_data()

"""Script for wiping dynamic user data from the local V2 database.

Provides a clean slate for the Event Sourced Engine while preserving seeded system_config.
"""

from __future__ import annotations

import argparse
import json
import logging
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)

__all__ = [
    "BACKUP_DIR",
    "DB_PATH",
    "EXECUTIONS_DIR",
    "REPO_ROOT",
    "main",
    "wipe_dynamic_data",
]

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DB_PATH = REPO_ROOT / "data" / "db_v2.json"
BACKUP_DIR = Path(__file__).resolve().parent / "backups"
EXECUTIONS_DIR = REPO_ROOT / "data" / "files" / "executions"


def wipe_dynamic_data(force: bool = False) -> None:
    """Wipe all user-generated dynamic data (Workflows and Executions) from the V2 database.

    Creates a clean slate for the V2 Event Sourced Engine while preserving seeded system_config.

    Args:
        force: If True, bypass interactive user confirmation prompt.

    Raises:
        AppException: STORAGE_ACCESS_FAILED if the database file is missing or file operations fail.
    """
    if not force:
        print("WARNING: This will permanently wipe all Workflows and Executions from db_v2.json!")
        confirmation = input("Are you sure you want to proceed? (y/N): ")
        if confirmation.lower() != "y":
            print("Aborted.")
            return

    db_path = Path(DB_PATH)
    backup_dir = Path(BACKUP_DIR)
    executions_dir = Path(EXECUTIONS_DIR)

    if not db_path.exists():
        logger.error(
            "Database file not found for wiping at %s",
            db_path,
            extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.name},
            exc_info=True,
        )
        raise AppException(
            message=f"Database file not found: {db_path}",
            status_code=404,
            details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
        )

    try:
        # 1. Create a timestamped backup first
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"db_v2_backup_before_wipe_{timestamp}.json"
        shutil.copy(db_path, backup_path)
        print(f"[Backup] Database backed up to {backup_path}")

        # 2. Open and mutate the DB
        with open(db_path, encoding="utf-8") as f:
            data = json.load(f)

        # 3. Wipe target dynamic tables
        workflows_count = 0
        if "workflows" in data:
            workflows_count = len(data["workflows"])

        executions_count = 0
        if "executions" in data:
            executions_count = len(data["executions"])

        data["workflows"] = {}
        data["executions"] = {}

        # 4. Save the DB
        with open(db_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # 5. Wipe orphaned physical files
        if executions_dir.exists():
            shutil.rmtree(executions_dir, ignore_errors=True)
            executions_dir.mkdir(parents=True, exist_ok=True)

        print("[Scrubber] Clean slate achieved!")
        print(f" - Wiped {workflows_count} Workflows.")
        print(f" - Wiped {executions_count} Executions.")
        print("Please restart any running V2 Backend processes to ensure fresh state propagation.")

    except (OSError, json.JSONDecodeError) as e:
        logger.error(
            "Failed to wipe dynamic data from database at %s",
            db_path,
            extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.name, "error_details": str(e)},
            exc_info=True,
        )
        raise AppException(
            message=f"Database wipe failed: {str(e)}",
            status_code=500,
            details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
        ) from e


def main(argv: list[str] | None = None) -> None:
    """CLI entrypoint for database wipe utility.

    Args:
        argv: Optional command-line argument list.
    """
    parser = argparse.ArgumentParser(description="Wipe dynamic user data from local V2 database")
    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Bypass interactive confirmation prompt",
    )
    args = parser.parse_args(argv)
    wipe_dynamic_data(force=args.force)


if __name__ == "__main__":
    main(sys.argv[1:])

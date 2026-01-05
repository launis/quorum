from pathlib import Path

import verifier


def main():
    """Runs the DB Verification logic.
    """
    # 1. Define Project Root
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent

    seed_path = script_dir / "seed_data.json"
    prod_path = project_root / "data" / "db.json"
    mock_path = project_root / "backend" / "database" / "db_mock.json"
    firestore_creds = project_root / "service-account.json"

    verifier.run_verification(seed_path, prod_path, mock_path, firestore_creds)


if __name__ == "__main__":
    main()

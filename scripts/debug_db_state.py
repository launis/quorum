"""Debug Database State."""
import os

from tinydb import TinyDB


def debug_db():
    """Prints summary statistics for Prod and Mock TinyDB instances."""
    print("=======================================")
    print("  DEBUG TINYDB STATE                   ")
    print("=======================================")

    # 1. Inspect data/db.json (PROD)
    prod_db_path = os.path.join("data", "db.json")
    print(f"\n[Target: PROD DB] {os.path.abspath(prod_db_path)}")

    if not os.path.exists(prod_db_path):
        print("  -> FILE NOT FOUND!")
    else:
        try:
            db = TinyDB(prod_db_path, encoding="utf-8")
            tables = db.tables()
            print(f"  -> Tables Found: {len(tables)} ({', '.join(tables)})")

            for table_name in tables:
                table = db.table(table_name)
                print(f"     - {table_name}: {len(table.all())} records")

            # Check for executions specifically
            if "executions" in tables:
                print("     [WARNING] 'executions' table exists! Seeding should have wiped this?")
            else:
                print("     [OK] 'executions' table is clean/missing.")

        except Exception as e:
            print(f"  -> ERROR reading DB: {e}")

    # 2. Inspect backend/database/db_mock.json (MOCK)
    mock_db_path = os.path.join("backend", "database", "db_mock.json")
    print(f"\n[Target: MOCK DB] {os.path.abspath(mock_db_path)}")

    if not os.path.exists(mock_db_path):
        print("  -> FILE NOT FOUND (Normal if strictly using Prod)")
    else:
        try:
            db = TinyDB(mock_db_path, encoding="utf-8")
            print(f"  -> Tables Found: {len(db.tables())}")
        except Exception as e:
            print(f"  -> ERROR reading MOCK DB: {e}")


if __name__ == "__main__":
    debug_db()

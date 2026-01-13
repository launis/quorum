"""Inspector for TinyDB mock database."""

import json
import os

DB_PATH = r"C:\src\quorum\backend\database\db_mock.json"


def inspect_db():
    """Load and print summary of the mock database."""
    if not os.path.exists(DB_PATH):
        print(f"DB file not found: {DB_PATH}")
        return

    try:
        with open(DB_PATH, encoding="utf-8") as f:
            data = json.load(f)

        # Check keys
        print(f"Top level keys: {list(data.keys())}")

        # Check users table
        # TinyDB usually stores tables as keys. If 'users' key exists directly:
        if "users" in data:
            users_table = data["users"]
            print(f"Users table found. Records: {len(users_table)}")
            # TinyDB usually uses numeric keys for records in a table dict
            for key, user in users_table.items():
                if user.get("uid") == "root_master":
                    print(f"Found root_master (Key: {key}): {user}")
                else:
                    # Print one sample non-root user
                    # print(f"Sample user: {user}")
                    pass
        elif "_default" in data:
            # Sometimes default table is used?
            print("Checking _default table...")
        else:
            print("No 'users' table found in top level.")

    except Exception as e:
        print(f"Error reading DB: {e}")


if __name__ == "__main__":
    inspect_db()

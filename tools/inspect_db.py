"""Inspect Database Tool."""
import json
import os

db_path = r"c:\Users\risto\OneDrive\quorum\data\db.json"

if not os.path.exists(db_path):
    print(f"Error: {db_path} not found")
    exit(1)

try:
    with open(db_path, encoding="utf-8") as f:
        data = json.load(f)

    users = data.get("users", {})
    # TinyDB might store as dict of dicts or list
    if isinstance(users, dict):
        print(f"Found {len(users)} users (dict)")
        for _key, user in users.items():
            print(
                f"User: {user.get('uid', 'unknown')} | "
                f"Org: {user.get('organization_id', 'unknown')} | "
                f"Role: {user.get('role', 'unknown')}"
            )
    elif isinstance(users, list):
        print(f"Found {len(users)} users (list)")
        for user in users:
            print(
                f"User: {user.get('uid', 'unknown')} | "
                f"Org: {user.get('organization_id', 'unknown')} | "
                f"Role: {user.get('role', 'unknown')}"
            )
    else:
        print("Users key not found or empty")
        # Check if it is nested in '_default' standard TinyDB format
        default = data.get("_default", {})
        if default:
            print("Found _default table, checking contents...")
            # This would be complex to parse if mixed types, assuming separation by table names in root

except Exception as e:
    print(f"Error reading DB: {e}")

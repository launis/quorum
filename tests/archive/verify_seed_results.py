import os

from tinydb import TinyDB


def verify_seed():
    db_path = "data/db.json"  # Actual prod path
    if not os.path.exists(db_path):
        db_path = "db.json"  # Fallback check

    print(f"Checking {db_path}...")
    db = TinyDB(db_path)

    # Check Org
    orgs = db.table("organizations").all()
    print(f"Organizations count: {len(orgs)}")
    print(f"Found Org IDs: {[o.get('id') for o in orgs]}")
    system_org = next((o for o in orgs if o["id"] == "system"), None)
    if system_org:
        print("PASS: System Org found.")
    else:
        print("FAIL: System Org MISSING.")

    # Check User
    users = db.table("users").all()
    print(f"Users count: {len(users)}")
    root = next((u for u in users if u["uid"] == "root_master"), None)
    if root:
        print(f"PASS: Root User found (Org: {root.get('organization_id')}).")
    else:
        print("FAIL: Root User MISSING.")

    # Check for legacy demo data
    demo = next((o for o in orgs if o["id"] == "demo_corp_id"), None)
    if not demo:
        print("PASS: Demo Corp NOT present (Clean).")
    else:
        print("WARN: Demo Corp IS present.")


if __name__ == "__main__":
    verify_seed()

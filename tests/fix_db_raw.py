
from tinydb import TinyDB, Query
import time

def fix_db_directly():
    print("--- RAW DB FIX ---")
    db = TinyDB("db.json")
    
    # 1. Fix Organizations
    org_table = db.table("organizations")
    Organization = Query()
    
    # Ensure system exists
    sys_org = org_table.get(Organization.id == "system")
    if not sys_org:
        print("Creating 'system' org...")
        org_table.insert({
            "id": "system",
            "name": "System Administration",
            "tier": "enterprise",
            "created_at": str(time.time()),
            "contact_email": "root@example.com",
            "is_active": True
        })
    else:
        print(f"System Org found: {sys_org}")
        # Patch tier if missing
        if "tier" not in sys_org:
            print("Patching system tier...")
            org_table.update({"tier": "enterprise"}, Organization.id == "system")

    # 2. Fix Users
    user_table = db.table("users")
    User = Query()
    root = user_table.get(User.uid == "root_master")
    
    if root:
        print(f"Root User found. Org: {root.get('organization_id')}")
        if root.get("organization_id") != "system":
            print("Updating Root user to org 'system'...")
            user_table.update({"organization_id": "system"}, User.uid == "root_master")
    else:
        print("Root User NOT FOUND!")

    print("--- DONE ---")

if __name__ == "__main__":
    fix_db_directly()

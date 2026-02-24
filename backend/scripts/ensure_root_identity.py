import sys
from datetime import datetime, timezone
from pathlib import Path

# Helper for standalone TinyDB access
try:
    from tinydb import Query, TinyDB
except ImportError:
    print("TinyDB not installed. Skipping check.")
    sys.exit(0)


def ensure_root_identity():
    # 1. Resolve Path
    project_root = Path(__file__).resolve().parent.parent.parent
    db_path = project_root / "data" / "db.json"

    if not db_path.exists():
        print(f"[Identity] DB not found at {db_path}. Skipping.")
        return

    db = TinyDB(db_path, encoding="utf-8")
    users_table = db.table("users")
    User = Query()

    # 2. Check for Correct Root (root_master)
    root_master = users_table.get(User.slug == "root_master")
    if root_master:
        print("[Identity] ✅ Root user 'root_master' exists. No action needed.")
        return

    # 3. Check for Legacy Root (uid="1")
    legacy_root = users_table.get(User.id == "1")
    if legacy_root:
        print("[Identity] ⚠️ Found Legacy Root (ID 1). Migrating to 'root_master'...")
        # Update Slug
        users_table.update({"slug": "root_master"}, User.id == "1")
        print("[Identity] ✅ Migration complete.")
        return

    # 4. If neither exists, Create Surgical Root (Minimal)
    print("[Identity] ❌ No Root user found. Creating surgical backup...")

    # Minimal Root User (matches seed_data.json structure)
    surgical_root = {
        "id": "10fb2f60-5ee1-419f-a16c-b5cfdfc5f55b", # Match the uuid in seed_data.json
        "slug": "root_master",
        "email": "root@example.com",
        "display_name": "System Root",
        "role": "ROOT",
        "organization_id": "436d84de-c526-43b7-93ef-634912be0d2f", # Match seed_data.json org
        "is_active": True,
        "language": "fi",
        "theme_mode": "system",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "created_by": "system_bootstrap",
    }

    users_table.insert(surgical_root)
    print("[Identity] ✅ Surgically restored 'root_master'.")


if __name__ == "__main__":
    ensure_root_identity()

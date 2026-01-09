import json
import os


def check_integrity(db_path, env_name):
    print(f"\n--- Checking Integrity: {env_name} ---")
    if not os.path.exists(db_path):
        print(f"[SKIP] Database file not found: {db_path}")
        return

    try:
        with open(db_path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"[ERROR] Could not load DB: {e}")
        return

    # TinyDB structure normalization
    # If tables are keys, use them.
    # Note: verifier.py logic handled TinyDB specific structure {_default: ...} vs direct keys.
    # Our seeder writes direct keys for tables.

    tables = list(data.keys())
    print(f"Found Tables: {tables}")

    # 1. Check for Unknown Tables
    KNOWN_TABLES = {
        "organizations",
        "users",
        "system_config",
        "components",
        "steps",
        "workflows",
        "knowledge_base",
        "dimensions",
        "banned_phrases",
        "model_registry",
        "_default",
    }

    extras = set(tables) - KNOWN_TABLES
    if extras:
        print(f"[WARN] Unknown tables found (potential orphans): {extras}")
    else:
        print("[OK] No unknown tables found.")

    # 2. Referential Integrity: Users -> Organizations
    orgs = data.get("organizations", {})
    users = data.get("users", {})

    # Normalize to dict if list (Seed vs DB structure matters)
    # TinyDB usually stores as dict of "1": {...}, "2": {...}
    if isinstance(orgs, dict):
        org_ids = set()
        for _k, v in orgs.items():
            if isinstance(v, dict) and "id" in v:
                org_ids.add(v["id"])
    else:
        # Assuming list
        org_ids = set(o.get("id") for o in orgs)

    orphans = []
    if isinstance(users, dict):
        for _k, u in users.items():
            if isinstance(u, dict):
                user_org = u.get("organization_id")
                if user_org and user_org not in org_ids:
                    orphans.append(f"User {u.get('uid')} -> {user_org}")

    if orphans:
        print(f"[FAIL] Found {len(orphans)} orphaned users (pointing to non-existent orgs):")
        for o in orphans:
            print(f"  - {o}")
    else:
        print(f"[OK] All users link to valid organizations ({len(org_ids)} orgs).")


if __name__ == "__main__":
    check_integrity("data/db.json", "PRODUCTION (TinyDB)")
    check_integrity("backend/database/db_mock.json", "MOCK (TinyDB)")

"""Seed Via API Tool."""

import json
import os
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from backend.main import app  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

# Experiment Settings
DB_PATH = project_root / "data" / "db_api_seeded.json"


def run_experiment():
    """Run the API seeding experiment."""
    print("--- API Seeding Tool ---")
    print(f"Target DB: {DB_PATH}")

    # 1. Clean Slate
    if DB_PATH.exists():
        os.remove(DB_PATH)
        print("[Setup] Removed existing target DB.")

    # 2. Configure Environment (Force Mock + Local DB Path)
    os.environ["USE_MOCK_DB"] = "true"  # Ensure we use TinyDB logic
    os.environ["START_DB_PATH"] = str(DB_PATH)

    # Reset Caches to ensure new DB path is respected
    from backend import settings

    settings.get_settings.cache_clear()

    from backend import dependencies

    dependencies.get_db_client_dep.cache_clear()

    # 3. Initialize Client (Triggers Startup -> ensure_root_user)
    print("[Setup] Initializing TestClient...")
    with TestClient(app) as client:
        # 4. Auth Header (Mock Mode: Token = UID)
        auth_headers = {"Authorization": "Bearer root_master"}

        # 5. Load Seed Data
        seed_path = project_root / "backend" / "seed" / "seed_data.json"
        if not seed_path.exists():
            print(f"[Error] Seed data not found at {seed_path}")
            return

        with open(seed_path, encoding="utf-8") as f:
            seed_data = json.load(f)

        print("[Action] Reading seed_data.json...")

        # 6. Seed Organizations
        orgs = seed_data.get("organizations", [])
        for org in orgs:
            if org["id"] == "system":
                print("  [Skip] Skipping 'system' org (bootstrapped).")
                continue

            print(f"  [POST] Creating Organization: {org['name']} (ID: {org['id']})")
            payload = {
                "id": org["id"],
                "name": org["name"],
                "tier": org["tier"] if "tier" in org else "standard",
                "contact_email": org["contact_email"],
                "billing_id": org.get("billing_id"),
                "subscription_status": org.get("subscription_status", "trial"),
                "quota_limit": org.get("quota_limit", 100),
                "settings_override": {},
            }
            resp = client.post("/organizations", json=payload, headers=auth_headers)
            if resp.status_code in (200, 201):
                print(f"    [OK] Created. Response ID: {resp.json()['id']}")
            else:
                print(f"    [FAIL] {resp.status_code} - {resp.text}")

        # 7. Seed Users
        users = seed_data.get("users", [])
        created_users_map = {}  # seed_uid -> real_uid

        for user in users:
            if user["uid"] == "root_master":
                continue

            target_org = user["organization_id"]
            print(f"  [POST] Creating User: {user['display_name']} ({user['role']}) -> {target_org}")

            user_payload = {
                "email": user["email"],
                "display_name": user["display_name"],
                "role": user["role"],
                "password": "password123",  # Dummy password
            }

            # API endpoint for user creation: /organizations/{org_id}/users
            resp = client.post(f"/organizations/{target_org}/users", json=user_payload, headers=auth_headers)

            if resp.status_code in (200, 201):
                new_user = resp.json()
                print(f"    [OK] Created. UID: {new_user['uid']}")
                created_users_map[user["uid"]] = new_user["uid"]
            else:
                print(f"    [FAIL] {resp.status_code} - {resp.text}")

    # 8. Verification Report
    print("\n--- Seeding Results ---")
    if os.path.exists(DB_PATH):
        print(f"[Success] Database file created at {DB_PATH}")
        with open(DB_PATH, encoding="utf-8") as f:
            db_content = json.load(f)

        # Check Orgs
        org_count = len(db_content.get("organizations", {}))
        print(f"Total Organizations in DB: {org_count}")

        # Check Users
        user_count = len(db_content.get("users", {}))
        print(f"Total Users in DB: {user_count}")

    else:
        print("[Fail] Database file was NOT created.")


if __name__ == "__main__":
    run_experiment()

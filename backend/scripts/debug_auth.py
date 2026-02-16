
import asyncio
import os
import sys
from pathlib import Path

# Setup Path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Simulate run_local.bat Environment
os.environ["USE_MOCK_DB"] = "false"
os.environ["STORAGE_BACKEND"] = "LOCAL"
os.environ["USE_FIREBASE_AUTH"] = "true"
# Minimal required for settings validtion
os.environ["GOOGLE_API_KEY"] = "dummy"
os.environ["VERTEX_PROJECT_ID"] = "dummy"

from backend.database.wrapper import get_db_client
from backend.services.auth import AuthService
from backend.settings import get_settings


async def main():
    print("--- DEBUG AUTH ---")
    settings = get_settings()
    print(f"Settings: UseMockDB={settings.use_mock_db}, Backend={settings.active_backend}, FirebaseAuth={settings.use_firebase_auth}")
    print(f"DB Path: {settings.prod_db_path}")

    # 1. Initialize DB
    try:
        db_client = get_db_client()
        print("DB Client initialized.")
    except Exception as e:
        print(f"DB Init Failed: {e}")
        return

    # 2. Check User in DB directly
    try:
        users_table = db_client.table("users")
        all_users = users_table.all()
        print(f"Found {len(all_users)} users in DB.")

        target_uid = "admin_1"
        found = False
        for u in all_users:
            if u.get("uid") == target_uid:
                print(f"✅ User '{target_uid}' FOUND in DB. Role: {u.get('role')}")
                found = True
                break

        if not found:
            print(f"❌ User '{target_uid}' NOT FOUND in DB!")
    except Exception as e:
        print(f"DB Access Failed: {e}")

    # 3. Initialize AuthService
    try:
        auth_service = AuthService(db_client, use_firebase=settings.use_firebase_auth)
        print("AuthService initialized.")
    except Exception as e:
        print(f"AuthService Init Failed: {e}")
        return

    # 4. Verify Token
    token = f"mock-token:{target_uid}"
    print(f"Verifying token: {token}")
    try:
        user_data = auth_service.verify_token(token)
        print(f"✅ Token Verified! User: {user_data}")
    except Exception as e:
        print(f"❌ Token Verification Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())

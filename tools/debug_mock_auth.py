import sys
import os
import logging

# 1. Set Env Vars to FORCE MOCK DB
os.environ["USE_MOCK_DB"] = "true"
os.environ["STORAGE_BACKEND"] = "LOCAL"
os.environ["USE_MOCK_LLM"] = "true"

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.dependencies import get_auth_service
from backend.services.auth import AuthService
from backend.database.wrapper import TinyDBClient
from backend.settings import get_settings

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_mock_auth():
    print("--- Debugging MOCK Auth (Force Populate) ---")
    settings = get_settings()
    print(f"USE_MOCK_DB: {settings.use_mock_db}")
    print(f"Settings DB Path: {settings.start_db_path}")
    
    # Initialize DB Client
    db_client = TinyDBClient(settings.start_db_path)
    
    # Init Service (this should trigger ensure_root_user)
    print("Initializing AuthService...")
    auth_service = AuthService(db_client, use_firebase=False)
    
    # Explicitly call ensure_root_user just in case dependencies didn't (though constructor doesn't call it, dependencies.py does)
    print("Calling ensure_root_user()...")
    user = auth_service.ensure_root_user()
    print(f"Ensure Root Result: {user.uid} / {user.role}")
    
    token = "mock-token:root_master"
    print(f"Verifying token: {token}")
    
    try:
        user_data = auth_service.verify_token(token)
        print("SUCCESS! Token Verified in Mock DB.")
        print(user_data)
    except Exception as e:
        print(f"FAILURE: {e}")

if __name__ == "__main__":
    debug_mock_auth()

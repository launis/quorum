import sys
import os
import logging

# 1. Set Env Vars BEFORE importing backend modules
os.environ["USE_MOCK_DB"] = "false"
os.environ["STORAGE_BACKEND"] = "LOCAL"
os.environ["USE_MOCK_LLM"] = "false"

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.dependencies import get_auth_service
from backend.services.auth import AuthService
from backend.database.wrapper import TinyDBClient
from backend.settings import get_settings

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_auth():
    print("--- Debugging Auth ---")
    settings = get_settings()
    print(f"Settings DB Path: {settings.start_db_path}")
    
    # Initialize DB Client manually to ensure we control it
    # strict logic from main.py/dependencies.py
    db_client = TinyDBClient(settings.start_db_path)
    
    auth_service = AuthService(db_client, use_firebase=False)
    
    token = "mock-token:root_master"
    print(f"Verifying token: {token}")
    
    try:
        user_data = auth_service.verify_token(token)
        print("SUCCESS! Token Verified.")
        print(user_data)
        
        # Double check role
        print(f"Role: {user_data.role}")
        
    except ValueError as e:
        print(f"FAILURE: ValueError caught: {e}")
    except Exception as e:
        print(f"FAILURE: Unexpected exception: {e}")

    # Check directly from Repo
    print("\n--- Direct Repo Check ---")
    user = auth_service.repo.get_by_uid("root_master")
    if user:
        print(f"User found in Repo: {user.uid}, Role: {user.role}, Org: {user.organization_id}")
    else:
        print("User NOT found in Repo.")

if __name__ == "__main__":
    debug_auth()

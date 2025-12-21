
import os
import sys

# Setup Path
sys.path.append(os.getcwd())
# Force Real DB
os.environ['DB_PATH'] = r'c:\Users\risto\OneDrive\quorum\data\db.json'
os.environ['MOCK_DB'] = 'false'

from backend.database.wrapper import get_db_client
from backend.database.repository import TinyDBRepository
from backend.services.agent_registry import AgentRegistry

try:
    print("--- 1. Init Registry ---")
    db = get_db_client()
    repo = TinyDBRepository(db)
    registry = AgentRegistry(repo)
    
    print("\n--- 2. Resolve 'deep' ---")
    try:
        res = registry.resolve_model_name("deep")
        print(f"Result for 'deep': '{res}'")
        
        # Also get Full Config
        conf = registry.resolve_model_config("deep")
        print(f"Config for 'deep': {conf}")
        
    except Exception as e:
        print(f"Error resolving deep: {e}")

    print("\n--- 3. Resolve 'fast' ---")
    try:
        res = registry.resolve_model_name("fast")
        print(f"Result for 'fast': '{res}'")
    except Exception as e:
        print(f"Error resolving fast: {e}")

except Exception as e:
    print(f"Fatal Error: {e}")


import os
import sys

# Add project root to sys.path
sys.path.append(os.getcwd())

from backend.config import USE_MOCK_DB, DB_PATH
from backend.database.wrapper import get_db_client

print(f"DEBUG: USE_MOCK_DB={USE_MOCK_DB}")
print(f"DEBUG: DB_PATH={os.path.abspath(DB_PATH)}")

try:
    db = get_db_client()
    executions = db.table('executions').all()
    print(f"DEBUG: Executions found: {len(executions)}")
    for ex in executions:
        print(f" - ID: {ex.get('execution_id')}, Status: {ex.get('status')}, Start: {ex.get('start_time')}")
except Exception as e:
    print(f"ERROR: {e}")

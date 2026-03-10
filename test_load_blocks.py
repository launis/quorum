import sys
import os

# Ensure backend_v2 is in path
sys.path.append(os.path.abspath("."))

from backend_v2.database.repository import TinyDBWorkflowRepository

try:
    repo = TinyDBWorkflowRepository("backend_v2/db_v2.json")
    blocks = repo.get_all_prompt_blocks()
    print(f"Loaded {len(blocks)} blocks successfully")
except Exception as e:
    print("VALIDATION ERROR:")
    print(e)

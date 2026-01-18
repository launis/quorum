
import asyncio
import logging
import os
import sys

# Add project root to path
sys.path.append(os.getcwd())

from backend.database.wrapper import TinyDBClient
from tinydb import Query

# Mock settings path logic
DB_PATH = os.path.join("data", "db.json")

def test_lookup():
    print(f"Testing lookup in {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("DB file not found!")
        return

    client = TinyDBClient(DB_PATH)
    users_table = client.table("users")
    
    # Method 1: Lambda
    print("\n--- Testing Lambda Lookup ---")
    try:
        user_lambda = users_table.get(lambda x: x.get("uid") == "root_master")
        print(f"Result (Lambda): {user_lambda}")
    except Exception as e:
        print(f"Error (Lambda): {e}")

    # Method 2: Query
    print("\n--- Testing Query Lookup ---")
    try:
        User = Query()
        user_query = users_table.get(User.uid == "root_master")
        print(f"Result (Query): {user_query}")
    except Exception as e:
        print(f"Error (Query): {e}")

    # Method 3: Search (for sanity)
    print("\n--- Testing Search (Lambda) ---")
    try:
        results = users_table.search(User.uid == "root_master")
        print(f"Result (Search): Found {len(results)} items")
    except Exception as e:
        print(f"Error (Search): {e}")

if __name__ == "__main__":
    test_lookup()

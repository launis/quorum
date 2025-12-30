
import sys
import os
import traceback

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("Diagnostics for agents_router...")
try:
    print("Importing backend.database.wrapper...")
    from backend.database.wrapper import AbstractDatabase
    print(f"AbstractDatabase imported: {AbstractDatabase}")
except Exception:
    print("Failed to import AbstractDatabase")
    traceback.print_exc()

try:
    print("Importing backend.api.agents_router...")
    import backend.api.agents_router
    print("OK: agents_router")
except Exception:
    print("FAIL: agents_router")
    traceback.print_exc()

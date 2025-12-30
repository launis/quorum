
import sys
import os
import traceback

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("Diagnostics for Config Router...")
try:
    print("Importing backend.api.config_router...")
    import backend.api.config_router
    print("OK: config_router")
except Exception:
    print("FAIL: config_router")
    traceback.print_exc()

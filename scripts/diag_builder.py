
import sys
import os
import traceback

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("Diagnostics for builder_router...")
try:
    print("Importing backend.api.builder_router...")
    import backend.api.builder_router
    print("OK: builder_router")
except Exception:
    print("FAIL: builder_router")
    traceback.print_exc()

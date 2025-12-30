
import sys
import os
import traceback

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

api_modules = [
    "backend.api.admin_router",
    "backend.api.agents_router",
    "backend.api.builder_router",
    "backend.api.config_router",
    "backend.api.execution_router",
    "backend.api.llm_router",
    "backend.api.tools_router",
    "backend.main"
]

print("Starting diagnostics...")
for mod in api_modules:
    try:
        print(f"Importing {mod}...")
        __import__(mod)
        print(f"OK: {mod}")
    except Exception:
        print(f"FAIL: {mod}")
        traceback.print_exc()
        # Don't exit, try next

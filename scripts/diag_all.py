"""Diagnostic Script for Backend Modules."""
import os
import sys
import traceback

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

modules = [
    "backend.api.admin_router",
    "backend.api.agents_router",
    "backend.api.builder_router",
    "backend.api.config_router",
    "backend.api.execution_router",
    "backend.api.llm_router",
    "backend.api.tools_router",
    "backend.main",
]

print("Starting FULL diagnostics...")
for mod in modules:
    print(f"--- Importing {mod} ---")
    try:
        __import__(mod)
        print(f"OK: {mod}")
    except Exception:
        print(f"FAIL: {mod}")
        traceback.print_exc()


import sys
import os

# Ensure backend module can be found
sys.path.append("c:/src/quorum")

from backend.main import app

print("--- Registered Routes ---")
for route in app.routes:
    if hasattr(route, "methods"):
        print(f"{route.path} {route.methods}")
    else:
        print(f"{route.path}")
print("-------------------------")

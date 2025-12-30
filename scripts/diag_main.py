
import sys
import os
import traceback

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("Diagnostics for Main...")
try:
    print("Importing backend.main...")
    import backend.main
    print("OK: main")
except Exception:
    print("FAIL: main")
    traceback.print_exc()

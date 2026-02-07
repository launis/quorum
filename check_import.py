
import sys
import os
sys.path.append(os.getcwd())

try:
    print("Importing backend.database.repository...")
    import backend.database.repository
    print("Import OK")
except Exception as e:
    print(f"Import Failed: {e}")
    import traceback
    traceback.print_exc()

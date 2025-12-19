import sys
import os

sys.path.append(os.getcwd())

print("Importing domain...")
try:
    from backend.models import domain
    print("Domain imported successfully.")
except Exception as e:
    print(f"Domain import failed: {e}")
    import traceback
    traceback.print_exc()

print("Importing state...")
try:
    from backend.models import state
    print("State imported successfully.")
except Exception as e:
    print(f"State import failed: {e}")
    import traceback
    traceback.print_exc()

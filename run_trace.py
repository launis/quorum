import traceback
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from backend_v2.scripts.migrate_v1_to_v2 import migrate_seeds
    migrate_seeds()
except Exception:
    with open("trace.txt", "w") as f:
        traceback.print_exc(file=f)
print("Trace written to trace.txt")

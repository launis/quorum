
import sys
import traceback
from pathlib import Path

# Setup Path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

log_file = project_root / "import_error.log"

print(f"DEBUG: Importing backend.main... Logging to {log_file}")
try:
    from backend.main import app
    print("SUCCESS: backend.main imported successfully!")
    with open(log_file, "w") as f:
        f.write("SUCCESS")
except ImportError as e:
    print(f"FAILURE: ImportError: {e}")
    with open(log_file, "w") as f:
        f.write(f"ImportError: {e}\n")
        traceback.print_exc(file=f)
except Exception as e:
    print(f"FAILURE: Unexpected Error: {e}")
    with open(log_file, "w") as f:
        f.write(f"Unexpected Error: {e}\n")
        traceback.print_exc(file=f)

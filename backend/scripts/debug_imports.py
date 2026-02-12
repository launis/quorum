
import sys
from pathlib import Path

# Setup Path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print("DEBUG: Importing backend.main...")
try:
    from backend.main import app
    print("SUCCESS: backend.main imported successfully!")
except ImportError as e:
    print(f"FAILURE: ImportError: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"FAILURE: Unexpected Error: {e}")
    import traceback
    traceback.print_exc()

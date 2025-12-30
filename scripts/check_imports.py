
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    print("Checking imports...")
    from backend.api import admin_router
    print("[OK] admin_router imported")
    import sys
    if 'backend.database.wrapper' in sys.modules:
        import backend.database.wrapper
        print(f"Wrapper dir: {dir(backend.database.wrapper)}")
    from backend.api import agents_router
    print("[OK] agents_router imported")
    from backend.api import builder_router
    print("[OK] builder_router imported")
    from backend.api import config_router
    print("[OK] config_router imported")
    from backend.api import execution_router
    print("[OK] execution_router imported")
    from backend.api import llm_router
    print("[OK] llm_router imported")
    from backend.api import tools_router
    print("[OK] tools_router imported")
    # workflows_router removed
    from backend import main
    print("[OK] main imported")
    
    print("\nAll router modules imported successfully!")

except Exception as e:
    print(f"\n[FAIL] Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

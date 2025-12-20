import sys
import os
import importlib

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def verify_import_cleanliness():
    print("--- Verifying Imports ---")
    try:
        import backend.config
        print("❌ FAILURE: backend.config was imported! It should be deleted.")
    except ImportError:
        print("✅ SUCCESS: backend.config could not be imported (as expected).")
    except Exception as e:
        print(f"⚠️ Unexpected error importing backend.config: {e}")

def verify_settings_load():
    print("\n--- Verifying Settings Load ---")
    try:
        from backend.settings import get_settings
        settings = get_settings()
        print(f"✅ Settings Loaded Successfully.")
        print(f"   - USE_MOCK_LLM: {settings.use_mock_llm}")
        print(f"   - USE_MOCK_DB: {settings.use_mock_db}")
        print(f"   - DB Path: {settings.start_db_path}")
    except Exception as e:
        print(f"❌ FAILURE: Could not load settings: {e}")

if __name__ == "__main__":
    verify_settings_load()
    verify_import_cleanliness()

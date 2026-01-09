import os

from backend.settings import get_settings

print("--- DEBUG SETTINGS ---")
print(f"CWD: {os.getcwd()}")
print(f"Files in CWD: {[f for f in os.listdir('.') if '.env' in f]}")

settings = get_settings()
print(f"Settings.vertex_location: '{settings.vertex_location}'")
print(f"Settings.data_dir: '{settings.data_dir}'")
print(f"Start DB Path: '{settings.start_db_path}'")

if settings.vertex_location == "us-central1":
    print("❌ FAILURE: defaulting to us-central1 (did not load .env)")
elif settings.vertex_location == "europe-north1":
    print("✅ SUCCESS: loaded europe-north1 from .env")
else:
    print(f"❓ UNKNOWN: '{settings.vertex_location}'")

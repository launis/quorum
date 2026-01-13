
try:
    from backend.api.admin_router import router
    print("Import Successful")
except Exception as e:
    print(f"Import Failed: {e}")
    import traceback
    traceback.print_exc()

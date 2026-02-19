
try:
    from backend.models.domain import JudgeDTO
    print("SUCCESS: JudgeDTO imported successfully.")
except ImportError as e:
    print(f"FAILURE: {e}")
    exit(1)

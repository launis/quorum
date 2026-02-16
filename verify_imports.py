
try:
    from backend.models.domain.profiler import BehavioralMetrics, TextMetrics
    print("Import successful")
    bm = BehavioralMetrics()
    print(f"Model created: {bm}")
except Exception as e:
    print(f"Import failed: {e}")

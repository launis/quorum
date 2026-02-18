from pydantic import ValidationError
from backend.models.domain.logician import CognitiveLevel
from backend.models.enums import BloomLevel, StrategicDepth

try:
    print("Test 1: Enum Instance (Like in Integration Test)")
    c1 = CognitiveLevel(
        bloom_level=BloomLevel.CREATING,
        strategic_depth=StrategicDepth.HIGH,
        bloom_score=6.0,
        strategic_score=3.0
    )
    print("SUCCESS: Test 1 passed.")
except Exception as e:
    print(f"FAIL: Test 1 failed with {e}")

try:
    print("\nTest 2: String Value (Like in DB/JSON)")
    c2 = CognitiveLevel(
        bloom_level="BLOOM_CREATING",
        strategic_depth="STRAT_HIGH",
        bloom_score=6.0,
        strategic_score=3.0
    )
    print("SUCCESS: Test 2 passed.")
except ValidationError as e:
    print(f"FAIL: Test 2 failed with ValidationError:\n{e}")
except Exception as e:
    print(f"FAIL: Test 2 failed with {type(e).__name__}: {e}")

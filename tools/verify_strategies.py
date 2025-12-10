import requests
import json

API_URL = "http://localhost:8000"

def test_strategies():
    print("Testing /config/models/strategies endpoint...")
    try:
        res = requests.get(f"{API_URL}/config/models/strategies")
        if res.status_code == 200:
            strategies = res.json()
            print("SUCCESS: Retrieved strategies:")
            print(json.dumps(strategies, indent=2))
            
            # Verify structure
            assert "fast" in strategies
            assert "deep" in strategies
            assert strategies["fast"]["model"] == "gemini-2.0-flash-exp"
            assert strategies["deep"]["model"] == "gemini-2.0-flash-thinking-exp-1219"
            print("VERIFIED: Strategy structure matches expectations.")
        else:
            print(f"FAILURE: Status code {res.status_code}")
            print(res.text)
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_strategies()

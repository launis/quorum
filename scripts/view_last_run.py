"""View details of the last execution."""

import json
import sys

import requests

BASE_URL = "http://localhost:8000"
exec_id = "0bb04134-79b3-4e15-81cb-abfb44de3db8"

try:
    print(f"Fetching execution {exec_id} from {BASE_URL}...")
    resp = requests.get(f"{BASE_URL}/executions/{exec_id}")

    if resp.status_code != 200:
        print(f"Error: API returned {resp.status_code}")
        print(resp.text)
        sys.exit(1)

    data = resp.json()
    # API returns generic response structure usually? Or directly the obj?
    # Usually: {"id":..., "status":..., "result":...}

    execution = data
    print(f"Execution Keys: {list(execution.keys())}")
    result = execution.get("result", {})
    if not result:
        print("Result object is empty or None!")
        # Try finding state or steps elsewhere
        for k, v in execution.items():
            if isinstance(v, dict) and "step_" in str(v):
                print(f"Found potential steps in key {k}")
    else:
        print(f"Result Keys: {list(result.keys())}")

    # 1. Coach References
    print("\n--- COACH REFERENCES ---")
    if "step_coach" in result:
        refs = result["step_coach"].get("lahdeluettelo", [])
        for r in refs:
            print(f"- {r}")
    else:
        print("No Coach step found.")

    # 2. Archivist Cases
    print("\n--- ARCHIVIST CASES ---")
    if "step_archivist" in result:
        cases = result["step_archivist"].get("viitatut_ennakkotapaukset", [])
        for c in cases:
            print(f"- {c}")
        rec = result["step_archivist"].get("suositus_tuomarille", "")
        print(f"\nRecommendation: {rec[:200]}...")
    else:
        print("No Archivist step found.")

    # 3. Judge Score
    print("\n--- JUDGE SCORE ---")
    if "step_judge" in result:
        pisteet = result["step_judge"].get("pisteet", {})
        print(json.dumps(pisteet, indent=2, ensure_ascii=False))

except Exception as e:
    print(f"Error: {e}")


import json

SEED_PATH = r"c:\src\quorum\backend\seed\seed_data.json"

def verify():
    print(f"Checking {SEED_PATH}...")
    try:
        with open(SEED_PATH, encoding="utf-8") as f:
            data = json.load(f)

        steps = data.get("steps", [])
        print(f"Found {len(steps)} steps in root 'steps' array.")

        missing = []
        for step in steps:
            sid = step.get("id")
            config = step.get("config", {})
            schema = config.get("output_schema")

            if schema:
                print(f"[OK] {sid}: {schema}")
            else:
                print(f"[FAIL] {sid}: Missing output_schema")
                missing.append(sid)

        if missing:
             print(f"\nFAILED: {len(missing)} steps missing output_schema: {missing}")
             exit(1)
        else:
             print("\nSUCCESS: All steps have output_schema.")
             exit(0)

    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    verify()

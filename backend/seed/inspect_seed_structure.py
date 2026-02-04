
import json

SEED_PATH = r"c:\src\quorum\backend\seed\seed_data.json"

try:
    with open(SEED_PATH, encoding="utf-8") as f:
        data = json.load(f)

    workflows = data.get("workflows", [])
    print(f"Found {len(workflows)} workflows.")

    if workflows:
        first_wf = workflows[0]
        steps = first_wf.get("steps", [])
        print(f"First workflow ID: {first_wf.get('id')}")
        print(f"Steps count: {len(steps)}")
        if steps:
            first_step = steps[0]
            print(f"First step type: {type(first_step)}")
            if isinstance(first_step, dict):
                print(f"First step keys: {list(first_step.keys())}")
                if "inputs" in first_step:
                     print(f"First step inputs: {first_step['inputs']}")
            else:
                print(f"First step value: {first_step}")

except Exception as e:
    print(f"Error: {e}")

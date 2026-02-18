
import json

with open("backend/seed/seed_data.json", "r", encoding="utf-8") as f:
    lines = f.readlines()

found = False
for i, line in enumerate(lines):
    if '"components":' in line:
        print(f"FOUND 'components': at line {i+1}")
        found = True
        break

if not found:
    print("KEY 'components': NOT FOUND")
    # Check top level keys
    try:
        data = json.loads("".join(lines))
        print(f"Top Level Keys: {list(data.keys())}")
    except Exception as e:
        print(f"JSON Parse Error: {e}")

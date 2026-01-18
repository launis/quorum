import json
import os

path = r"c:\src\quorum\backend\seed\seed_data.json"

if not os.path.exists(path):
    print("File not found.")
    exit()

with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Top level keys: {list(data.keys())}")

if "workflows" in data:
    wfs = data["workflows"]
    print(f"Workflows count: {len(wfs)}")
    for i, wf in enumerate(wfs):
        print(f"[{i}] ID: {wf.get('id')} | Name: {wf.get('name')}")
else:
    print("No 'workflows' key found.")

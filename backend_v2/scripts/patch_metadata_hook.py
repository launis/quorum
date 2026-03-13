import json

DATA_PATH = r"c:\src\quorum\backend_v2\seed\seed_data.json"

with open(DATA_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

for wf in data.get("workflows", []):
    if wf["id"] == "workflow_courtroom_20_full_audit":
        for step in wf.get("steps", []):
            if "pre_hooks" not in step:
                step["pre_hooks"] = []
            if "inject_step_metadata" not in step["pre_hooks"]:
                step["pre_hooks"].append("inject_step_metadata")

with open(DATA_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Injected 'inject_step_metadata' into all steps of workflow_courtroom_20_full_audit")

import json

DATA_PATH = r"c:\src\quorum\backend_v2\seed\seed_data.json"

with open(DATA_PATH, encoding="utf-8") as f:
    data = json.load(f)

for block in data.get("prompt_blocks", []):
    if block.get("type") not in ["float", "int", "string"]:
        if block.get("allow_decimals") is True:
            block["allow_decimals"] = False

for wf in data.get("workflows", []):
    if wf.get("id") == "workflow_courtroom_20_full_audit":
        for step in wf.get("steps", []):
            if "pre_hooks" not in step:
                step["pre_hooks"] = []
            if "inject_step_metadata" not in step["pre_hooks"]:
                step["pre_hooks"].append("inject_step_metadata")

with open(DATA_PATH, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Fixed allow_decimals and re-injected metadata hook.")

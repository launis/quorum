import json

path = r"c:\src\quorum\backend_v2\seed\seed_data.json"
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

removed = 0
for wf in data.get("workflows", []):
    if "render_blueprint" in wf:
        del wf["render_blueprint"]
        removed += 1
    if "render_blueprints" in wf:
        del wf["render_blueprints"]
        removed += 1

with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print(f"Removed {removed} occurrences of render_blueprint(s) from workflows.")

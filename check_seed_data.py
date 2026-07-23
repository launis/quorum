import json
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

with open("backend_v2/seed/seed_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for wf in data.get("workflows", []):
    for pid, profile in wf.get("output_profiles", {}).items():
        for i, layout in enumerate(profile.get("layouts", [])):
            print(f"Profile {pid} Layout {i}:")
            print("  matrix_column_labels:", json.dumps(layout.get("matrix_column_labels"), ensure_ascii=False))
            print("  extension_labels:", json.dumps(layout.get("extension_labels"), ensure_ascii=False))

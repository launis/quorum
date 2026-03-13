import json

SEED_FILE = r"C:\src\quorum\backend_v2\seed\seed_data.json"
with open(SEED_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

for bp in data.get("task_blueprints", []):
    print(f"Blueprint: {bp['id']} -> Prompts: {bp.get('prompt_blocks', [])}")

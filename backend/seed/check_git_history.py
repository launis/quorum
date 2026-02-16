import json
import subprocess


def get_file_content(commit_ref):
    try:
        cmd = ["git", "show", f"{commit_ref}:backend/seed/seed_data.json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Error fetching {commit_ref}: {e}")
        return None

def extract_instructions(data):
    instructions = {}
    items = data if isinstance(data, list) else []
    if isinstance(data, dict):
         for key in ["instructions", "mandates", "rules", "tasks", "steps", "workflows", "components"]:
             items.extend(data.get(key, []))

    for item in items:
        if isinstance(item, dict) and 'id' in item:
            instructions[item['id']] = item.get('content', '')

    return instructions

head_data = get_file_content("HEAD")
prev_data = get_file_content("HEAD~1") # Or maybe HEAD~5 depending on when it was removed?

if head_data and prev_data:
    head_instr = extract_instructions(head_data)
    prev_instr = extract_instructions(prev_data)

    all_ids = set(head_instr.keys()) | set(prev_instr.keys())

    print("Checking for REMOVED SCALE constraints in modified instructions:")

    for iid in sorted(list(all_ids)):
        h_content = head_instr.get(iid, "")
        p_content = prev_instr.get(iid, "")

        # Check if content CHANGED and "scale" or "asteikko" was potentially removed
        if h_content != p_content:
            if ("scale" in p_content.lower() or "asteikko" in p_content.lower()):
                print(f"\n[CHANGED] {iid}:")
                print(f"  PREV: {p_content[:100]}...")
                print(f"  HEAD: {h_content[:100]}...")

                # Simple diff check
                if "scale" not in h_content.lower() and "asteikko" not in h_content.lower():
                     print("  WARNING: Scale keywords REMOVED from HEAD version!")

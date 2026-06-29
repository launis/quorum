import json

with open("c:/src/quorum/data/db_v2.json", encoding="utf-8") as f:
    db = json.load(f)

workflows = db.get("workflows", {})
for wf_id, wf in workflows.items():
    print(f"Workflow: {wf.get('name', {}).get('fi', wf_id)}")
    for step in wf.get("steps", []):
        for block in step.get("prompt_blocks", []):
            name = block.get("name", {}).get("fi", "Unknown")
            instruction = block.get("instructions", "")
            print(f"  - Block: {name}")
            if (
                "sävy" in instruction.lower()
                or "päättely" in instruction.lower()
                or "rivien" in instruction.lower()
                or "sävy" in name.lower()
                or "strategia" in name.lower()
                or "riski" in name.lower()
            ):
                print(f"    [SUGGESTION] Good for contextual override! (Instruction: {instruction[:100]}...)")

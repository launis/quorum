import json
from pathlib import Path
from datetime import datetime

def main():
    seed_path = Path(r"c:\src\quorum\backend_v2\seed\seed_data.json")
    backup_dir = Path(r"c:\src\quorum\backend_v2\seed\backups")
    backup_dir.mkdir(exist_ok=True, parents=True)

    # 1. Backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"seed_data_pre_strictness_removal_{timestamp}.json"
    backup_path.write_bytes(seed_path.read_bytes())
    print(f"Backed up to {backup_path}")

    # 2. Modify
    with open(seed_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    count = 0
    for pb in data.get("prompt_blocks", []):
        if "strictness_level" in pb:
            del pb["strictness_level"]
            count += 1

    with open(seed_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"Removed strictness_level from {count} prompt blocks.")

if __name__ == "__main__":
    main()

import json
import os
import shutil
from datetime import datetime

SEED_DIR = r"c:\src\quorum\backend_v2\seed"
SEED_FILE = os.path.join(SEED_DIR, "seed_data.json")
BACKUPS_DIR = os.path.join(SEED_DIR, "backups")
os.makedirs(BACKUPS_DIR, exist_ok=True)

# 1. Create a timestamped backup
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_file = os.path.join(BACKUPS_DIR, f"seed_data_backup_causality_{timestamp}.json")
shutil.copy2(SEED_FILE, backup_file)

# 2. Load the seed data
with open(SEED_FILE, encoding="utf-8") as f:
    data = json.load(f)

new_profile = {
    "name": {
        "fi": "Kausaliteetti ja Rehellisyys (Itsekritiikin 3D)",
        "en": "Causality and Honesty (Self-Criticism 3D)"
    },
    "layouts": [
        {
            "preset_view": "3d_complex",
            "steps": [],
            "target_blocks": [
                "blk_a8e356b276f04ddeb7cc3a0eec58daf6", # Abduktiivinen Päättely (Pearl) / Post-Hoc vs Real Strategy
                "blk_635d07ae441d41e6a274911854ef8283", # Tekstin omat rajoitteet
                "blk_2878d1c8b5494180b1a5231466e2e0a9"  # Läpinäkyvyys
            ],
            "show_text": True
        }
    ]
}

mutated = False
for workflow in data.get("workflows", []):
    if workflow.get("slug") == "kokonaisvaltainen_auditointi":
        profiles = workflow.get("output_profiles", {})
        profiles["causality_synthesis"] = new_profile
        mutated = True

if mutated:
    with open(SEED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Suoritettu! Luotu kausaliteetti-tulostusmäärittely.")

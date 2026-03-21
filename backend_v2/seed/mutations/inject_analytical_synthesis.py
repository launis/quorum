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
backup_file = os.path.join(BACKUPS_DIR, f"seed_data_backup_combinations_{timestamp}.json")
shutil.copy2(SEED_FILE, backup_file)

# 2. Load the seed data
with open(SEED_FILE, encoding="utf-8") as f:
    data = json.load(f)

new_profile = {
    "name": {
        "fi": "Kokonaisvaltainen Synteesi: Kognitio, Riskit ja Vääristymät",
        "en": "Holistic Synthesis: Cognition, Risks & Biases"
    },
    "layouts": [
        {
            "preset_view": "3d_complex",
            "steps": [], # Legacy requirement fallback, keeping empty if possible, or listing steps? V2 handles layout matching independent of this, but backend_v2 might need all steps if we don't use 'target_blocks'? Actually, we use 'target_blocks'.
            "target_blocks": [
                "blk_371c7724eeba40218409b5a3697ac1d3", # Toulmin
                "blk_a0405e121dbf44bfa8ee80566f8d0c2a", # Bloom
                "blk_9adcb55b7ba44baeaf8921cb2fb935dc"  # System 1/2
            ],
            "show_text": True
        },
        {
            "preset_view": "2d_compare",
            "steps": [],
            "target_blocks": [
                "blk_d0e240184e0a40759d37138a250bd0aa", # Precedent
                "blk_8b12be64227c4abd83e2f409b5c3ce28"  # Security / Bias
            ],
            "show_text": True
        },
        {
            "preset_view": "2d_compare",
            "steps": [],
            "target_blocks": [
                "blk_b5ec25bb352e4dc09de386f0da991a08", # Metric vs bias
                "blk_1e33ce78623943af9d5ce39ce6620478"  # Critical Distance
            ],
            "show_text": True
        }
    ]
}

mutated = False
for workflow in data.get("workflows", []):
    if workflow.get("slug") == "kokonaisvaltainen_auditointi":
        profiles = workflow.get("output_profiles", {})
        profiles["analytical_synthesis"] = new_profile
        mutated = True

if mutated:
    with open(SEED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Suoritetty! Luotu uusi tulostusmäärittely.")

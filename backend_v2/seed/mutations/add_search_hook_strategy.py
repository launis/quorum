import json
import os
import shutil
from datetime import datetime

SEED_FILE = "C:/src/quorum/backend_v2/seed/seed_data.json"
BACKUP_DIR = "C:/src/quorum/backend_v2/seed/backups"

def backup_file(file_path: str) -> str:
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.basename(file_path)
    backup_path = os.path.join(BACKUP_DIR, f"{filename}.{timestamp}.bak")
    shutil.copy2(file_path, backup_path)
    return backup_path

def add_search_hook_strategy():
    backup_path = backup_file(SEED_FILE)
    print(f"[MUTATION] Created backup at: {backup_path}")

    with open(SEED_FILE, encoding="utf-8") as f:
        data = json.load(f)

    # Find system config
    system_config = data.get("system_config", [])
    registry = None
    for config in system_config:
        if config.get("slug") == "config_model_registry":
            registry = config
            break

    if not registry:
        print("[ERROR] config_model_registry not found!")
        return

    models = registry.get("models", {})

    if "SearchHook" in models:
        print("[SKIP] SearchHook strategy already exists.")
        return

    # Clone the 'search' strategy or create a new Gemini 2.5 Flash one
    base_search = models.get("search", {})

    new_search_hook = {
        "max_tokens": 65536,
        "model_name": "vertex_ai/gemini-2.5-flash",
        "temperature": 0.0,
        "top_p": None,
        "supports_grounding": True,
        "tpm_limit": 100000,
        "rpm_limit": 15,
        "parsing_mode": "GEMINI_JSON",
        "is_active": True,
        "provider": "google"
    }

    models["SearchHook"] = new_search_hook

    with open(SEED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        # Ensure trailing newline
        f.write("\n")

    print("[MUTATION] SearchHook AI strategy successfully injected into model_registry configs.")

if __name__ == "__main__":
    add_search_hook_strategy()

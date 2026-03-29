import ast
import json
import logging
import shutil
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SEED_JSON_PATH = Path(r"c:\src\quorum\backend_v2\seed\seed_data.json")

def clean_timestamp(val: str) -> str:
    """Yritetään korjata aikaleima Strict ISO8601 muotoon (Z)."""
    # 2026-03-25 12:00:00 -> 2026-03-25T12:00:00Z
    v = val.strip()
    if v.endswith("+00:00"):
        v = v.replace("+00:00", "Z")
    if " " in v and "T" not in v:
        v = v.replace(" ", "T")
    if not v.endswith("Z"):
        v = v + "Z"
    return v

def clean_enum_type(val: str) -> str:
    v = val.lower()
    if v == "str":
        return "string"
    return v

def clean_enum_status(val: str) -> str:
    v = val.lower()
    if v == "done":
        return "completed"
    if v == "draft":
        return "draft"
    if v == "running":
        return "running"
    if v == "failed":
        return "failed"
    if v == "pending":
        return "pending"
    return v

def deep_clean(data: Any, modifications: dict[str, int]) -> None:
    if isinstance(data, dict):
        for k, v in data.items():
            # 1. Aikaleimat (ISO 8601 Strict Z)
            if k in ["created_at", "updated_at", "completed_at", "timestamp"] and isinstance(v, str):
                new_v = clean_timestamp(v)
                if new_v != v:
                    data[k] = new_v
                    modifications["timestamps"] += 1

            # 2. BlockDataType ja muut tyypit (Pienkirjaimet)
            if k == "type" and isinstance(v, str):
                # Varo koskemasta "step_type" arvoihin (esim. "llm" tai "model_registry"), korjataan vain yleisimmät
                if v.upper() in ["STRING", "FLOAT", "INT", "JSON", "BOOLEAN", "STR"]:
                    new_v = clean_enum_type(v)
                    if new_v != v:
                        data[k] = new_v
                        modifications["enums_type"] += 1
                elif v.upper() in ["COMPLETED", "DONE", "FAILED", "PENDING", "RUNNING"]:
                    new_v = clean_enum_status(v)
                    if new_v != v:
                        data[k] = new_v
                        modifications["enums_status"] += 1

            # 3. ExecutionStatus
            if k == "status" and isinstance(v, str):
                new_v = clean_enum_status(v)
                if new_v != v:
                    data[k] = new_v
                    modifications["enums_status"] += 1

            # 4. Stringifioitu JSON -purkaus
            if isinstance(v, str) and (v.strip().startswith("{") and v.strip().endswith("}")):
                try:
                    # Yritetään Ensin aitoa JSON:ia
                    parsed = json.loads(v)
                    data[k] = parsed
                    modifications["json_evals"] += 1
                except json.JSONDecodeError:
                    try:
                        # Jos yksinkertaiset heittomerkit (Python dicteissä kuten 'score')
                        parsed = ast.literal_eval(v)
                        data[k] = parsed
                        modifications["json_evals"] += 1
                    except (SyntaxError, ValueError):
                        pass

            # Jatka rekursiota
            deep_clean(data[k], modifications)

    elif isinstance(data, list):
        for item in data:
            deep_clean(item, modifications)

def main() -> None:
    if not SEED_JSON_PATH.exists():
        print(f"❌ Tiedostoa ei löydy: {SEED_JSON_PATH}")
        return

    # Backup ensin
    backup_path = SEED_JSON_PATH.with_suffix(".json.bak.epic11")
    shutil.copy(SEED_JSON_PATH, backup_path)
    print(f"🛡️ Backup luotu onnistuneesti: {backup_path}")

    with open(SEED_JSON_PATH, encoding="utf-8") as f:
        data = json.load(f)

    mods = {
        "timestamps": 0,
        "enums_type": 0,
        "enums_status": 0,
        "json_evals": 0
    }

    # Puhdistajamoottori päälle
    deep_clean(data, mods)

    total = sum(mods.values())
    if total > 0:
        with open(SEED_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("✅ Siemendatan Pydantic-korjaukset suoritettu lokaalisti:")
        for k, v in mods.items():
            print(f"  - {k}: {v} muunnosta")
    else:
        print("✅ Siemendata oli valmiiksi puhdas.")

if __name__ == "__main__":
    main()

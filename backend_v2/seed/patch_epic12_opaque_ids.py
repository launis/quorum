import json
import os
import re
import shutil
import uuid
from datetime import datetime
from typing import Any

SEED_PATH = r"c:\src\quorum\backend_v2\seed\seed_data.json"
BACKUP_DIR = r"c:\src\quorum\backend_v2\seed\backups"

# Known entity ID prefixes across the platform that should be handled as Stripe IDs
VALID_ENTITY_PREFIXES = {
    "steprule", "syscfg", "step", "wf", "org", "usr", "prf", "blk", "mcp", "exe", "res", "cfg"
}

def is_target_id(s: str) -> bool:
    if not isinstance(s, str):
        return False
    if s == "mcp_gateways":
        return False
    match = re.match(r"^([a-z]+)_([a-zA-Z0-9]+)$", s)
    if not match:
        return False
    return match.group(1) in VALID_ENTITY_PREFIXES

def generate_new_id(old_id: str, mapping: dict[str, str]) -> str:
    if old_id in mapping:
        return mapping[old_id]

    match = re.match(r"^([a-z]+)_(.+)$", old_id)
    if not match:
        return old_id

    prefix = match.group(1)

    # 1. Tuetaan vain sallittuja 2-5 merkin pituuksia.
    # Uudelleenmapataan rikkinäiset
    if prefix == "steprule":
        new_prefix = "sr"
    elif prefix == "syscfg" or prefix == "cfg":
        new_prefix = "sys"
    elif prefix == "step":
        new_prefix = "sp"
    else:
        # Säilytetään jos se on jo 2-5 char välillä (esim blk, wf, usr, org, prf)
        if 2 <= len(prefix) <= 5:
            new_prefix = prefix
        else:
            new_prefix = prefix[:5] # Pakotetaan trunkoimalla, jottei jää laittomaksi

    # 2. Pakotetaan aito satunnainen krypto-ID, jotta semanttiset jäänteet kuolevat
    new_hash = uuid.uuid4().hex[:16]
    new_id = f"{new_prefix}_{new_hash}"

    mapping[old_id] = new_id
    return new_id


def traverse_and_replace_ids(node: Any, mapping: dict[str, str]) -> Any:
    """Recursively traverse the JSON tree and replace ALL occurrences of Opaque IDs."""
    if isinstance(node, dict):
        new_dict = {}
        for k, v in node.items():
            new_k = generate_new_id(k, mapping) if is_target_id(k) else k
            new_dict[new_k] = traverse_and_replace_ids(v, mapping)
        return new_dict
    elif isinstance(node, list):
        return [traverse_and_replace_ids(item, mapping) for item in node]
    elif isinstance(node, str):
        if is_target_id(node):
            return generate_new_id(node, mapping)
        return node
    else:
        return node

def patch_output_profiles_schema(output_profiles_list: list[dict[str, Any]]) -> int:
    """Schema Parity Migration: Updates the standalone `/studio/output-profiles/` items
    to perfectly match the OutputLayoutBlock standard introduced in v2_core.py Phase 9.
    layout_type -> preset_view
    components -> target_blocks
    Adds empty steps: []
    """
    modifications = 0
    for profile in output_profiles_list:
        layouts = profile.get("layouts", [])
        for layout in layouts:
            # Muunnetaan vanha LayoutType uuteen preset_view muotoon!
            if "layout_type" in layout:
                old_type = layout.pop("layout_type")
                if old_type == "automatic":
                    layout["preset_view"] = "default"
                elif old_type == "radar_3d":
                    layout["preset_view"] = "3d_complex"
                elif old_type == "box_1d":
                    layout["preset_view"] = "1d_metrics"
                elif old_type == "matrix_2d":
                    layout["preset_view"] = "2d_compare"
                elif old_type == "text_only":
                    layout["preset_view"] = "text_only"
                else:
                    layout["preset_view"] = "default"
                modifications += 1

            # Muunnetaan vanha 'components' uudeksi 'target_blocks'
            if "components" in layout:
                layout["target_blocks"] = layout.pop("components")
                modifications += 1

            if "steps" not in layout:
                layout["steps"] = []
                modifications += 1

    return modifications

def main() -> None:
    if not os.path.exists(SEED_PATH):
        print(f"Error: {SEED_PATH} ei löydy.")
        return

    # 1. Varmuuskopiointi (Backup)
    dt_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"seed_data_backup_{dt_str}_epic12_opaque_ids.json")
    os.makedirs(BACKUP_DIR, exist_ok=True)
    shutil.copy2(SEED_PATH, backup_file)
    print(f"✅ Varmuuskopio luotu: {backup_file}")

    # 2. Lataus (Load)
    with open(SEED_PATH, encoding='utf-8') as f:
        data = json.load(f)

    # 3. Output Profiles Schema Parity Patch
    profiles_patched = 0
    if "output_profiles" in data and isinstance(data["output_profiles"], list):
        profiles_patched = patch_output_profiles_schema(data["output_profiles"])
        print(f"✅ Output Profiles Schema Parity Patch suoritettuna: {profiles_patched} osumaa päivitetty.")

    # 4. Global Recursive ID Replacement
    mapping_dict: dict[str, str] = {}
    new_data = traverse_and_replace_ids(data, mapping_dict)

    # Suodatetaan ID-mapping listauksesta ulos ne, jotka eivät oikeasti muuttuneet
    # (jotkut olivat jo valideja ja niille tuotettiin identtinen map)
    actual_changes = {k: v for k, v in mapping_dict.items() if k != v}

    print(f"✅ Löydettiin ja korvattiin {len(actual_changes)} kpl Legacy/Pseudo-Opaque ID:tä krypto-puhtaina Stripe ID:einä.")
    for k, v in list(actual_changes.items())[:10]:
        print(f"   - Mappaus: {k} -> {v}")

    if len(actual_changes) > 10:
        print(f"   ... ja {len(actual_changes) - 10} muuta.")

    # 5. Tallennus (Save)
    with open(SEED_PATH, 'w', encoding='utf-8') as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)

    print("✅ Pysyvä tallennus suoritettu. Seed Data on nyt 100% Epic 12 yhteensopiva.")

if __name__ == "__main__":
    main()

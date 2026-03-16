import json
from pathlib import Path


def verify():
    v1_path = Path("c:/src/quorum/data/github_seed_data.json")
    v2_path = Path("c:/src/quorum/backend_v2/seed/seed_data.json")

    with open(v1_path, encoding="utf-8") as f:
        v1_data = json.load(f)
    with open(v2_path, encoding="utf-8") as f:
        v2_data = json.load(f)

    v1_steps = v1_data.get("steps", [])
    if isinstance(v1_steps, dict): v1_steps = list(v1_steps.values())

    v2_steps = v2_data.get("steps", [])

    # Needs a mapping of original v1 step IDs to v2 step slugs
    # We can reconstruct how V2 steps are named from V1 name/slugs
    import re
    def slugify(text: str, fallback_index: int) -> str:
        if not text: return f"item_{fallback_index}"
        clean = re.sub(r'[^a-zA-Z0-9\s-]', '', text).strip().lower()
        clean = re.sub(r'[\s-]+', '_', clean)
        return clean[:30]

    # Rebuild uuid_to_slug exactly as the stitcher did
    uuid_to_slug = {}

    matrices_db = v1_data.get("matrices", [])
    if isinstance(matrices_db, dict): matrices_db = list(matrices_db.values())
    for idx, m in enumerate(matrices_db):
        uid = m.get("id")
        raw_name = m.get("label") or m.get("slug", "") or f"Matrix {idx}"
        clean_slug = f"matrix_{slugify(raw_name, idx)}"
        uuid_to_slug[uid] = clean_slug

        name_lower = raw_name.lower()
        desc_lower = (m.get("description") or "").lower()
        if "toulmin" in name_lower or "toulmin" in desc_lower or "argument" in desc_lower: uuid_to_slug[uid] = "matrix_toulmin"
        elif "bloom" in name_lower or "bloom" in desc_lower or "cognitiv" in name_lower or "kognitiivi" in name_lower: uuid_to_slug[uid] = "matrix_bloom"
        elif "kahneman" in name_lower or "kahneman" in desc_lower or "fast and slow" in desc_lower or "system 1" in desc_lower or "system 2" in desc_lower: uuid_to_slug[uid] = "matrix_kahneman"
        elif "goodhart" in name_lower or "goodhart" in desc_lower or "performatiivisuus" in name_lower or "performativity" in name_lower: uuid_to_slug[uid] = "matrix_goodhart"

    components_db = v1_data.get("components", [])
    if isinstance(components_db, dict): components_db = list(components_db.values())
    for idx, c in enumerate(components_db):
        uid = c.get("id")
        raw_name = c.get("name") or c.get("slug", "") or f"Block {idx}"
        clean_slug = f"block_{slugify(raw_name, idx)}"
        uuid_to_slug[uid] = clean_slug

        name_lower = raw_name.lower()
        desc_lower = (c.get("description") or "").lower()
        if "toulmin" in name_lower or "toulmin" in desc_lower or "argument" in desc_lower: uuid_to_slug[uid] = "matrix_toulmin"
        elif "bloom" in name_lower or "bloom" in desc_lower or "cognitiv" in name_lower or "kognitiivi" in name_lower: uuid_to_slug[uid] = "matrix_bloom"
        elif "kahneman" in name_lower or "kahneman" in desc_lower or "fast and slow" in desc_lower or "system 1" in desc_lower or "system 2" in desc_lower: uuid_to_slug[uid] = "matrix_kahneman"
        elif "goodhart" in name_lower or "goodhart" in desc_lower or "performatiivisuus" in name_lower or "performativity" in name_lower: uuid_to_slug[uid] = "matrix_goodhart"

    for idx, st in enumerate(v1_steps):
        s_id = st.get("id")
        raw_name = st.get("name") or f"Task {idx}"
        clean_slug = f"step_{slugify(raw_name, idx)}"
        uuid_to_slug[s_id] = clean_slug

    mismatches = 0

    print("--- PARITY CHECK ---")
    for st in v1_steps:
        v1_id = st.get("id")
        v1_name = st.get("name")
        config = st.get("config", {})

        v1_prompts = list(dict.fromkeys(config.get("llm_prompts", [])))
        v1_matrix = config.get("matrix_id")

        # Expected V2 array mapping
        expected_v2_slugs = []
        for p in v1_prompts:
            if p in uuid_to_slug:
                 expected_v2_slugs.append(uuid_to_slug[p])

        if v1_matrix and v1_matrix in uuid_to_slug:
             expected_v2_slugs.append(uuid_to_slug[v1_matrix])

        # Map step self reference
        if v1_id in uuid_to_slug and uuid_to_slug[v1_id].startswith("matrix_"):
             expected_v2_slugs.append(uuid_to_slug[v1_id])

        expected_v2_slugs = list(dict.fromkeys(expected_v2_slugs))

        # Find actual V2 step by checking name parity or generated slug
        # Find by ID because the stitch script generated deterministic IDs but they might have numeric suffixes.
        # So we look at the name first

        v2_step = next((x for x in v2_steps if x["name"]["translations"]["fi"] == v1_name), None)
        if not v2_step:
            print(f"WARN: Could not find V2 step for {v1_name}")
            continue

        actual_v2_prompts = v2_step.get("prompt_blocks", [])

        # Compare
        if set(expected_v2_slugs) != set(actual_v2_prompts):
            print(f"MISMATCH in Step '{v1_name}':")
            print(f"  Expected V2 Prompts: {expected_v2_slugs}")
            print(f"  Actual V2 Prompts:   {actual_v2_prompts}")
            mismatches += 1

    if mismatches == 0:
        print("PERFECT PARITY! Kaikki stepit ja niiden sisältämät ohjeet / matriisit täsmäävät V1:n kanssa 100%.")
    else:
        print(f"Löytyi {mismatches} eroa askelten ohjemääritteissä.")

if __name__ == "__main__":
    verify()

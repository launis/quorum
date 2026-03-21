import json

SEED_FILE = r"c:\src\quorum\backend_v2\seed\seed_data.json"

with open(SEED_FILE, encoding="utf-8") as f:
    data = json.load(f)

# The 5 actual mathematical scoring matrices
id_3d_x = "blk_371c7724eeba40218409b5a3697ac1d3" # Toulmin
id_3d_y = "blk_a0405e121dbf44bfa8ee80566f8d0c2a" # Bloom
id_3d_z = "blk_9adcb55b7ba44baeaf8921cb2fb935dc" # System 1/2

id_2d_x = "blk_d0e240184e0a40759d37138a250bd0aa" # Precedent
id_2d_y = "blk_8b12be64227c4abd83e2f409b5c3ce28" # Security

mutated = False
for workflow in data.get("workflows", []):
    if workflow.get("slug") == "kokonaisvaltainen_auditointi":
        profiles = workflow.get("output_profiles", {})
        default_profile = profiles.get("default")

        if default_profile:
            layouts = default_profile.get("layouts", [])
            if len(layouts) > 0 and layouts[0].get("preset_view") == "3d_complex":
                layouts[0]["target_blocks"] = [id_3d_x, id_3d_y, id_3d_z]
                mutated = True
            if len(layouts) > 1 and layouts[1].get("preset_view") == "1d_metrics":
                layouts[1]["target_blocks"] = [id_2d_x, id_2d_y]
                mutated = True

if mutated:
    with open(SEED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

import json

# The 17 oscillating atoms from 11.md
high_entropy_ids = {
    "tda_bce60530213249dd",
    "tda_545bffdc85a31f0e",
    "tda_f142c3fa1d08cc2d",
    "tda_247927c98b0c46f8",
    "tda_bdbdc546677cc222",
    "tda_55dfd9cb0adec620",
    "tda_2303fd9ca0b0fa67",
    "tda_8b1717b2ca9f25e2",
    "tda_c74c4367acc028cf",
    "tda_8f668ea29869ba8b",
    "tda_9ab273ce743ac29e",
    "tda_8c7b6a9f0d8e411b",
    "tda_c6bcce2b818718a1",
    "tda_ade6cbd3f956fa67",
    "tda_32ee0cac79ad098e",
    "tda_6bf0433f60924302",
    "tda_80c038ed35173cb4"
}

seed_path = "backend_v2/seed/seed_data.json"
with open(seed_path, "r", encoding="utf-8") as f:
    data = json.load(f)

modified_count = 0

for block in data.get("prompt_blocks", []):
    for scale in block.get("scales", []):
        for claim in scale.get("claims", []):
            for tda in claim.get("tda_assertions", []):
                tda_id = tda.get("tda_id")
                if tda_id in high_entropy_ids:
                    tda["high_entropy"] = True
                    modified_count += 1
                else:
                    tda["high_entropy"] = False

print(f"Parsed seed_data.json. Modified {modified_count} out of {len(high_entropy_ids)} targeted high entropy assertions.")

with open(seed_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Saved updated seed_data.json cleanly.")

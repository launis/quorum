import json


def clean_seed():
    path = 'c:/src/quorum/backend_v2/seed/seed_data.json'
    with open(path, encoding='utf-8') as f:
        db = json.load(f)

    prompt_blocks = db.get("prompt_blocks", [])
    for pb in prompt_blocks:
        for scale in pb.get("scales", []):
            for claim in scale.get("claims", []):
                for tda in claim.get("tda_assertions", []):
                    if "ai_rule_description" in tda:
                        del tda["ai_rule_description"]

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=4)

if __name__ == "__main__":
    clean_seed()

import json

seed_path = 'c:/src/quorum/backend_v2/seed/seed_data.json'
with open(seed_path, 'r', encoding='utf-8') as f:
    db = json.load(f)

count = 0
for list_name in ["prompt_blocks", "matrices"]:
    for item in db.get(list_name, []):
        if "scales" in item and len(item["scales"]) > 0:
            count += 1
            scores = [s.get("score") for s in item["scales"]]
            allow_dec = item.get("allow_decimals", False)
            scale_min = item.get("scale_min")
            scale_max = item.get("scale_max")
            score_str = str(scores)
            print(f"{item.get('id'):25} | Scores: {score_str:20} | Decimals: {str(allow_dec):5} | Min: {scale_min}, Max: {scale_max}")

print(f"\nTotal BARS Matrices found: {count}")

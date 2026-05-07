import json

evaluative_true_ids = {
    "blk_440a5fef9331451b", # Toulminin Argumentaatiomalli
    "blk_f921c7c0989b47e8", # Bloomin Taksonomia
    "blk_109dab5b6b3f403a", # Kahnemanin Kaksoisprosessiteoria
    "blk_b476f89fb732448c", # Falsifioinnin Auditointi
    "blk_f6e286f050c94d60", # Selitettävyys ja Läpinäkyvyys
    "blk_22e3598e06414409", # Episteeminen Nöyryys
    "blk_c3bc5f3eb8e74110", # Kausaalinen ja Abduktiivinen Integriteetti
}

evaluative_false_ids = {
    "blk_c5804a9143c34cb1", # Kausaalisuuden Analyysi
    "blk_80732a33fe1947ee", # Turvallisuus- ja Etiikkasuodatin
    "blk_fb15f8dcf23f4865", # Arkistointistandardien Auditointi
    "blk_ff72c2d79edb4ebf", # Ylituomari
    "blk_6b8c766185294f7e", # XAI-Raportoija
    "blk_53f32679aa514fcb", # Performatiivisuus ja Goodhartin Laki
}

with open("backend_v2/seed/seed_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

updated_count = 0
for block in data.get("prompt_blocks", []):
    if block.get("category_id") == "matrix":
        block_id = block.get("id")
        if block_id in evaluative_true_ids:
            block["is_evaluative"] = True
            updated_count += 1
        elif block_id in evaluative_false_ids:
            block["is_evaluative"] = False
            updated_count += 1

with open("backend_v2/seed/seed_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"Updated {updated_count} matrices in seed_data.json")

import json
from pathlib import Path

# V2 Architecture: SSoT Seeding JSON
seed_path = Path("backend_v2/seed/seed_data.json")

# Lataa nykyinen tietokanta
data = json.loads(seed_path.read_text(encoding="utf-8"))

# Määrittele ortogonaaliset matriisit (jotka EIVÄT vaikuta järjestelmän laadun keskiarvoon)
orthogonal_slugs = {
    "matrix_taskguard",               # Turvallisuus- ja Etiikkasuodatin
    "matrix_epistemic_humility",      # Episteeminen Nöyryys
    "matrix_input_processing"         # Kriittinen Syötteiden Prosessointi
}

updated_count = 0

# Päivitä PromptBlockien uusi is_evaluative -lippu
for pb in data.get("prompt_blocks", []):
    slug = pb.get("slug")
    if slug in orthogonal_slugs:
        pb["is_evaluative"] = False
        updated_count += 1
        print(f"[Patch] Asetettiin is_evaluative=False matriisille: {slug} ({pb.get('label', {}).get('translations', {}).get('fi')})")
    elif pb.get("category_id") == "matrix" and "scales" in pb:
        # Muut varsinaiset matriisit säilyttävät vakiona True
        pass

# Tallenna takaisin V2-standardilla
seed_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

print(f"\n✅ Seed-data päivitetty onnistuneesti! ({updated_count} ortogonaalista matriisia liputettu).")

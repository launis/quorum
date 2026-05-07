import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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

def verify_file(filepath, container_key, is_tinydb=False):
    print(f"--- Verifying {filepath} ---")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        blocks = []
        if is_tinydb:
            blocks_dict = data.get("prompt_blocks", {})
            blocks = list(blocks_dict.values())
        else:
            blocks = data.get(container_key, [])
            
        matrices = [b for b in blocks if b.get("category_id") == "matrix"]
        
        errors = []
        for m in matrices:
            id = m.get("id")
            name = m.get("label", {}).get("translations", {}).get("fi", "N/A")
            is_eval = m.get("is_evaluative")
            
            if id in evaluative_true_ids and not is_eval:
                errors.append(f"[ERROR] {name} ({id}) should be TRUE but is {is_eval}")
            elif id in evaluative_false_ids and is_eval:
                errors.append(f"[ERROR] {name} ({id}) should be FALSE but is {is_eval}")
            elif id in evaluative_true_ids or id in evaluative_false_ids:
                print(f"[OK] {name} ({id}) correctly set to {is_eval}")
        
        if errors:
            print("\nFound errors:")
            for e in errors:
                print(e)
        else:
            print("\nAll matrices match the recommendation perfectly!")
            
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
    print()

verify_file("backend_v2/seed/seed_data.json", "prompt_blocks", is_tinydb=False)
verify_file("data/db_v2.json", "prompt_blocks", is_tinydb=True)

import json
import hashlib
from pathlib import Path

def extract_cache():
    seed_file = Path("backend_v2/seed/seed_data.json")
    db_file = Path("data/db_v2.json")
    cache_file = Path("backend_v2/seed/atomization_cache.json")

    if not db_file.exists():
        print(f"DB tiedostoa ei löydy: {db_file}")
        return

    with open(seed_file, "r", encoding="utf-8") as f:
        seed_data = json.load(f)
    
    with open(db_file, "r", encoding="utf-8") as f:
        db_data = json.load(f)

    # TinyDB stores as {"_default": {"1": {...}, "2": {...}}}
    # Let's extract prompt_blocks.
    prompt_blocks_db = db_data.get("prompt_blocks", {})
    # In db_v2.json TinyDB structure, there is a root collection object.
    db_blocks_list = []
    for doc_id, doc in prompt_blocks_db.items():
        if isinstance(doc, dict):
            db_blocks_list.append(doc)

    atomized_logic_map = {}
    for b in db_blocks_list:
        if b.get("category_id") == "matrix" and b.get("scales"):
            # Tarkistetaan että edes yksi micro_atoms löytyy, jotta tiedetään että tämä todella on atomisoitu!
            is_atomized = any(
                claim.get("micro_atoms") 
                for scale in b.get("scales", []) 
                for claim in scale.get("claims", [])
            )
            if is_atomized:
                atomized_logic_map[b["id"]] = b.get("scales")

    print(f"Löydettiin {len(atomized_logic_map)} atomisoitua matriisia tietokannasta.")

    if len(atomized_logic_map) == 0:
        print("Ei mitään välimuistitettavaa (atomisoituja 'scales' kenttiä ei löytynyt).")
        return

    cache = {}
    seed_blocks = seed_data.get("prompt_blocks", [])
    
    for b in seed_blocks:
        if b.get("category_id") == "matrix":
            b_id = b.get("id")
            if b_id in atomized_logic_map:
                en_label = b.get("label", {}).get("translations", {}).get("en", "")
                content = b.get("content", "")
                
                raw_text = f"{b_id}_{en_label}_{content}"
                cache_key = hashlib.md5(raw_text.encode('utf-8')).hexdigest()
                
                cache[cache_key] = atomized_logic_map[b_id]

    print(f"Luodaan välimuisti {len(cache)} kohteelle...")
    
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)
        
    print(f"Välimuisti tallennettu onnistuneesti: {cache_file.absolute()}")

if __name__ == "__main__":
    extract_cache()

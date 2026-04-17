import json
import shutil
import sys
import pprint
from pathlib import Path

# Varmistetaan että backend_v2 löytyy polulta (Pydantic validointia varten)
sys.path.insert(0, r"c:\src\quorum")

try:
    from backend_v2.models.prompt_block import PromptBlock
except ImportError as e:
    print(f"Kriittinen virhe: Ei voida ladata PromptBlock Pydantic-mallia: {e}")
    sys.exit(1)

SEED_FILE = Path(r"c:\src\quorum\backend_v2\seed\seed_data.json")
BACKUP_FILE = Path(r"c:\src\quorum\backend_v2\seed\seed_data_backup_epic25.json")

def run():
    print("==================================================")
    print("   EPIC 25: OUTPUT EXTENSION PRUNING TOOL")
    print("==================================================")
    
    if not SEED_FILE.exists():
        print(f"Error: {SEED_FILE} not found!")
        return

    # 1. Turvaverkko (Backup)
    shutil.copy2(SEED_FILE, BACKUP_FILE)
    print(f"[1/4] Varmuuskopio luotu onnistuneesti: {BACKUP_FILE.name}")
    
    # 2. Lataus ja karsinta
    with open(SEED_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    prompt_blocks = data.get("prompt_blocks", {})
    original_len = len(prompt_blocks)
    
    modified_blocks = []
    matrix_blocks = []
    
    for block_id, block in prompt_blocks.items():
        category = block.get("category_id")
        extensions = block.get("output_extensions", [])
        
        if category != "matrix":
            if extensions:  # Jos listassa on tavaraa (kuten "citation" tms)
                block["output_extensions"] = []
                modified_blocks.append(block_id)
        else:
            matrix_blocks.append(block_id)
            
    print(f"[2/4] Logiikka-ajo valmis. Karsittiin output_extensions {len(modified_blocks)} ei-matriisi lohkolta.")
    
    # 3. Triple-Validation
    # Testi A: Matemaattinen tasapaino
    assert len(prompt_blocks) == original_len, "Virhe 1: Kokonaismäärä ei täsmää!"
    
    # Testi B: Matriisien koskemattomuus
    for b_id in matrix_blocks:
        assert data["prompt_blocks"][b_id].get("category_id") == "matrix"
        
    # Testi C: Pydantic Compile-Test
    try:
        for b_id, block in prompt_blocks.items():
            PromptBlock(**block)
        print("[3/4] Triple-Validation (Pydantic Fail-Fast) LÄPÄISTY!")
    except Exception as e:
        print("Pydantic-validointi epäonnistui arkkitehtuurijohdannaisten takia!")
        print(str(e))
        print("Operaatio keskeytetty. Alkuperäinen seed-tiedosto on koskematon.")
        return

    # 4. Pistokoe ("AI Spot Check" via Console)
    print("\n--------------------------------------------------")
    print(" TARKISTUSLAUSUNTO (SPOT CHECK)")
    print("--------------------------------------------------")
    if modified_blocks:
        print("ESIMERKKI 1: Karsittu synteesilohko (extensions poistettu):")
        sample_id = modified_blocks[0]
        pprint.pprint({
            "id": sample_id,
            "category_id": prompt_blocks[sample_id].get("category_id"),
            "old_extensions_had_items": True,
            "new_output_extensions": prompt_blocks[sample_id].get("output_extensions")
        })
        
    if matrix_blocks:
        print("\nESIMERKKI 2: Säilytetty matriisi (extensions tallella):")
        sample_matrix_id = matrix_blocks[0]
        pprint.pprint({
            "id": sample_matrix_id,
            "category_id": prompt_blocks[sample_matrix_id].get("category_id"),
            "output_extensions": prompt_blocks[sample_matrix_id].get("output_extensions")
        })
        
    print("--------------------------------------------------")
    confirm = input("\nVahvistatko muutokset turvallisiksi Epic 25:n mukaisesti? (y/n): ")
    if confirm.lower() == 'y':
        with open(SEED_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n[4/4] Seed-tiedosto päivitetty! Muutettu {len(modified_blocks)} tietuetta.")
        print("👉 Aja lopuksi normaali 'run_seed.py' levittääksesi muutokset kantaan.")
    else:
        print("\nPeruutettu. Mitään ei tallennettu.")

if __name__ == "__main__":
    run()

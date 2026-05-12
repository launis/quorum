import json
import sys

def verify_all_matrices():
    file_path = "backend_v2/seed/seed_data.json"
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    all_valid = True
    matrices_checked = 0
    
    print("--- Aloitetaan matriisien kattava MECE-vahvistus (Tasan 3 väitettä/skaala) ---")
    
    for block in data.get("prompt_blocks", []):
        if block.get("category_id") == "matrix":
            block_id = block.get("id")
            scales = block.get("scales", [])
            matrices_checked += 1
            
            for scale in scales:
                score = scale.get("score")
                num_claims = len(scale.get("claims", []))
                
                if num_claims != 3:
                    print(f"❌ VIRHE: Matriisi {block_id}, Skaala {score} sisältää {num_claims} väitettä (pitää olla 3).")
                    all_valid = False
                    
    print("-------------------------------------------------------------------------")
    print(f"Yhteensä tarkistettiin {matrices_checked} matriisia.")
    
    if all_valid:
        print("✅ SUCCESS: Kaikki matriisit on tarkistettu! Jokaisella skaalalla on täsmälleen 3 väitettä.")
        sys.exit(0)
    else:
        print("❌ FAILURE: Tietokannasta löytyi matriiseja, joissa MECE-sääntö ei toteudu.")
        sys.exit(1)

if __name__ == "__main__":
    verify_all_matrices()

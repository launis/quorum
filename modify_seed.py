import json
import sys

SEED_FILE = "backend/seed/seed_data.json"

def modify_seed():
    with open(SEED_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    found_toulmin = False
    found_bloom = False
    
    # Ohjeet löytyvät 'components' listasta
    components = data.get("components", [])
    
    if not components:
        print("Could not find components array!")
        sys.exit(1)

    for rule in components:
        slug = rule.get("slug")
        
        if slug == "INSTRUCTION_TOULMIN":
            base_content = rule.get("content", "")
            if "yhden desimaalin tarkkuudella" not in base_content:
                rule["content"] = base_content + " Anna analyysin päätteeksi toulmin_score yhden desimaalin tarkkuudella (esim. 4.2)."
            found_toulmin = True
            print("Modified INSTRUCTION_TOULMIN")
            
        elif slug == "INSTRUCTION_BLOOM":
            base_content = rule.get("content", "")
            if "yhden desimaalin tarkkuudella" not in base_content:
                rule["content"] = base_content + " Anna analyysin päätteeksi erikseen numeerinen arvio, bloom_score, yhden desimaalin tarkkuudella (esim. 4.2)."
            found_bloom = True
            print("Modified INSTRUCTION_BLOOM")

    if not found_toulmin or not found_bloom:
        print(f"Warning: Could not find Toulmin ({found_toulmin}) or Bloom ({found_bloom}).")
    else:
        print("Successfully modified instructions in memory.")
        
    # Tallenna muutokset
    with open(SEED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print("Modification complete.")

if __name__ == "__main__":
    modify_seed()

import json

SEED_FILE = "backend/seed/seed_data.json"

def modify_seed():
    with open(SEED_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Varmistetaan että myös Agenttien ohjeet ja isot blokit saavat päivityksen
    modified_count = 0
    
    # Etsi kaikki mestaripromptit "agents" ja "components" tauluista
    for section in ["agents", "components", "system_config"]:
        items = data.get(section, [])
        for item in items:
            
            content = ""
            if isinstance(item, dict):
                content = item.get("content", "")
            
            if not isinstance(content, str):
                continue
                
            needs_update = False
            
            if "Toulmin-mallilla (6 osaa)" in content:
                if "yhden desimaalin tarkkuudella" not in content:
                    content = content.replace(
                        "OUTPUT: logician_data", 
                        "OUTPUT: logician_data (HUOM: Palauta toulmin_score yhden desimaalin tarkkuudella, esim. 4.2. Samoin bloom_score ja strategic_score yhden desimaalin tarkkuudella!)"
                    )
                    content = content.replace(
                        "KÄSKE: Tulosta vastauksesi TÄSMÄLLEEN",
                        "KÄSKE: Tulosta vastauksesi TÄSMÄLLEEN (HUOM: Varmista että kaikki numeeriset pisteet kuten toulmin_score ja bloom_score ovat desimaaleja, esim 4.2)"
                    )
                    needs_update = True
                    
            if "yhden desimaalin tarkkuudella" not in content and "Arvioi Bloomin tasolla" in content:
                 content = content + " Anna bloom_score yhden desimaalin tarkkuudella (esim 4.2)"
                 needs_update = True
                 
            if needs_update:
                item["content"] = content
                modified_count += 1
                print(f"Updated a massive prompt block in {section}: {item.get('slug', item.get('id'))}")

    if modified_count > 0:
        with open(SEED_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Modification complete. Updated {modified_count} monolithic prompts.")
    else:
        print("No monolithic prompts needed updates.")

if __name__ == "__main__":
    modify_seed()

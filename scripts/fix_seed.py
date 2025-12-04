import json
from pathlib import Path

def fix_seed_data():
    seed_path = Path("data/seed_data.json")
    
    with open(seed_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Define new components
    new_components = [
        {
            "id": "HEADER_TEXT",
            "type": "static_text",
            "name": "Raportin Otsikko",
            "content": "# Kognitiivinen Arviointiraportti (v2)\n\n**Järjestelmä:** Cognitive Quorum Assessment Engine\n**Versio:** 2.0 (Data-Driven)\n**Päiväys:** {{ date }}\n\n---",
            "description": "Standard report header",
            "citation": "",
            "citation_full": ""
        },
        {
            "id": "DISCLAIMER_TEXT",
            "type": "static_text",
            "name": "Vastuuvapauslauseke",
            "content": "> **Vastuuvapauslauseke:** Tämä raportti on generoitu tekoälyavusteisesti (AI-Assisted). Se perustuu syötettyyn aineistoon ja määriteltyihin kognitiivisiin sääntöihin. Raportti on tarkoitettu päätöksenteon tueksi, ei korvaamaan ihmisen tekemää lopullista arviota. Järjestelmä voi tehdä virheitä (hallusinaatiot, päättelyvirheet). Ihmisvalvojan (HITL) tulee aina tarkistaa kriittiset havainnot.",
            "description": "Standard legal disclaimer",
            "citation": "",
            "citation_full": ""
        }
    ]
    
    # Check if they already exist to avoid duplicates
    existing_ids = {c.get("id") for c in data["components"]}
    
    for comp in new_components:
        if comp["id"] not in existing_ids:
            print(f"Adding component: {comp['id']}")
            # Insert at the beginning for visibility
            data["components"].insert(0, comp)
        else:
            print(f"Component {comp['id']} already exists.")

    # Update Step 9
    for step in data["steps"]:
        if step["id"] == "step_9":
            prompts = step["execution_config"].get("llm_prompts", [])
            
            if "HEADER_TEXT" not in prompts:
                print("Adding HEADER_TEXT to step_9 prompts")
                prompts.insert(0, "HEADER_TEXT")
            
            if "DISCLAIMER_TEXT" not in prompts:
                print("Adding DISCLAIMER_TEXT to step_9 prompts")
                prompts.append("DISCLAIMER_TEXT")
                
            step["execution_config"]["llm_prompts"] = prompts
            break
            
    # Save back
    with open(seed_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("seed_data.json updated successfully.")

if __name__ == "__main__":
    fix_seed_data()

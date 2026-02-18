
import json
import os
import sys

SEED_FILE = os.path.join(os.path.dirname(__file__), "../backend/seed/seed_data.json")

def inject_panel_prompt():
    print(f"Reading seed data from {SEED_FILE}...")
    try:
        with open(SEED_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Seed file not found at {SEED_FILE}")
        return

    components = data.get("components", [])
    
    # Check for existing
    existing = next((c for c in components if c.get("id") == "PANEL_PROMPT_TEMPLATE"), None)
    
    if existing:
        print("PANEL_PROMPT_TEMPLATE already exists. Updating it...")
        # Update content if needed, but for now just inform
        # We replace it entirely to be sure
        components = [c for c in components if c.get("id") != "PANEL_PROMPT_TEMPLATE"]
    
    new_component = {
        "id": "PANEL_PROMPT_TEMPLATE",
        "name": None,
        "description": None,
        "citation": None,
        "citation_full": None,
        "module": None,
        "component_class": None,
        "class_name": None,
        "registered_at": None,
        "type": "prompt",
        "content": "Olet Cognitive Quorum -järjestelmän Asiantuntijapaneeli (Panel Agent).\n\nSINUN TEHTÄVÄSI on suorittaa alla määritellyt roolit ja analyysit rinnakkain, hyödyntäen syötteenä saatuja aiempien vaiheiden tuloksia.\n\n{task_section}\n\n{context_section}\n\n{search_section}\n\n{linguistics_section}\n\nTÄSSÄ ON ANALYSOITAVA AINEISTO (INPUTS):\n{input_json}\n\nSUORITA ANALYYSI JA PALAUTA VAIN JSON-MUOTOINEN VASTAUS (PanelOutputDTO)."
    }
    
    components.append(new_component)
    data["components"] = components
    
    print("Writing updated seed data...")
    with open(SEED_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
    print("Success: PANEL_PROMPT_TEMPLATE injected.")

if __name__ == "__main__":
    inject_panel_prompt()

import json
import os

path = r"c:\src\quorum\backend\seed\seed_data.json"
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

# check if PANEL_PROMPT_TEMPLATE exists
exists = False
for comp in data.get("components", []):
    if comp.get("id") == "PANEL_PROMPT_TEMPLATE":
        exists = True
        break

if not exists:
    data.setdefault("components", []).append({
        "id": "PANEL_PROMPT_TEMPLATE",
        "name": "Panel Prompt Template",
        "description": "Template for Panel Agent execution",
        "citation": None,
        "citation_full": None,
        "module": None,
        "component_class": None,
        "class_name": None,
        "registered_at": None,
        "type": "prompt",
        "content": "Olet Cognitive Quorum -järjestelmän Asiantuntijapaneeli (Panel Agent).\n\nSINUN TEHTÄVÄSI on suorittaa alla määritellyt roolit ja analyysit rinnakkain, hyödyntäen syötteenä saatuja aiempien vaiheiden tuloksia.\n\n{task_section}\n\n{context_section}\n\n{search_section}\n\n{linguistics_section}\n\nTÄSSÄ ON ANALYSOITAVA AINEISTO (INPUTS):\n{input_json}\n\nSUORITA ANALYYSI JA PALAUTA VAIN JSON-MUOTOINEN VASTAUS (PanelOutputDTO)."
    })
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("Added PANEL_PROMPT_TEMPLATE to seed_data.json")
else:
    print("PANEL_PROMPT_TEMPLATE already exists")

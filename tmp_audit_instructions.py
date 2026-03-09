import json
from pathlib import Path

def audit_instructions():
    v1_path = Path("data/github_seed_data.json")
    v2_path = Path("backend_v2/seed/seed_data.json")
    
    with open(v1_path, "r", encoding="utf-8") as f:
        v1_data = json.load(f)
        
    with open(v2_path, "r", encoding="utf-8") as f:
        v2_data = json.load(f)

    # 1. Kerää V1 components data
    v1_components = v1_data.get("components", [])
    if isinstance(v1_components, dict):
        v1_components = list(v1_components.values())
        
    v1_map = {c.get("id"): c for c in v1_components if isinstance(c, dict)}
    
    # 2. Tutki V2 matriisit, joista tehtiin "instruction" (kategoria system_rule/agent_role)
    v2_matrices = v2_data.get("matrices", [])
    
    print("--- Instruction Audit ---")
    missing_instructions = []
    
    for m in v2_matrices:
        m_type = m.get("type")
        
        if m_type == "instruction":
            slug = m.get("id")
            fi_desc = m.get("description", {}).get("translations", {}).get("fi", "").strip()
            label = m.get("label", {}).get("translations", {}).get("fi", "")
            
            # Etsitäänkö tälle kuvaus alkuperäisestä datasta? (Onko sielläkään mitään)
            v1_match = None
            raw_content = ""
            for v1_id, comp in v1_map.items():
                if slug.endswith(str(comp.get("slug"))) or slug.endswith(str(comp.get("name")).lower().replace(" ", "_")):
                    v1_match = comp
                    break
                    
            if not fi_desc:
                # Etsitään olisiko v1 datassa ollut content/instructions joita ei saatu talteen?
                if v1_match:
                    raw_content = v1_match.get("content") or v1_match.get("instructions") or v1_match.get("description")
                
                missing_instructions.append({
                    "v2_slug": slug,
                    "v2_label": label,
                    "v1_found_text": str(raw_content) if raw_content else "KOKONAAN TYHJÄ MYÖS V1",
                    "category": m.get("category_id")
                })
                
    if missing_instructions:
        print(f"Löytyi {len(missing_instructions)} instruction-blokkia joilla ei ole sisältöä/käskyä!")
        for item in missing_instructions:
            print(f"- [{item['category']}] {item['v2_label']} ({item['v2_slug']})")
            print(f"  V1 alkuperäisteksti oli: {item['v1_found_text']}")
            print()
    else:
        print("Kaikilla instruktioilla on jokin käsky, kuvaus tai sisältö!")

if __name__ == "__main__":
    audit_instructions()

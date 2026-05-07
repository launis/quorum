import json

with open("backend_v2/seed/seed_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

blocks = data.get("prompt_blocks", [])
matrices = [b for b in blocks if b.get("category_id") == "matrix"]

print(f"Total matrices: {len(matrices)}\n")
for m in matrices:
    name_fi = m.get("label", {}).get("translations", {}).get("fi", "N/A")
    id = m.get("id", "N/A")
    is_eval = m.get("is_evaluative", "N/A")
    theory = m.get("theory_grounding", {})
    if theory is None:
        theory = {}
    citation = theory.get("citation_reference", "N/A")
    
    print(f"--- ID: {id} | Name: {name_fi} | Evaluative: {is_eval} ---")
    print(f"Theory: {citation}")
    print("Scales:")
    for s in m.get("scales", []):
        score = s.get("score")
        s_name = s.get("name", {}).get("translations", {}).get("fi", "N/A")
        ai_desc = s.get("ai_description", "N/A")
        print(f"  [{score}] {s_name}: {ai_desc[:100]}...")
    print()

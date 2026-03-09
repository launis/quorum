import json
import re

def clean_file():
    seed_path = "backend_v2/seed/seed_data.json"
    with open(seed_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    changes = 0
    
    # regex matches `### AUDITOITAVA MATERIAALI (INPUT DATA)` and everything after it until the end of the text
    pattern_fi = re.compile(r"### AUDITOITAVA MATERIAALI \(INPUT DATA\).*?(?=\Z)", re.DOTALL)
    pattern_en = re.compile(r"### MATERIAL TO BE AUDITED \(INPUT DATA\).*?(?=\Z)", re.DOTALL)

    for matrix in data.get("matrices", []):
        matrix_id = matrix.get("id") or matrix.get("slug")
        
        # Tarkistetaan sekä instruction että description lohkot
        for field_name in ["instruction", "description"]:
            field_data = matrix.get(field_name, {})
            translations = field_data.get("translations", {})
            
            for lang, text in translations.items():
                original_text = text
                if "HISTORY_TEXT" in text or "PRODUCT_TEXT" in text or "### AUDITOITAVA" in text or "### MATERIAL TO BE AUDITED" in text:
                    print(f"Putsataan matriisi: {matrix_id} ({field_name}.{lang})")
                    
                    cleaned = pattern_fi.sub("", text)
                    cleaned = pattern_en.sub("", cleaned)
                    
                    cleaned = re.sub(r"\[KESKUSTELUHISTORIA_ALKU\].*?\[KESKUSTELUHISTORIA_LOPPU\]", "", cleaned, flags=re.DOTALL)
                    cleaned = re.sub(r"\[LOPPUTUOTE_ALKU\].*?\[LOPPUTUOTE_LOPPU\]", "", cleaned, flags=re.DOTALL)
                    cleaned = re.sub(r"\[REFLEKTIODOKUMENTTI_ALKU\].*?\[REFLEKTIODOKUMENTTI_LOPPU\]", "", cleaned, flags=re.DOTALL)
                    
                    cleaned = cleaned.replace("{{HISTORY_TEXT}}", "")
                    cleaned = cleaned.replace("{{PRODUCT_TEXT}}", "")
                    cleaned = cleaned.replace("{{REFLECTION_TEXT}}", "")
                    
                    cleaned = cleaned.strip()
                    
                    if cleaned != original_text:
                        translations[lang] = cleaned
                        changes += 1

    if changes > 0:
        with open(seed_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Tehtiin {changes} muutosta seed-dataan.")
    else:
        print("Mitään ei tarvinnut muuttaa.")

if __name__ == "__main__":
    clean_file()

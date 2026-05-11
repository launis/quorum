import json
import os

SEED_FILE = r"C:\src\quorum\backend_v2\seed\seed_data.json"
TRACKER_FILE = r"C:\src\quorum\docs\epic\epic51_matrix_tracker.md"

def extract_matrices():
    if not os.path.exists(SEED_FILE):
        print(f"Error: {SEED_FILE} ei löydy.")
        return
        
    with open(SEED_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    matrices = []
    
    # Rekursiivinen haku
    def search(obj):
        if isinstance(obj, dict):
            if obj.get("category_id") == "matrix" and "id" in obj:
                label_fi = obj.get("label", {}).get("translations", {}).get("fi", "Tuntematon Matriisi")
                matrices.append((obj["id"], label_fi))
            for v in obj.values():
                search(v)
        elif isinstance(obj, list):
            for item in obj:
                search(item)
                
    search(data)
    
    with open(TRACKER_FILE, "w", encoding="utf-8") as out:
        out.write("# Epic 51: Matrix Refactor Tracker\n\n")
        out.write("Tämä on automaattisen työnkulun aivot. Käytä puhdasta chattia ja komenna tekoälyä: `Jatka`. Tekoäly poimii ensimmäisen `[NOK]`-rivin, refaktoroi sen `seed_data.json`-tiedostoon ja muuttaa tilan `[OK]`.\n\n")
        
        for matrix_id, label in matrices:
            out.write(f"- [NOK] `{matrix_id}` - {label}\n")
            
    print(f"Löydettiin {len(matrices)} matriisia. Seurantatiedosto luotu: {TRACKER_FILE}")

if __name__ == "__main__":
    extract_matrices()

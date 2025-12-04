import json
from pathlib import Path

def clean_seed_data():
    seed_path = Path("data/seed_data.json")
    
    with open(seed_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    cleaned_components = []
    for comp in data.get("components", []):
        cleaned_comp = {}
        for key, value in comp.items():
            # Keep critical fields even if empty (though they shouldn't be)
            if key in ["id", "type", "name"]:
                cleaned_comp[key] = value
                continue
                
            # Skip empty strings or None
            if value == "" or value is None:
                continue
                
            cleaned_comp[key] = value
        cleaned_components.append(cleaned_comp)
        
    data["components"] = cleaned_components
    
    # Save back
    with open(seed_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("seed_data.json cleaned successfully.")

if __name__ == "__main__":
    clean_seed_data()

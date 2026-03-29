import json
import os

SEED_PATH = r"c:\src\quorum\backend_v2\seed\seed_data.json"

def main():
    if not os.path.exists(SEED_PATH):
        print(f"Virhe: {SEED_PATH} ei löydy.")
        return

    with open(SEED_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    modifications = 0
    # Korjataan irralliset Output Profilet (uusi arkkitehtuuri)
    output_profiles = data.get("output_profiles", [])
    for profile in output_profiles:
        for layout in profile.get("layouts", []):
            if "steps" in layout:
                del layout["steps"]
                modifications += 1
            if "target_blocks" in layout:
                del layout["target_blocks"]
                modifications += 1
                
    if modifications > 0:
        with open(SEED_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Korjaus valmis! Poistettiin yhteensä {modifications} kpl jäännöskenttiä ('steps', 'target_blocks') siemendatasta.")
    else:
        print("✅ Mitään poistettavaa ei löytynyt.")

if __name__ == "__main__":
    main()

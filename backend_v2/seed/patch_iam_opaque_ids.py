import json
import os
import re

SEED_PATH = r"c:\src\quorum\backend_v2\seed\seed_data.json"

def main():
    if not os.path.exists(SEED_PATH):
        print(f"Virhe: {SEED_PATH} ei löydy.")
        return

    with open(SEED_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    modifications = 0
    org_id_map = {
        "system": "org_system000000",
        "default": "org_default00000"
    }

    # 1. Päivitä Organizations
    for org in data.get("organizations", []):
        old_id = org.get("id", "")
        if old_id in org_id_map:
            org["id"] = org_id_map[old_id]
            modifications += 1
        elif old_id and not re.match(r"^([a-z]{2,5})_[a-zA-Z0-9]{8,}$", old_id):
            # Pakotetaan väkisin Opaque ID muodostus jos failfast uhkaa
            new_id = f"org_{old_id.replace('-', '')}00000000"[:16]
            org["id"] = new_id
            org_id_map[old_id] = new_id
            modifications += 1

    # 2. Päivitä Users
    for user in data.get("users", []):
        old_id = user.get("id", "")
        # Opaque ID check for Users
        if old_id and not re.match(r"^([a-z]{2,5})_[a-zA-Z0-9]{8,}$", old_id):
            user["id"] = f"usr_{old_id.replace('-', '')}00000000"[:16]
            modifications += 1
            
        # Vaihdetaan viittaukset järjestelmäorganisaatioihin
        org_id = user.get("organization_id")
        if org_id in org_id_map:
            user["organization_id"] = org_id_map[org_id]
            modifications += 1

    # 3. Päivitä Workflows (jos niissä on org_id viittaus)
    for wf in data.get("workflows", []):
        org_id = wf.get("organization_id")
        if org_id in org_id_map:
            wf["organization_id"] = org_id_map[org_id]
            modifications += 1

    if modifications > 0:
        with open(SEED_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Opaque ID päivitys valmis! Korjattiin {modifications} kpl IAM-viittauksia siemendatasta (Organisaatiot, Käyttäjät).")
    else:
        print("✅ IAM-data oli jo Opaque ID -yhteensopivaa. Ei tehtävää.")

if __name__ == "__main__":
    main()

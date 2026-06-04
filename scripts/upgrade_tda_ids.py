import json
import uuid
import re
from pathlib import Path

def upgrade_tda_ids():
    file_path = Path(r"c:\src\quorum\backend_v2\seed\seed_data.json")
    if not file_path.exists():
        print("seed_data.json not found!")
        return

    content = file_path.read_text(encoding="utf-8")
    
    # Etsitään kaikki tarkalleen 16 heksamerkkiä sisältävät tda_ tunnisteet
    matches = set(re.findall(r'\btda_[a-f0-9]{16}\b', content))
    
    if not matches:
        print("Ei löytynyt päivitettäviä 16-merkkisiä tda_ tunnisteita.")
        return
        
    print(f"Löydettiin {len(matches)} uniikkia 16-merkkistä tda_ tunnistetta.")
    
    # Luodaan uudet 32-merkkiset UUIDv4 tunnisteet
    mapping = {}
    for old_id in matches:
        mapping[old_id] = f"tda_{uuid.uuid4().hex}"
        
    # Korvataan tunnisteet
    new_content = content
    for old_id, new_id in mapping.items():
        new_content = re.sub(r'\b' + old_id + r'\b', new_id, new_content)
        
    # Varmistetaan että JSON ei hajonnut korvauksen myötä
    try:
        json.loads(new_content)
    except json.JSONDecodeError:
        print("Virhe: JSON-rakenne hajosi korvauksen yhteydessä! Perutaan tallennus.")
        return
        
    # Tallennetaan päivitetty tiedosto
    file_path.write_text(new_content, encoding="utf-8")
    print(f"Onnistuneesti päivitetty {len(matches)} tda_ tunnistetta 32-merkkisiksi (UUIDv4) seed_data.json -tiedostoon.")

if __name__ == "__main__":
    upgrade_tda_ids()

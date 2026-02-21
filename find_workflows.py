import json
import os
import sys

def scan_file(filepath):
    if not os.path.exists(filepath):
        return

    print(f"\n{'='*50}")
    print(f"SKANNAUS: {filepath}")
    print(f"{'='*50}\n")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # Käsittele seed_data.json tyyppinen rakenne
            workflows = []
            if isinstance(data, dict):
                if 'workflows' in data:
                    workflows = data['workflows']
                elif '_default' in data: # db.json tyyppinen tinydb rakenne
                    for k, v in data['_default'].items():
                        if isinstance(v, dict) and v.get('type') == 'workflow' or 'steps' in v:
                            workflows.append(v)
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and (item.get('type') == 'workflow' or 'steps' in item):
                        workflows.append(item)

            if isinstance(workflows, dict):
                workflows = list(workflows.values())

            if not workflows:
                print("  -> Ei työnkulkuja löytynyt tästä tiedostosta.")
                return

            print(f"LÖYTYI {len(workflows)} TYÖNKULKUA:\n")
            for w in workflows:
                w_id = w.get('id', 'N/A')
                name = w.get('name', 'N/A')
                desc = w.get('description')
                
                print(f"  ID:          {w_id}")
                print(f"  NIMI:        {name}")
                print(f"  KUVAUS:      '{desc}' (Tyyppi: {type(desc).__name__})")
                
                # Jos kuvaus on null tai puuttuu, varoitetaan erikseen
                if desc is None:
                    if 'description' not in w:
                        print("               [!] TÄSSÄ TYÖNKULUSSA EI OLE 'description' KENTTÄÄ OLLENKAAN!")
                    else:
                        print("               [!] TÄMÄN TYÖNKULUN KUVAUS ON EKSPLISIITTISESTI 'null'")
                        
                print(f"  ASKELEITA:   {len(w.get('steps', []))}")
                print("-" * 40)

    except Exception as e:
        print(f"  Virhe luettaessa tiedostoa: {e}")

def main():
    files_to_check = [
        os.path.join("backend", "seed", "seed_data.json"),
        os.path.join("data", "db.json"),
        os.path.join("backend", "database", "db_mock.json"),
    ]
    
    for f in files_to_check:
        scan_file(f)

if __name__ == "__main__":
    main()

import os
import glob
import re
from collections import Counter

def main():
    # Etsitään kaikki mismatch_traces_raw*.md -tiedostot scratch/-hakemistosta
    md_files = glob.glob("scratch/mismatch_traces_raw*.md")
    
    # Etsitään myös tiedostot, joissa on välilyöntejä tai numeroita nimessä
    all_files = list(set(md_files))
    print(f"Löydettiin {len(all_files)} vertailutiedostoa analysoitavaksi:\n")
    for f in sorted(all_files):
        print(f"  - {f}")
        
    atom_counter = Counter()
    atom_files = {} # Kirjataan missä tiedostoissa kukin atomi esiintyi
    
    # Hakulausekkeet Atom-ID:lle (eri Markdown-versioissa)
    # Esim: "### Atom-ID: `tda_3d3f1162d2ff1558`" tai "## Atom: tda_55dfd9cb0adec620"
    patterns = [
        re.compile(r"Atom-ID:\s*`?(tda_[a-f0-9]{16})`?"),
        re.compile(r"Atom:\s*(tda_[a-f0-9]{16})")
    ]
    
    for file_path in all_files:
        basename = os.path.basename(file_path)
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            
        # Etsitään kaikki uniikit osumat tästä tiedostosta
        file_atoms = set()
        for pattern in patterns:
            matches = pattern.findall(content)
            for m in matches:
                file_atoms.add(m)
                
        for atom in file_atoms:
            atom_counter[atom] += 1
            if atom not in atom_files:
                atom_files[atom] = []
            atom_files[atom].append(basename)
            
    print("\n" + "="*50)
    print("EPÄVAKAIMMAT ATOMIT JÄRJESTETTYNÄ ESIINTYMISFREKVENSSIN MUKAAN:")
    print("="*50)
    
    # Etsitään säännön kuvaukset tietokannasta, jos saatavilla
    atom_rules = {}
    seed_path = "backend_v2/seed/seed_data.json"
    if os.path.exists(seed_path):
        try:
            import json
            with open(seed_path, "r", encoding="utf-8") as sf:
                seed = json.load(sf)
            for block in seed.get('prompt_blocks', []):
                for scale in block.get('scales', []):
                    for claim in scale.get('claims', []):
                        for tda in claim.get('tda_assertions', []):
                            atom_rules[tda.get('tda_id')] = tda.get('ai_rule_description')
        except Exception as e:
            print(f"Virhe ladattaessa seed_data.json: {e}")
            
    sorted_atoms = atom_counter.most_common()
    
    # Tallenna tulokset Markdown-muotoon
    output_report = "scratch/all_unstable_atoms_summary.md"
    with open(output_report, "w", encoding="utf-8") as out:
        out.write("# Historiallisesti Epävakaiden Atomien Kokonaisanalyysi\n\n")
        out.write(f"Analysoitu yhteensä **{len(all_files)}** vertailuajoa hakemistosta `scratch/`.\n\n")
        out.write("## Kaikki epävakaat atomit järjestettynä heilahtelukertojen mukaan\n\n")
        out.write("| Sija | Atom-ID | Heilahtelukerrat | Esiintymisprosentti | Kuvaus / Sääntö |\n")
        out.write("| :---: | :--- | :---: | :---: | :--- |\n")
        
        for idx, (atom, count) in enumerate(sorted_atoms):
            pct = (count / len(all_files)) * 100
            rule_desc = atom_rules.get(atom, "Tuntematon sääntö")
            # Lyhennetään kuvausta jos se on liian pitkä taulukkoon
            if len(rule_desc) > 120:
                rule_desc = rule_desc[:117] + "..."
            out.write(f"| {idx + 1} | `{atom}` | {count} | {pct:.1f} % | {rule_desc} |\n")
            
        out.write("\n\n## Yksityiskohtaiset esiintymistiedot\n")
        for idx, (atom, count) in enumerate(sorted_atoms):
            out.write(f"\n### `{atom}` ({count} kertaa epävakaa)\n")
            out.write(f"**Sääntö:** {atom_rules.get(atom, 'Tuntematon sääntö')}\n\n")
            out.write("**Havaittu epävakaaksi seuraavissa tiedostoissa:**\n")
            for filename in sorted(atom_files[atom]):
                out.write(f"- `{filename}`\n")
            out.write("\n---\n")
            
    print(f"\nAnalyysi valmis! Tulokset kirjoitettu tiedostoon: {output_report}")
    print(f"Yhteensä löydettiin {len(sorted_atoms)} eri epävakaata atomia.")
    for idx, (atom, count) in enumerate(sorted_atoms[:10]):
        print(f"  {idx+1}. {atom}: {count} kertaa ({(count/len(all_files))*100:.1f}%)")

if __name__ == "__main__":
    main()

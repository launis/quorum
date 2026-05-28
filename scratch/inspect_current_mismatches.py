import json
import os
import re
import glob

def get_all_evals(path: str) -> dict[str, dict[str, object]]:
    if not os.path.exists(path):
        return {}
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    all_evals: dict[str, dict[str, object]] = {}
    for step in data:
        if 'content' in step and isinstance(step['content'], dict):
            for e in step['content'].get('evaluations', []):
                all_evals[e['atom_id']] = e
    return all_evals

def main():
    # 1. Lue nykyinen mismatch_traces_raw.md ja poimi sieltä atomit
    report_path = "scratch/mismatch_traces_raw.md"
    if not os.path.exists(report_path):
        print(f"Virhe: Raporttia '{report_path}' ei löydy. Aja diff_executions.py ensin.")
        return

    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Etsi kaikki "Atom-ID: `tda_...`" osumat
    atom_pattern = re.compile(r"Atom-ID:\s*`?(tda_[a-f0-9]{16})`?")
    mismatching_atoms = sorted(list(set(atom_pattern.findall(content))))

    if not mismatching_atoms:
        print("Raportista ei löytynyt heilahtelevia atomeja tai se on tyhjä.")
        return

    print(f"Löydettiin {len(mismatching_atoms)} heilahtelevaa atomia raportista.")

    # 2. Etsi kaksi tuoreinta ajoa
    exe_dirs = glob.glob('data/files/executions/exe_*')
    exe_dirs.sort(key=os.path.getmtime, reverse=True)

    if len(exe_dirs) < 2:
        print("Virhe: Ei tarpeeksi suorituskansioita vertailuun.")
        return

    run_1_id = os.path.basename(exe_dirs[1])
    run_2_id = os.path.basename(exe_dirs[0])
    run_1_path = os.path.join(exe_dirs[1], 'execution_trace.json')
    run_2_path = os.path.join(exe_dirs[0], 'execution_trace.json')

    print(f"Ladataan evaluoinnit ajosta 1 ({run_1_id}) ja ajosta 2 ({run_2_id})")
    evals_1 = get_all_evals(run_1_path)
    evals_2 = get_all_evals(run_2_path)

    # Etsi säännön kuvaus tietokannasta
    atom_rules = {}
    seed_path = 'backend_v2/seed/seed_data.json'
    if os.path.exists(seed_path):
        try:
            with open(seed_path, 'r', encoding='utf-8') as sf:
                seed = json.load(sf)
            for block in seed.get('prompt_blocks', []):
                for scale in block.get('scales', []):
                    for claim in scale.get('claims', []):
                        for tda in claim.get('tda_assertions', []):
                            atom_rules[tda.get('tda_id')] = tda.get('ai_rule_description')
        except Exception as e:
            print(f"Varoitus: Ei voitu ladata seed_data.json-kuvauksia: {e}")

    output_path = "scratch/detailed_mismatches_inspection.md"
    print(f"Kirjoitetaan yksityiskohtainen katsaus tiedostoon: {output_path}")

    with open(output_path, "w", encoding="utf-8") as out:
        out.write("# Yksityiskohtainen Heilahtelevien Atomien Katsaus (RCA Analysis)\n\n")
        out.write(f"Vertailussa kaksi tuoreinta ajoa:\n")
        out.write(f"- **Run 1:** `{run_1_id}`\n")
        out.write(f"- **Run 2:** `{run_2_id}`\n\n")
        out.write(f"Tiedosto sisältää kunkin heilahtelevan atomin raa'at JSON-evaluointitulokset molemmista ajoista vertailua varten.\n\n")
        out.write("## Sisällysluettelo\n")
        for atom in mismatching_atoms:
            out.write(f"- [`{atom}`](#{atom})\n")
        out.write("\n---\n\n")

        for atom in mismatching_atoms:
            rule_desc = atom_rules.get(atom, "Tuntematon sääntö")
            out.write(f"## <a name=\"{atom}\"></a>`{atom}`\n")
            out.write(f"**Arviointisääntö:**\n> {rule_desc}\n\n")

            out.write("### Run 1 ja Run 2 Vertailu\n")
            
            e1 = evals_1.get(atom, {})
            e2 = evals_2.get(atom, {})

            out.write("| Kenttä | Run 1 | Run 2 |\n")
            out.write("| :--- | :--- | :--- |\n")
            out.write(f"| **Tila (mapped_state)** | `{str(e1.get('mapped_state')).upper()}` | `{str(e2.get('mapped_state')).upper()}` |\n")
            out.write(f"| **Lainaus (exact_quote)** | `{e1.get('exact_quote')}` | `{e2.get('exact_quote')}` |\n")
            
            # Poimitaan lisätiedot
            trace1 = e1.get('context_scan_trace') or e1.get('semantic_reasoning') or e1.get('reasoning_trace') or ""
            trace2 = e2.get('context_scan_trace') or e2.get('semantic_reasoning') or e2.get('reasoning_trace') or ""
            
            out.write(f"| **Havaitut poikkeukset / Perustelu** | {e1.get('mitigating_exception_found') or 'Ei poikkeusta'} | {e2.get('mitigating_exception_found') or 'Ei poikkeusta'} |\n")
            
            out.write("\n#### Run 1 Raaka Jälki (Reasoning Trace):\n")
            out.write(f"```text\n{trace1}\n```\n\n")
            
            out.write("#### Run 2 Raaka Jälki (Reasoning Trace):\n")
            out.write(f"```text\n{trace2}\n```\n")
            
            out.write("\n#### Raaka JSON-vertailu:\n")
            out.write("````carousel\n")
            out.write("```json\n")
            out.write(json.dumps(e1, indent=2, ensure_ascii=False))
            out.write("\n```\n")
            out.write("<!-- slide -->\n")
            out.write("```json\n")
            out.write(json.dumps(e2, indent=2, ensure_ascii=False))
            out.write("\n```\n")
            out.write("````\n")
            
            out.write("\n---\n\n")

    print("Valmis! Voit nyt avata tiedoston ja tarkastella eroja graafisesti ja raakadatana.")

if __name__ == "__main__":
    main()

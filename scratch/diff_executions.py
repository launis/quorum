import json
import os

def get_all_evals(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    all_evals = {}
    for step in data:
        if 'content' in step and isinstance(step['content'], dict):
            for e in step['content'].get('evaluations', []):
                all_evals[e['atom_id']] = e
    return all_evals

# Lataa 3 ristiinajon tulokset
evals_1 = get_all_evals('data/files/executions/exe_fd76e010f8e948d0928facb23be6575b/execution_trace.json')
evals_2 = get_all_evals('data/files/executions/exe_a9168cefea7740eba3a096949331ee78/execution_trace.json')
evals_3 = get_all_evals('data/files/executions/exe_e3b7bcb0c44946eb89261816f962cb6f/execution_trace.json')

# Etsi yhteiset atomit
common_atoms = set(evals_1.keys()).intersection(set(evals_2.keys())).intersection(set(evals_3.keys()))

# Etsi säännön kuvaus tietokannasta
with open('backend_v2/seed/seed_data.json', 'r', encoding='utf-8') as f:
    seed = json.load(f)
atom_rules = {}
for block in seed.get('prompt_blocks', []):
    for s_idx, scale in enumerate(block.get('scales', [])):
        for c_idx, claim in enumerate(scale.get('claims', [])):
            for tda in claim.get('tda_assertions', []):
                atom_rules[tda.get('tda_id')] = tda.get('ai_rule_description')

# Tunnista mismatchit (jotka hajosivat kognitiiviseen epämääräisyyteen)
mismatches = []
for atom in common_atoms:
    s1, s2, s3 = evals_1[atom]['mapped_state'], evals_2[atom]['mapped_state'], evals_3[atom]['mapped_state']
    if not (s1 == s2 == s3):
        mismatches.append(atom)

# Tallenna raakadata luettavaan Markdown-muotoon
os.makedirs('scratch', exist_ok=True)
with open('scratch/mismatch_traces_raw.md', 'w', encoding='utf-8') as f:
    f.write('# Raw Mismatch Traces (3-way Execution)\n\n')
    for atom in mismatches:
        f.write(f'## Atom: {atom}\n')
        f.write(f'**Rule:** {atom_rules.get(atom, "Unknown")}\n\n')
        
        f.write(f'**Run 1 (fd7) [{evals_1[atom]["mapped_state"]}]**\n')
        f.write(f'> {evals_1[atom]["reasoning_trace"].replace(chr(10), " ")}\n\n')
        
        f.write(f'**Run 2 (a91) [{evals_2[atom]["mapped_state"]}]**\n')
        f.write(f'> {evals_2[atom]["reasoning_trace"].replace(chr(10), " ")}\n\n')
        
        f.write(f'**Run 3 (e3b) [{evals_3[atom]["mapped_state"]}]**\n')
        f.write(f'> {evals_3[atom]["reasoning_trace"].replace(chr(10), " ")}\n\n')
        
        f.write('---\n\n')

print(f'Done! Dumped {len(mismatches)} mismatch traces.')

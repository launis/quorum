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

# Lataa 2 ristiinajon tulokset
evals_1 = get_all_evals('data/files/executions/exe_ae646cba42ca4e5ca8411bbd841491e5/execution_trace2.json')
evals_2 = get_all_evals('data/files/executions/exe_fab8ea579487462380819afec268e91e/execution_trace1.json')

# Etsi yhteiset atomit
common_atoms = set(evals_1.keys()).intersection(set(evals_2.keys()))

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
summary_stats = {"PASSED->FAILED": 0, "FAILED->PASSED": 0, "Other": 0}
for atom in common_atoms:
    s1, s2 = evals_1[atom]['mapped_state'], evals_2[atom]['mapped_state']
    if s1 != s2:
        mismatches.append(atom)
        s1_str = str(s1).lower()
        s2_str = str(s2).lower()
        
        # Mappaa sekä Pydanticin enumit että mahdolliset bool-arvot
        passed_states = ['true', 'passed', '1']
        failed_states = ['false', 'failed', '0']

        if s1_str in passed_states and s2_str in failed_states:
            summary_stats["PASSED->FAILED"] += 1
        elif s1_str in failed_states and s2_str in passed_states:
            summary_stats["FAILED->PASSED"] += 1
        else:
            summary_stats["Other"] += 1

# Tallenna raakadata luettavaan Markdown-muotoon
os.makedirs('scratch', exist_ok=True)
with open('scratch/mismatch_traces_raw.md', 'w', encoding='utf-8') as f:
    f.write('# Raw Mismatch Traces (2-way Execution)\n\n')
    f.write('## Summary\n')
    f.write(f'- Total common atoms evaluated: {len(common_atoms)}\n')
    f.write(f'- Total mismatching atoms: {len(mismatches)}\n')
    if len(common_atoms) > 0:
        f.write(f'- Variance percentage: {(len(mismatches)/len(common_atoms))*100:.1f} %\n')
    f.write(f'- PASSED -> FAILED (Run 1 -> Run 2): {summary_stats["PASSED->FAILED"]}\n')
    f.write(f'- FAILED -> PASSED (Run 1 -> Run 2): {summary_stats["FAILED->PASSED"]}\n')
    f.write(f'- Other state changes: {summary_stats["Other"]}\n\n')
    
    for atom in mismatches:
        f.write(f'## Atom: {atom}\n')
        f.write(f'**Rule:** {atom_rules.get(atom, "Unknown")}\n\n')
        
        f.write(f'**Run 1 [{evals_1[atom]["mapped_state"]}]**\n')
        f.write(f'> {evals_1[atom].get("reasoning_trace", "").replace(chr(10), " ")}\n\n')
        
        f.write(f'**Run 2 [{evals_2[atom]["mapped_state"]}]**\n')
        f.write(f'> {evals_2[atom].get("reasoning_trace", "").replace(chr(10), " ")}\n\n')
        
        f.write('---\n\n')

print(f'Done! Evaluated {len(common_atoms)} common atoms.')
print(f'Mismatching atoms: {len(mismatches)}')
if len(common_atoms) > 0:
    print(f'Variance: {(len(mismatches)/len(common_atoms))*100:.1f} %')
print(f'PASSED->FAILED: {summary_stats["PASSED->FAILED"]}, FAILED->PASSED: {summary_stats["FAILED->PASSED"]}, Other: {summary_stats["Other"]}')

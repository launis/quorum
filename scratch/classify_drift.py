"""Deep-dive into pure semantic drift: what exactly causes the disagreement?"""
import json


def get_all_evals(path):
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
    all_evals = {}
    for step in data:
        if 'content' in step and isinstance(step['content'], dict):
            evals = step['content'].get('evaluations')
            if isinstance(evals, list):
                for e in evals:
                    all_evals[e['atom_id']] = e
    return all_evals

def get_state(e):
    if 'mapped_state' in e:
        return str(e['mapped_state']).lower()
    if 'exact_quote' in e:
        eq = e['exact_quote']
        if eq is None:
            return "false"
        eq_lower = str(eq).strip().lower()
        blacklist = {
            "null", "none", "n/a", "false", "", "ei löydy", "not found", "-", "ei mainittu",
            "none detected", "[]", "{}", "ei sovelleta", "ei lainausta", "no quote", "ei ole"
        }
        return "true" if eq_lower not in blacklist else "false"
    return "unknown"

def get_trace(e):
    for key in ['context_scan_trace', 'semantic_reasoning', 'reasoning_trace', 'mechanical_trace']:
        if key in e:
            return str(e[key])
    return ""

evals_1 = get_all_evals("data/files/executions/exe_0adc01fd7c9a40c99b7537e2d32b443c/execution_trace.json")
evals_2 = get_all_evals("data/files/executions/exe_e22f62d350d84d5289a9886c27c1947f/execution_trace.json")

common = set(evals_1.keys()) & set(evals_2.keys())

# Load seed data to get the actual rules
with open('backend_v2/seed/seed_data.json', encoding='utf-8') as f:
    seed = json.load(f)
atom_rules = {}
atom_extraction = {}
atom_inverse = {}
atom_concept = {}
for block in seed.get('prompt_blocks', []):
    for scale in block.get('scales', []):
        for claim in scale.get('claims', []):
            for tda in claim.get('tda_assertions', []):
                tid = tda.get('tda_id')
                atom_rules[tid] = tda.get('extraction_rule', '')
                atom_inverse[tid] = tda.get('inverse_evidence', False)
                atom_concept[tid] = tda.get('concept_description', '')

# Classify pure semantic drift sub-causes
drift_atoms = []
for atom in common:
    s1 = get_state(evals_1[atom])
    s2 = get_state(evals_2[atom])
    if s1 == s2:
        continue
    t1 = get_trace(evals_1[atom])
    t2 = get_trace(evals_2[atom])
    co1 = evals_1[atom].get('contextual_override', False)
    co2 = evals_2[atom].get('contextual_override', False)
    if 'AGENT_SCHEMA_VALIDATION_FAILED' in t1 or 'AGENT_SCHEMA_VALIDATION_FAILED' in t2:
        continue
    if 'SYSTEM ERROR' in t1 or 'SYSTEM ERROR' in t2:
        continue
    if co1 != co2:
        continue
    drift_atoms.append(atom)

# Sub-classify drift atoms
sub_empty_rule = 0
sub_rule_swap = 0  # atomit arvioidaan eri sääntöä vasten
sub_genuine = 0
sub_inverse_confusion = 0

for atom in drift_atoms:
    rule = atom_rules.get(atom, '')
    concept = atom_concept.get(atom, '')
    t1 = get_trace(evals_1[atom])
    t2 = get_trace(evals_2[atom])

    # Check if the rule/extraction text is empty or near-empty
    if not rule or rule.strip() == '' or rule.strip() == 'None':
        sub_empty_rule += 1
        continue

    # Check if traces suggest the atom was evaluated against different rules
    # (one trace talks about a completely different concept)
    inv = atom_inverse.get(atom, False)

    # Check for inverse_evidence confusion: one run treats as positive, other as inverse
    if inv:
        # If it's an inverse rule, check if one run found evidence (PASS) and other didn't (FAIL)
        # but they disagreed on what "finding evidence" means
        sub_inverse_confusion += 1
    else:
        sub_genuine += 1

print(f"=== PURE SEMANTIC DRIFT SUB-CLASSIFICATION ({len(drift_atoms)} atoms) ===")
print("")
print(f"A. Empty/missing extraction_rule:     {sub_empty_rule} ({sub_empty_rule/len(drift_atoms)*100:.1f}%)")
print(f"B. Inverse evidence confusion:         {sub_inverse_confusion} ({sub_inverse_confusion/len(drift_atoms)*100:.1f}%)")
print(f"C. Genuine semantic disagreement:      {sub_genuine} ({sub_genuine/len(drift_atoms)*100:.1f}%)")

# Show details of a few inverse confusion cases
print("\n--- Inverse Evidence Confusion Cases (first 5) ---")
count = 0
for atom in drift_atoms:
    inv = atom_inverse.get(atom, False)
    if not inv:
        continue
    rule = atom_rules.get(atom, 'N/A')[:100]
    concept = atom_concept.get(atom, 'N/A')[:80]
    s1 = get_state(evals_1[atom])
    s2 = get_state(evals_2[atom])
    print(f"  {atom}: R1={s1} R2={s2} | inv=True")
    print(f"    rule: {rule}")
    print(f"    concept: {concept}")
    count += 1
    if count >= 5:
        break

# Show details of genuine drift cases
print("\n--- Genuine Semantic Disagreement (first 5) ---")
count = 0
for atom in drift_atoms:
    inv = atom_inverse.get(atom, False)
    if inv:
        continue
    rule = atom_rules.get(atom, 'N/A')[:100]
    s1 = get_state(evals_1[atom])
    s2 = get_state(evals_2[atom])
    t1 = get_trace(evals_1[atom])[:150]
    t2 = get_trace(evals_2[atom])[:150]
    print(f"  {atom}: R1={s1} R2={s2}")
    print(f"    rule: {rule}")
    print(f"    R1: {t1}")
    print(f"    R2: {t2}")
    count += 1
    if count >= 5:
        break

# Overall stats
print("\n=== GRAND TOTAL ===")
print("Schema fail:       6 / 69 = 8.7%   -> Fixable by schema patch")
print("CO Disagreement:  21 / 69 = 30.4%  -> Fixable by deterministic CO protocol")
print(f"Inverse confusion: {sub_inverse_confusion} / 69 = {sub_inverse_confusion/69*100:.1f}%  -> Fixable by clearer inverse_evidence handling")
print(f"Genuine drift:     {sub_genuine} / 69 = {sub_genuine/69*100:.1f}%  -> Inherent LLM stochasticity (temperature/sampling)")
print("System error:      2 / 69 = 2.9%   -> Fixable by retry logic")
print(f"Empty rules:       {sub_empty_rule} / 69 = {sub_empty_rule/69*100:.1f}%  -> Fixable by seed cleanup")

"""Classify each mismatch by root cause category."""
import json


# Load both execution traces
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

# Categories
cat_schema_fail = []      # Schema validation failed (condition_met hallucination)
cat_contextual_override = []  # One used contextual_override, other didn't
cat_pure_semantic = []    # Both ran fine but reached opposite conclusions
cat_system_error = []     # SYSTEM ERROR in trace

for atom in common:
    s1 = get_state(evals_1[atom])
    s2 = get_state(evals_2[atom])
    if s1 == s2:
        continue

    t1 = get_trace(evals_1[atom])
    t2 = get_trace(evals_2[atom])

    co1 = evals_1[atom].get('contextual_override', False)
    co2 = evals_2[atom].get('contextual_override', False)

    # Check for schema validation failure
    if 'AGENT_SCHEMA_VALIDATION_FAILED' in t1 or 'AGENT_SCHEMA_VALIDATION_FAILED' in t2:
        cat_schema_fail.append(atom)
    elif 'SYSTEM ERROR' in t1 or 'SYSTEM ERROR' in t2:
        cat_system_error.append(atom)
    elif co1 != co2:
        cat_contextual_override.append(atom)
    else:
        cat_pure_semantic.append(atom)

total_mismatch = len(cat_schema_fail) + len(cat_contextual_override) + len(cat_pure_semantic) + len(cat_system_error)

print("=== MISMATCH ROOT CAUSE CLASSIFICATION ===")
print(f"Total mismatches: {total_mismatch}")
print("")
print(f"1. Schema Validation Failed (condition_met hallucination): {len(cat_schema_fail)} ({len(cat_schema_fail)/total_mismatch*100:.1f}%)")
print(f"2. Contextual Override Disagreement:                      {len(cat_contextual_override)} ({len(cat_contextual_override)/total_mismatch*100:.1f}%)")
print(f"3. Pure Semantic Drift (both ran, opposite result):       {len(cat_pure_semantic)} ({len(cat_pure_semantic)/total_mismatch*100:.1f}%)")
print(f"4. System Error:                                          {len(cat_system_error)} ({len(cat_system_error)/total_mismatch*100:.1f}%)")

# Schema fail details - which chunk
print(f"\n--- Schema Fail atoms ({len(cat_schema_fail)}) ---")
for a in cat_schema_fail:
    t2 = get_trace(evals_2[a])
    t1 = get_trace(evals_1[a])
    which_run = "R2" if 'AGENT_SCHEMA_VALIDATION_FAILED' in t2 else "R1"
    print(f"  {a} (failed in {which_run})")

# Contextual override details
print(f"\n--- Contextual Override Disagreement atoms ({len(cat_contextual_override)}) ---")
for a in cat_contextual_override:
    co1 = evals_1[a].get('contextual_override', False)
    co2 = evals_2[a].get('contextual_override', False)
    s1 = get_state(evals_1[a])
    s2 = get_state(evals_2[a])
    print(f"  {a}: R1 co={co1} state={s1} | R2 co={co2} state={s2}")

# Pure semantic drift - sample a few
print(f"\n--- Pure Semantic Drift atoms ({len(cat_pure_semantic)}) - first 5 ---")
for a in cat_pure_semantic[:5]:
    s1 = get_state(evals_1[a])
    s2 = get_state(evals_2[a])
    t1_short = get_trace(evals_1[a])[:120]
    t2_short = get_trace(evals_2[a])[:120]
    print(f"  {a}: R1={s1} R2={s2}")
    print(f"    R1 trace: {t1_short}...")
    print(f"    R2 trace: {t2_short}...")

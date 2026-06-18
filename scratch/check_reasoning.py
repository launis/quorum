import json

with open('c:/src/quorum/data/files/executions/exe_88bd56bdc0b64e0a8b447c31ab000802/execution_trace.json', encoding='utf-8') as f:
    r1 = json.load(f)

with open('c:/src/quorum/data/files/executions/exe_b7eb5587e06a4cfca71e90605eba9d23/execution_trace.json', encoding='utf-8') as f:
    r2 = json.load(f)

e1 = [e for trace in r1 for e in trace.get('content', {}).get('evaluations', [])]
e2 = [e for trace in r2 for e in trace.get('content', {}).get('evaluations', [])]

d1 = {e['atom_id']: e for e in e1}
d2 = {e['atom_id']: e for e in e2}

same_reasoning = 0
total = 0

for k in set(d1.keys()) & set(d2.keys()):
    total += 1
    s1 = d1[k].get('semantic_reasoning', '').replace('\n\n[5. VALIDATION DECISION: PASS]', '').replace('\n\n[5. VALIDATION DECISION: FAIL]', '')
    s2 = d2[k].get('semantic_reasoning', '').replace('\n\n[5. VALIDATION DECISION: PASS]', '').replace('\n\n[5. VALIDATION DECISION: FAIL]', '')
    if s1 == s2:
        same_reasoning += 1

print(f"Total common atoms: {total}")
print(f"Atoms with IDENTICAL reasoning text: {same_reasoning}")
print(f"Percentage: {same_reasoning/total*100:.2f}%")

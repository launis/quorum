import json

trace_path = r'c:\src\quorum\data\files\executions\exe_add8965fdc7342c5950678fd9745dfb6\execution_trace.json'
with open(trace_path, 'r', encoding='utf-8') as f:
    trace = json.load(f)

p1_schema_purity = 0
p4_rule_anchor = 0
p3_inverse = 0
p0_do_not_evaluate = 0
p4_flattened_atom = 0
empty_extraction_rules = 0

total_atoms = 0

for e in trace:
    event_type = e.get('event_type')
    content = e.get('content')
    if event_type == 'LLM_PROMPT':
        if isinstance(content, list):
            for msg in content:
                text = msg.get('content', '')
                if 'SCHEMA_PURITY_MANDATE' in text:
                    p1_schema_purity += 1
                if 'rule_anchor' in text:
                    p4_rule_anchor += 1
                if 'inverse_evidence' in text or 'käänteislogiikka' in text.lower():
                    p3_inverse += 1
                if 'Do not evaluate' in text:
                    p0_do_not_evaluate += 1
                if 'FlattenedAtom' in text:
                    p4_flattened_atom += 1

    if event_type == 'LLM_RESPONSE_PARSED':
        # Let's count how many atoms were evaluated
        # The content might be a dict containing "evaluations"
        if isinstance(content, dict):
            evals = content.get('evaluations', [])
            total_atoms += len(evals)

print(f"P1 (SCHEMA_PURITY_MANDATE tags found): {p1_schema_purity}")
print(f"P4 (rule_anchor tags found): {p4_rule_anchor}")
print(f"P3 (Inverse logic found in prompt - SHOULD BE 0): {p3_inverse}")
print(f"P0 ('Do not evaluate' found in prompt - SHOULD BE 0): {p0_do_not_evaluate}")
print(f"P4 (FlattenedAtom explicit struct found): {p4_flattened_atom}")
print(f"Total atoms extracted: {total_atoms}")

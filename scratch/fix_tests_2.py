import re

path = r'c:\src\quorum\backend_v2\tests\unit\models\dtos\test_lightweight_matrix.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

def add_internal_logic(match):
    full_match = match.group(0)
    # Check if internal_logic_en is in this block. But wait, regex match is just the line.
    if "internal_logic_en" in full_match:
        return full_match
    # We match "AtomEvaluationItemDTO(" up to the first parenthesis, and add the arg
    return full_match + '\n        internal_logic_en=ReasoningStepDTO(step_1_identify_premise="stub", step_2_scan_source="stub", step_3_evaluate_anti_patterns="stub", step_4_final_conclusion="stub"),'

# We look for AtomEvaluationItemDTO( and the next line to see if it has atom_id
# Wait, just matching `AtomEvaluationItemDTO\(` and replacing it with `AtomEvaluationItemDTO(\n    internal_logic_en=...` is easier, but some are on the same line?
content = re.sub(r'AtomEvaluationItemDTO\(\s*atom_id="[^"]+",', add_internal_logic, content)
content = re.sub(r'AtomEvaluationItemDTO\(\s*atom_id=tda\.tda_id,', add_internal_logic, content)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Added missing internal_logic_en")

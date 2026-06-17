import re

path = r'c:\src\quorum\backend_v2\tests\unit\models\dtos\test_lightweight_matrix.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Make sure ReasoningStepDTO is imported
if "from backend_v2.models.dtos.lightweight_matrix import ReasoningStepDTO" not in content:
    content = "from backend_v2.models.dtos.lightweight_matrix import ReasoningStepDTO\n" + content

# Replace old dictionary `internal_logic_en` with the ReasoningStepDTO
old_logic_pattern = re.compile(
    r'internal_logic_en=\{[^\}]+\},', re.DOTALL
)
new_logic = 'internal_logic_en=ReasoningStepDTO(step_1_identify_premise="stub", step_2_scan_source="stub", step_3_evaluate_anti_patterns="stub", step_4_final_conclusion="stub"),'

content = old_logic_pattern.sub(new_logic, content)

# Fix exact_quote= to exact_quotes=
content = content.replace(
    'exact_quote=exact_quote,',
    'exact_quotes=[exact_quote] if exact_quote != "None" else [],'
)
content = re.sub(r'exact_quote=("[^"]+"),', r'exact_quotes=[\1],', content)
content = content.replace('item.exact_quote == "This is an exact quote"', 'item.exact_quotes == ["This is an exact quote"]')
content = content.replace('validated.exact_quote == "Megatrendien kooste osoittaa kriisejä"', 'validated.exact_quotes == ["Megatrendien kooste osoittaa kriisejä"]')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("test_lightweight_matrix perfectly fixed!")
